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

CRISIS_RESOURCES_BY_COUNTRY = {
    "ES": {
        "emergency": "Emergencias: 112",
        "hotline": "Línea 024 (atención a la conducta suicida, España)",
        "active_help": "Pide a alguien de confianza que te acompañe presencialmente ahora.",
    },
    "US": {
        "emergency": "Emergencias: 911",
        "hotline": "988 Suicide & Crisis Lifeline (call/text/chat)",
        "active_help": "Contacta una persona de confianza y mantente acompañado/a mientras buscas ayuda.",
    },
}


def is_high_risk_message(message: str) -> bool:
    normalized = message.lower()
    return any(keyword in normalized for keyword in HIGH_RISK_KEYWORDS)


def get_crisis_resources(country_code: str = "ES") -> list[str]:
    normalized = country_code.upper()
    resource = CRISIS_RESOURCES_BY_COUNTRY.get(normalized)

    if resource:
        return [resource["emergency"], resource["hotline"], resource["active_help"]]

    return [
        "Emergencias: 112/911 según tu país",
        "Línea de ayuda en crisis de tu zona",
        "Busca apoyo inmediato de una persona de confianza.",
    ]


def crisis_support_message(country_code: str = "ES") -> str:
    emergency, hotline, active_help = get_crisis_resources(country_code)
    return (
        "🚨 CRISIS DETECTADA\n"
        "1) Si hay riesgo inmediato, llama ahora mismo a emergencias.\n"
        f"2) {emergency}.\n"
        f"3) {hotline}.\n"
        f"4) {active_help}"
    )


def append_non_diagnostic_disclaimer(message: str) -> str:
    if NON_DIAGNOSTIC_DISCLAIMER.strip() in message:
        return message
    return f"{message}{NON_DIAGNOSTIC_DISCLAIMER}"