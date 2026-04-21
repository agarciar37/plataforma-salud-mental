from fastapi import APIRouter, Depends, Query
from datetime import datetime, timezone
from app.db import messages_collection
from app.dependencies import get_current_user
from app.schemas.chat import ChatRequest
from app.services.recommendation_service import get_recommendations
from openai import OpenAI
import os

router = APIRouter(prefix="/chat", tags=["chat"])

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def detect_emotion(message: str) -> str:
    message = message.lower()

    if any(word in message for word in ["triste", "mal", "deprimido", "vacío", "solo", "desanimado"]):
        return "tristeza"
    if any(word in message for word in ["ansioso", "nervioso", "estres", "agobiado", "preocupado", "saturado"]):
        return "ansiedad"
    if any(word in message for word in ["feliz", "bien", "contento", "motivado", "tranquilo", "alegre"]):
        return "felicidad"

    return "neutral"


def get_recent_context(user_id: str, limit: int = 5) -> str:
    history = list(
        messages_collection
        .find({"user_id": user_id})
        .sort("created_at", -1)
        .limit(limit)
    )

    history.reverse()

    context_lines = []
    for item in history:
        user_msg = item.get("user_message", "")
        assistant_msg = item.get("assistant_message", "")
        context_lines.append(f"Usuario: {user_msg}")
        context_lines.append(f"Asistente: {assistant_msg}")

    return "\n".join(context_lines)


def generate_ai_response(user_message: str, emotion: str, context: str) -> str:
    system_prompt = """
Eres un asistente de apoyo emocional basado en inteligencia artificial.

Debes responder de forma:
- empática
- natural
- clara
- calmada
- no repetitiva

Normas:
- No diagnostiques trastornos ni enfermedades.
- No sustituyas ayuda profesional.
- No repitas siempre la misma estructura.
- Adapta la respuesta al mensaje actual y al contexto previo.
- Responde en español.
- Sé útil y humano, pero sin sonar excesivamente teatral.
"""

    user_prompt = f"""
Emoción detectada del usuario: {emotion}

Contexto reciente de la conversación:
{context if context else "No hay contexto previo."}

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
        temperature=0.8,
        max_tokens=300,
    )

    return response.choices[0].message.content or "Estoy aquí para escucharte."


@router.post("/message")
async def send_message(
    request: ChatRequest,
    current_user=Depends(get_current_user)
):
    user_id = current_user["sub"]
    emotion = detect_emotion(request.message)
    recommendations = get_recommendations(emotion)
    context = get_recent_context(user_id)

    try:
        ai_response = generate_ai_response(request.message, emotion, context)
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
        "created_at": created_at,
    }

    messages_collection.insert_one(message_data)

    return {
        "user_message": request.message,
        "assistant_message": ai_response,
        "emotion": emotion,
        "recommendations": recommendations,
        "created_at": created_at.isoformat(),
    }


@router.get("/history")
def get_chat_history(
    limit: int = Query(20),
    current_user=Depends(get_current_user)
):
    messages = list(
        messages_collection
        .find({"user_id": current_user["sub"]})
        .sort("created_at", -1)
        .limit(limit)
    )

    for msg in messages:
        msg["_id"] = str(msg["_id"])
        if msg.get("created_at"):
            msg["created_at"] = msg["created_at"].isoformat()

    messages.reverse()
    return messages


@router.get("/summary")
def get_user_summary(current_user=Depends(get_current_user)):
    messages = list(
        messages_collection
        .find({"user_id": current_user["sub"]})
        .sort("created_at", -1)
    )

    emotion_counts = {
        "ansiedad": 0,
        "tristeza": 0,
        "felicidad": 0,
        "neutral": 0,
    }

    recent_messages = []

    for msg in messages:
        emotion = msg.get("emotion", "neutral")

        if emotion in emotion_counts:
            emotion_counts[emotion] += 1
        else:
            emotion_counts["neutral"] += 1

        recent_messages.append({
            "user_message": msg.get("user_message", ""),
            "assistant_message": msg.get("assistant_message", ""),
            "emotion": emotion,
            "created_at": msg.get("created_at").isoformat() if msg.get("created_at") else None,
        })

    return {
        "user": {
            "id": current_user["sub"],
            "name": current_user["name"],
            "email": current_user["email"],
        },
        "total_messages": len(messages),
        "emotion_counts": emotion_counts,
        "recent_messages": recent_messages[:5],
    }