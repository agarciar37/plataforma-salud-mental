from __future__ import annotations

from app.services.safety_service import RiskType


CRISIS_SELF_HARM_RESPONSE = (
    "Me preocupa mucho lo que estás compartiendo y tu seguridad es la prioridad ahora mismo. "
    "Por favor, aléjate de cualquier cosa con la que puedas hacerte daño y busca un lugar seguro.\n\n"
    "Si estás en España, llama al 112 ahora mismo o al 024 (Línea de atención a la conducta suicida). "
    "También te puede ayudar contactar de inmediato con una persona de confianza que pueda acompañarte.\n\n"
    "No estás solo/a en esto. Lo más importante ahora es mantenerte a salvo."
)

BRIDGE_OR_HEIGHT_RESPONSE = (
    "Me preocupa mucho lo que acabas de decir, porque saltar desde un puente, ventana, balcón o zona elevada "
    "puede ponerte en peligro inmediato. Por favor, aléjate ahora mismo de esa zona y busca un lugar seguro.\n\n"
    "Si estás en España, llama al 112 o contacta inmediatamente con una persona de confianza que pueda acompañarte. "
    "También puedes llamar al 024, la línea de atención a la conducta suicida.\n\n"
    "No tienes que afrontar esto solo/a. Lo más importante ahora es tu seguridad inmediata."
)

DANGEROUS_BEHAVIOR_RESPONSE = (
    "Me preocupa mucho lo que acabas de decir, porque esa acción puede ponerte en peligro inmediato. "
    "Por favor, aléjate ahora mismo del lugar u objeto peligroso y busca un lugar seguro.\n\n"
    "Si estás en España, llama al 112 o contacta inmediatamente con una persona de confianza que pueda acompañarte. "
    "También puedes llamar al 024, la línea de atención a la conducta suicida.\n\n"
    "No tienes que afrontar esto solo/a. Lo más importante ahora es tu seguridad inmediata."
)

WATER_OR_DROWNING_RESPONSE = (
    "Me preocupa mucho lo que acabas de decir, porque meterte o tirarte al agua, al río, al mar "
    "o dejarte llevar por la corriente puede ponerte en peligro inmediato. Por favor, aléjate ahora mismo "
    "de esa zona y busca un lugar seguro.\n\n"
    "Si estás en España, llama al 112 o contacta inmediatamente con una persona de confianza que pueda acompañarte. "
    "También puedes llamar al 024, la línea de atención a la conducta suicida.\n\n"
    "No tienes que afrontar esto solo/a. Lo más importante ahora es tu seguridad inmediata."
)

SUBSTANCE_OR_OVERDOSE_RESPONSE = (
    "Me preocupa lo que estás planteando, porque tomar muchas pastillas, medicación o sustancias peligrosas "
    "puede poner tu vida en riesgo. Por favor, no lo hagas y aléjate de esas sustancias ahora mismo si las tienes cerca.\n\n"
    "Si estás en España, llama al 112 de inmediato. También puedes contactar con una persona de confianza para que esté contigo "
    "y llamar al 024 si esto está relacionado con ideas de hacerte daño.\n\n"
    "Lo más importante ahora es que no te quedes solo/a y busques ayuda inmediata."
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
    "Evita enfrentarte a otras personas o tomar decisiones precipitadas mientras te sientes así. "
    "Si sientes riesgo de hacerte daño o hacer daño a alguien, llama al 112."
)

PSYCHOTIC_SYMPTOMS_RESPONSE = (
    "Gracias por contarlo. Lo que describes puede ser muy angustiante y es importante que tengas apoyo ahora. "
    "No voy a discutir si esas voces, señales o percepciones son reales, pero sí me preocupa cómo te hacen sentir.\n\n"
    "Busca una persona de confianza y contacta con un profesional de salud mental cuanto antes. "
    "Si sientes peligro inmediato o impulso de hacerte daño o dañar a alguien, llama al 112 de inmediato."
)

MEDICAL_ADVICE_RESPONSE = (
    "No puedo diagnosticar ni indicar medicación. Para tu seguridad, no modifiques ni suspendas un tratamiento "
    "sin supervisión profesional.\n\n"
    "Te recomiendo consultar con tu médico, psiquiatra o profesional de salud mental para una pauta segura. "
    "Si notas riesgo inmediato, llama al 112."
)

EMOTIONAL_DISTRESS_RESPONSE = (
    "Siento que estés pasando por un momento tan intenso. Gracias por expresarlo.\n\n"
    "Si te ayuda, prueba a respirar lento unos minutos, escribir lo que sientes y contactar con alguien de confianza. "
    "Si notas que el riesgo aumenta o te sientes en peligro, llama al 112 o al 024 en España."
)


def get_safety_response(risk_type: RiskType, matched_patterns: list[str] | None = None) -> str:
    """Devuelve una respuesta segura predefinida sin generación libre por IA."""
    joined_patterns = " ".join(matched_patterns or [])

    if risk_type == "dangerous_behavior" and any(
        word in joined_patterns
        for word in ["puente", "ventana", "balcon", "azotea", "tejado", "precipicio", "acantilado", "terraza"]
    ):
        return BRIDGE_OR_HEIGHT_RESPONSE

    if risk_type == "dangerous_behavior" and any(
        word in joined_patterns
        for word in ["rio", "mar", "lago", "pantano", "embalse", "canal", "corriente", "agua", "ahog"]
    ):
        return WATER_OR_DROWNING_RESPONSE

    mapping = {
        "self_harm": CRISIS_SELF_HARM_RESPONSE,
        "dangerous_behavior": DANGEROUS_BEHAVIOR_RESPONSE,
        "substance_or_overdose": SUBSTANCE_OR_OVERDOSE_RESPONSE,
        "harm_to_others": HARM_TO_OTHERS_RESPONSE,
        "delusion_paranoia": DELUSION_PARANOIA_RESPONSE,
        "psychotic_symptoms": PSYCHOTIC_SYMPTOMS_RESPONSE,
        "medical_or_clinical_advice": MEDICAL_ADVICE_RESPONSE,
        "emotional_distress": EMOTIONAL_DISTRESS_RESPONSE,
        "unknown_high_risk": DANGEROUS_BEHAVIOR_RESPONSE,
    }
    return mapping.get(risk_type, EMOTIONAL_DISTRESS_RESPONSE)
