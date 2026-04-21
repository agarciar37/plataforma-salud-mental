from app.services.emotion_service import detect_emotion


def test_detect_emotion_returns_ansiedad_for_stress_keywords():
    assert detect_emotion("Estoy muy estresado y saturado") == "ansiedad"


def test_detect_emotion_returns_felicidad_for_positive_keywords():
    assert detect_emotion("Hoy me siento muy contento y alegre") == "felicidad"


def test_detect_emotion_returns_neutral_when_no_keywords():
    assert detect_emotion("He tenido un día normal") == "neutral"