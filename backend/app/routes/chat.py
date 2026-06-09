from collections import Counter
from datetime import datetime, timedelta, timezone
import os

from fastapi import APIRouter, Depends, HTTPException, Query, status
from openai import OpenAI

from app.db import messages_collection
from app.dependencies import get_current_user
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.emotion_service import detect_emotion
from app.services.privacy_service import redact_pii
from app.services.rate_limit_service import is_rate_limited
from app.services.recommendation_service import get_recommendations
from app.services.safety_responses import get_safety_response
from app.services.safety_service import classify_safety

router = APIRouter(prefix="/chat", tags=["chat"])

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


HIGH_RISK_LEVELS = {"high", "crisis"}


def normalize_datetime(dt: datetime | None) -> datetime | None:
    if not dt:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def get_recent_context(user_id: str, limit: int = 8) -> str:
    """
    Recupera contexto conversacional para mejorar continuidad.

    Por seguridad, los mensajes previos clasificados como high/crisis no se envían literalmente
    al modelo generativo. Esto evita que la IA use como contexto ideas delirantes, autolesivas
    o violentas y reduce el riesgo de reforzarlas.
    """
    history = list(
        messages_collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
    )
    history.reverse()

    context_lines: list[str] = []
    for item in history:
        risk_level = item.get("risk_level", "low")
        if risk_level in HIGH_RISK_LEVELS:
            context_lines.append("Usuario: [Mensaje anterior omitido por seguridad: evento de alto riesgo]")
            context_lines.append("Asistente: [Respuesta de seguridad emitida]")
            continue

        user_msg = item.get("user_message", "")
        assistant_msg = item.get("assistant_message", "")
        context_lines.append(f"Usuario: {user_msg}")
        context_lines.append(f"Asistente: {assistant_msg}")

    return "\n".join(context_lines)


def build_profile_memory(user_id: str) -> str:
    lookback_days = 14
    since = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    messages = list(
        messages_collection.find({"user_id": user_id, "created_at": {"$gte": since}})
        .sort("created_at", -1)
        .limit(50)
    )

    if not messages:
        return "Sin historial emocional relevante todavía."

    emotions = [item.get("emotion", "neutral") for item in messages]
    counts = Counter(emotions)
    top_three = counts.most_common(3)
    predominant = ", ".join([f"{emotion} ({count})" for emotion, count in top_three])
    recent = emotions[:5]
    recent_text = ", ".join(recent)

    return (
        f"Ventana de {lookback_days} días. Emociones predominantes: {predominant}. "
        f"Últimas emociones registradas: {recent_text}."
    )


