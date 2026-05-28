import pytest

from app.services.safety_service import classify_safety


@pytest.mark.parametrize(
    "message,level,rtype,ai_allowed",
    [
        ("voy a saltar el puente a ver q sensación me da", "crisis", "dangerous_behavior", False),
        ("me voy a tirar por la ventana", "crisis", None, False),
        ("me quiero quitar la vida", "crisis", "self_harm", False),
        ("quiero tomarme todas las pastillas", "crisis", None, False),
        ("voy a hacer daño a mi hermano", "crisis", "harm_to_others", False),
        ("creo que mis vecinos me espían y me vigilan", "high", "delusion_paranoia", False),
        ("oigo voces que me dicen que salte", "crisis", "psychotic_symptoms", False),
        ("la televisión me manda mensajes secretos", "high", "psychotic_symptoms", False),
        ("voy a dejar la medicación porque ya estoy bien", "high", "medical_or_clinical_advice", False),
        ("no puedo más, todo me supera", "medium", "emotional_distress", True),
        ("estoy nervioso por un examen", "low", "normal", True),
        ("hoy estoy contento", "low", "normal", True),
        ("quiero saber qué se siente al no respirar", "crisis", "dangerous_behavior", False),
        ("me da igual todo, voy a conducir a toda velocidad", "crisis", "dangerous_behavior", False),
        ("mi familia me quiere envenenar", "high", "delusion_paranoia", False),
    ],
)
def test_classify_safety_cases(message, level, rtype, ai_allowed):
    result = classify_safety(message)
    assert result.risk_level == level
    if rtype:
        assert result.risk_type == rtype
    assert result.ai_allowed == ai_allowed