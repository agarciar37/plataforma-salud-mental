from app.services.safety_service import SafetyResult


SAFETY_CLASSIFIER_PROMPT = (
    "Eres un clasificador de seguridad para una aplicación de apoyo emocional. "
    "Tu tarea es clasificar el riesgo del mensaje del usuario, no responderle. "
    "Devuelve únicamente JSON válido con risk_level, risk_type, reason, ai_allowed. "
    "Si hay duda razonable, elige el nivel de riesgo más alto. "
    "No minimices frases ambiguas que puedan implicar daño físico."
)


def classify_with_llm(message: str) -> SafetyResult | None:
    # Capa preparada para uso futuro (USE_LLM_SAFETY_CLASSIFIER=false por defecto).
    # Debe retornar SafetyResult cuando se implemente la llamada al modelo.
    _ = message
    return None