def generate_ai_response(
    user_message: str,
    emotion: str,
    context: str,
    profile_memory: str,
    safety_mode: bool = False,
) -> str:
    system_prompt = """
Eres un asistente de apoyo emocional basado en inteligencia artificial.

Debes responder de forma:
- empática
- natural
- clara
- calmada
- no repetitiva

Normas obligatorias:
- No diagnostiques trastornos ni enfermedades.
- No sustituyas ayuda profesional.
- No indiques medicación ni cambios de tratamiento.
- No añadas una nota o disclaimer fijo al final de cada respuesta.
- No repitas siempre la misma estructura.
- Adapta la respuesta al mensaje actual y al contexto previo.
- Usa el perfil emocional para ajustar tono y sugerencias sin etiquetar ni juzgar al usuario.
- Sé útil y humano, pero sin sonar excesivamente teatral.
"""

    if safety_mode:
        system_prompt += """

Modo de seguridad reforzado:
- El usuario muestra malestar emocional relevante, aunque no se ha detectado crisis inmediata.
- No minimices el malestar ni respondas con optimismo vacío.
- Recomienda apoyo de una persona de confianza o profesional si el malestar aumenta.
- Si el usuario menciona autolesión, suicidio, daño a terceros, delirios, voces o peligro físico, indica buscar ayuda urgente y emergencias.
- No hagas preguntas que puedan incentivar detalles sobre métodos de daño.
"""

    user_prompt = f"""
Emoción detectada del usuario: {emotion}

Contexto reciente de la conversación:
{context if context else "No hay contexto previo."}

Memoria de perfil emocional:
{profile_memory}

Mensaje actual del usuario:
"{user_message}"

Genera una respuesta breve o media, coherente con el contexto, empática y personalizada.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.6 if safety_mode else 0.8,
        max_tokens=300,
    )

    return response.choices[0].message.content or "Estoy aquí para escucharte."


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest, current_user=Depends(get_current_user)):
    user_id = current_user["sub"]

    if is_rate_limited(user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Has enviado demasiados mensajes en poco tiempo. Espera un minuto e inténtalo de nuevo.",
        )

    # 1) La seguridad se evalúa antes de llamar al modelo generativo.
    safety_result = classify_safety(request.message)
    crisis_resources = ["112", "024"] if safety_result.risk_level in HIGH_RISK_LEVELS else []
    ai_called = False

    # 2) Si el mensaje es high/crisis, NO se llama a OpenAI.
    if not safety_result.ai_allowed:
        emotion = "crisis" if safety_result.risk_level == "crisis" else "alto_riesgo"
        recommendations: list[str] = []
        ai_response = get_safety_response(
            safety_result.risk_type,
            safety_result.matched_patterns,
        )
        redaction_applied = False
        detected_types: list[str] = []

    else:
        context = get_recent_context(user_id)
        redacted_message, message_was_redacted, message_detected_types = redact_pii(request.message)
        redacted_context, context_was_redacted, context_detected_types = redact_pii(context)
        detected_types = sorted(set(message_detected_types + context_detected_types))
        redaction_applied = message_was_redacted or context_was_redacted

        emotion = detect_emotion(request.message)
        recommendations = get_recommendations(emotion)
        profile_memory = build_profile_memory(user_id)

        try:
            ai_response = generate_ai_response(
                redacted_message,
                emotion,
                redacted_context,
                profile_memory,
                safety_mode=safety_result.risk_level == "medium",
            )
            ai_called = True
        except Exception:
            ai_response = (
                "Estoy aquí para escucharte. Gracias por compartir cómo te sientes. "
                "Si quieres, puedes contarme un poco más para intentar orientarte mejor."
            )

    created_at = datetime.now(timezone.utc)

    message_data = {
        "user_id": user_id,
        "user_message": request.message,
        "assistant_message": ai_response,
        "emotion": emotion,
        "recommendations": recommendations,
        "redaction_applied": redaction_applied,
        "detected_sensitive_types": detected_types,
        "risk_level": safety_result.risk_level,
        "risk_type": safety_result.risk_type,
        "safety_triggered": safety_result.safety_triggered,
        "ai_called": ai_called,
        "safety_reason": safety_result.reason,
        "matched_patterns": safety_result.matched_patterns,
        "created_at": created_at,
    }

    messages_collection.insert_one(message_data)

    return {
        "user_message": request.message,
        "assistant_message": ai_response,
        "emotion": emotion,
        "recommendations": recommendations,
        "crisis_detected": safety_result.risk_level == "crisis",
        "crisis_resources": crisis_resources,
        "redaction_applied": redaction_applied,
        "detected_sensitive_types": detected_types,
        "created_at": created_at.isoformat(),
        "risk_level": safety_result.risk_level,
        "risk_type": safety_result.risk_type,
        "safety_triggered": safety_result.safety_triggered,
        "ai_called": ai_called,
    }


@router.get("/history")
def get_chat_history(limit: int = Query(20), current_user=Depends(get_current_user)):
    messages = list(
        messages_collection.find({"user_id": current_user["sub"]})
        .sort("created_at", -1)
        .limit(limit)
    )

    for msg in messages:
        msg["_id"] = str(msg["_id"])
        created = normalize_datetime(msg.get("created_at"))
        if created:
            msg["created_at"] = created.isoformat()

    messages.reverse()
    return messages


@router.get("/summary")
def get_user_summary(current_user=Depends(get_current_user)):
    messages = list(
        messages_collection.find({"user_id": current_user["sub"]}).sort("created_at", -1)
    )

    emotion_counts = {
        "ansiedad": 0,
        "estres": 0,
        "tristeza": 0,
        "neutral": 0,
        "positivo": 0,
        "crisis": 0,
        "alto_riesgo": 0,
    }

    recent_messages = []
    weekly_counts = {}

    now = datetime.now(timezone.utc)
    week_start = now - timedelta(days=7)

    for msg in messages:
        emotion = msg.get("emotion", "neutral")

        if emotion in emotion_counts:
            emotion_counts[emotion] += 1
        else:
            emotion_counts["neutral"] += 1

        created = normalize_datetime(msg.get("created_at"))

        if created and created >= week_start:
            key = created.date().isoformat()
            weekly_counts[key] = weekly_counts.get(key, 0) + 1

        recent_messages.append(
            {
                "user_message": msg.get("user_message", ""),
                "assistant_message": msg.get("assistant_message", ""),
                "emotion": emotion,
                "risk_level": msg.get("risk_level", "low"),
                "risk_type": msg.get("risk_type", "normal"),
                "safety_triggered": msg.get("safety_triggered", False),
                "ai_called": msg.get("ai_called", True),
                "created_at": created.isoformat() if created else None,
            }
        )

    emotion_timeline = [
        {"emotion": msg["emotion"], "created_at": msg["created_at"]}
        for msg in reversed(recent_messages[:20])
        if msg["created_at"]
    ]

    predominant_recent = [msg["emotion"] for msg in recent_messages[:5]]

    return {
        "user": {
            "id": current_user["sub"],
            "name": current_user["name"],
            "email": current_user["email"],
        },
        "total_messages": len(messages),
        "emotion_counts": emotion_counts,
        "predominant_recent": predominant_recent,
        "weekly_frequency": weekly_counts,
        "emotion_timeline": emotion_timeline,
        "recent_messages": recent_messages[:5],
    }
