from app.services.emotion_service import detect_emotion

def test_detect_emotion_returns_estres_for_stress_keywords():
    assert detect_emotion("Estoy muy estresado y saturado") == "estres"

def test_detect_emotion_returns_positivo_for_positive_keywords():
    assert detect_emotion("Hoy me siento muy contento y alegre") == "positivo"

def test_detect_emotion_detects_crisis():
    assert detect_emotion("No quiero vivir, quiero quitarme la vida") == "crisis"

def test_detect_emotion_returns_neutral_when_no_keywords():
    assert detect_emotion("He tenido un día normal") == "neutral"