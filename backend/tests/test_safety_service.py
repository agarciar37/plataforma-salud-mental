from app.services.safety_service import (
    append_non_diagnostic_disclaimer,
    get_crisis_resources,
    is_high_risk_message,
)


def test_is_high_risk_message_detects_risk_keywords():
    assert is_high_risk_message("No quiero vivir") is True


def test_get_crisis_resources_uses_fallback_for_unknown_country():
    resources = get_crisis_resources("XX")
    assert len(resources) == 3
    assert "Emergencias" in resources[0]


def test_append_non_diagnostic_disclaimer_is_idempotent():
    base_message = "Estoy aquí para escucharte."
    once = append_non_diagnostic_disclaimer(base_message)
    twice = append_non_diagnostic_disclaimer(once)
    assert once == twice