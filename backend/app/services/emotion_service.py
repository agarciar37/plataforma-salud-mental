def detect_emotion(text: str) -> str:
    text = text.lower()

    anxiety_keywords = ["ansioso", "ansiedad", "nervioso", "agobiado", "preocupado"]
    sadness_keywords = ["triste", "solo", "vacío", "deprimido", "desanimado"]
    stress_keywords = ["estresado", "estres", "cansado", "saturado", "agotado"]
    positive_keywords = ["bien", "feliz", "motivado", "tranquilo", "contento"]

    if any(word in text for word in anxiety_keywords):
        return "ansiedad"
    if any(word in text for word in sadness_keywords):
        return "tristeza"
    if any(word in text for word in stress_keywords):
        return "estrés"
    if any(word in text for word in positive_keywords):
        return "positivo"

    return "neutral"