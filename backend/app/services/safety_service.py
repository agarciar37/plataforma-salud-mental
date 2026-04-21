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
    "ES": [
        "Emergencias: 112",
        "Línea 024 (atención a la conducta suicida, España)",
    ],
    "US": [
        "Emergencias: 911",
        "988 Suicide & Crisis Lifeline",
    ],
}


def is_high_risk_message(message: str) -> bool:
    normalized = message.lower()
    return any(keyword in normalized for keyword in HIGH_RISK_KEYWORDS)


def get_crisis_resources(country_code: str = "ES") -> list[str]:
    normalized = country_code.upper()
    return CRISIS_RESOURCES_BY_COUNTRY.get(normalized, [
        "Emergencias: 112/911 según tu país",
        "Línea de ayuda en crisis de tu zona",
    ])


def crisis_support_message(country_code: str = "ES") -> str:
    resources = get_crisis_resources(country_code)
    return (
        "Siento mucho que estés pasando por esto. Tu seguridad es lo más importante ahora mismo. "
        "Si crees que puedes hacerte daño o estás en peligro, pide ayuda inmediata y no te quedes solo/a. "
        f"Recursos sugeridos: {resources[0]}; {resources[1]}."
    )


def append_non_diagnostic_disclaimer(message: str) -> str:
    if NON_DIAGNOSTIC_DISCLAIMER.strip() in message:
        return message
    return f"{message}{NON_DIAGNOSTIC_DISCLAIMER}"