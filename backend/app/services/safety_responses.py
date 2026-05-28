from app.services.safety_service import RiskType


CRISIS_SELF_HARM_RESPONSE = (
    "Me preocupa mucho lo que estás compartiendo y tu seguridad es la prioridad ahora mismo. "
    "Por favor, aléjate de cualquier cosa con la que puedas hacerte daño y busca un lugar seguro.\n\n"
    "Si estás en España, llama al 112 ahora mismo o al 024 (Línea de atención a la conducta suicida). "
    "También te puede ayudar contactar de inmediato con una persona de confianza que pueda acompañarte.\n\n"
    "No estás solo/a en esto. Lo más importante ahora es mantenerte a salvo."
)

DANGEROUS_BEHAVIOR_RESPONSE = (
    "Me preocupa mucho lo que acabas de decir, porque esa acción puede ponerte en peligro inmediato. "
    "Por favor, aléjate ahora mismo del lugar u objeto peligroso y busca un lugar seguro.\n\n"
    "Si estás en España, llama al 112 o contacta inmediatamente con una persona de confianza que pueda acompañarte. "
    "También puedes llamar al 024, la línea de atención a la conducta suicida.\n\n"
    "No tienes que afrontar esto solo/a. Lo más importante ahora es tu seguridad inmediata."
)

HARM_TO_OTHERS_RESPONSE = (
    "Gracias por decirlo. Es importante que no actúes impulsivamente ni te acerques a esa situación ahora. "
    "Aléjate del lugar o de la persona implicada y busca apoyo inmediato.\n\n"
    "Contacta con una persona de confianza o con emergencias (112 en España) si sientes que podrías perder el control. "
    "Tu seguridad y la de los demás es lo más importante ahora."
)

DELUSION_PARANOIA_RESPONSE = (
    "Siento que estés viviendo esto con tanta angustia. No puedo confirmar que eso esté ocurriendo, "
    "pero sí me preocupa cómo te está afectando.\n\n"
    "Sería importante que ahora hables con una persona de confianza o con un profesional de salud mental. "
    "Si sientes riesgo de hacerte daño o hacer daño a alguien, llama al 112."
)

PSYCHOTIC_SYMPTOMS_RESPONSE = (
    "Gracias por contarlo. Lo que describes puede ser muy angustiante y es importante que tengas apoyo ahora. "
    "Busca una persona de confianza y contacta con un profesional de salud mental cuanto antes.\n\n"
    "Si sientes peligro inmediato o impulso de hacerte daño o dañar a alguien, llama al 112 de inmediato."
)

MEDICAL_ADVICE_RESPONSE = (
    "No puedo diagnosticar ni indicar medicación. Para tu seguridad, no modifiques ni suspendas tratamiento "
    "sin supervisión profesional.\n\n"
    "Te recomiendo consultar con tu médico o profesional de salud mental para una pauta segura. "
    "Si notas riesgo inmediato, llama al 112."
)

EMOTIONAL_DISTRESS_RESPONSE = (
    "Siento que estés pasando por un momento tan intenso. Gracias por expresarlo.\n\n"
    "Si te ayuda, prueba a respirar lento unos minutos, escribir lo que sientes y contactar con alguien de confianza. "
    "Si notas que el riesgo aumenta o te sientes en peligro, llama al 112 o al 024 en España."
)


def get_safety_response(risk_type: RiskType) -> str:
    mapping = {
        "self_harm": CRISIS_SELF_HARM_RESPONSE,
        "dangerous_behavior": DANGEROUS_BEHAVIOR_RESPONSE,
        "substance_or_overdose": DANGEROUS_BEHAVIOR_RESPONSE,
        "harm_to_others": HARM_TO_OTHERS_RESPONSE,
        "delusion_paranoia": DELUSION_PARANOIA_RESPONSE,
        "psychotic_symptoms": PSYCHOTIC_SYMPTOMS_RESPONSE,
        "medical_or_clinical_advice": MEDICAL_ADVICE_RESPONSE,
        "emotional_distress": EMOTIONAL_DISTRESS_RESPONSE,
        "unknown_high_risk": DANGEROUS_BEHAVIOR_RESPONSE,
    }
    return mapping.get(risk_type, EMOTIONAL_DISTRESS_RESPONSE)