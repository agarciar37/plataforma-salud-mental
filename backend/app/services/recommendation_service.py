def get_recommendations(emotion: str) -> list[str]:
    recommendations = {
        "tristeza": [
            "Escribe durante unos minutos cómo te sientes para ordenar tus pensamientos.",
            "Hablar con alguien de confianza puede ayudarte a sentirte acompañado.",
            "Haz una actividad breve que normalmente te aporte calma o consuelo."
        ],
        "ansiedad": [
            "Prueba a hacer respiraciones lentas durante uno o dos minutos.",
            "Intenta centrarte solo en la siguiente tarea inmediata.",
            "Reducir estímulos durante un rato puede ayudarte a bajar el agobio."
        ],
        "felicidad": [
            "Identifica qué está contribuyendo a que te sientas así para reforzarlo.",
            "Aprovecha este momento para consolidar hábitos positivos.",
            "Compartir este estado con alguien cercano también puede reforzarlo."
        ],
        "neutral": [
            "Si quieres, puedes profundizar un poco más en cómo te has sentido hoy.",
            "Llevar un pequeño registro emocional diario puede ayudarte a conocerte mejor.",
            "Hacer pausas breves durante el día puede mejorar tu bienestar general."
        ],
        "crisis": [
            "Contacta con emergencias (112/911 según tu país) si hay riesgo inmediato.",
            "Busca apoyo de una persona de confianza y evita quedarte solo/a.",
            "Acude a un profesional de salud mental para atención especializada."
        ],
    }

    return recommendations.get(emotion, recommendations["neutral"])