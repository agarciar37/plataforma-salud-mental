HIGH_RISK_KEYWORDS = [
    "suicidio",
    "suicidarme",
    "quitarme la vida",
    "no quiero vivir",
    "hacerme daño",
    "autolesión",
    "autolesion",
    "me quiero morir",
]

NON_DIAGNOSTIC_DISCLAIMER = (
    "\n\nNota importante: soy un asistente de apoyo emocional, no realizo diagnósticos "
    "ni sustituyo a un profesional de salud mental."
)


def is_high_risk_message(message: str) -> bool:
    normalized = message.lower()
    return any(keyword in normalized for keyword in HIGH_RISK_KEYWORDS)


def crisis_support_message() -> str:
    return (
        "Siento mucho que estés pasando por esto. Tu seguridad es lo más importante ahora mismo. "
        "Si crees que puedes hacerte daño o estás en peligro, contacta de inmediato con emergencias "
        "(112/911 según tu país) o con una línea de ayuda en crisis de tu zona. "
        "Si puedes, avisa también a una persona de confianza para que no estés solo/a."
    )


def append_non_diagnostic_disclaimer(message: str) -> str:
    if NON_DIAGNOSTIC_DISCLAIMER.strip() in message:
        return message
    return f"{message}{NON_DIAGNOSTIC_DISCLAIMER}"