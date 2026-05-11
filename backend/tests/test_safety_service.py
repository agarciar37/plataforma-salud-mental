from app.services.safety_service import (
    get_crisis_resources,
    is_high_risk_message,
)


def test_is_high_risk_message_detects_risk_keywords():
    assert is_high_risk_message("No quiero vivir") is True


def test_get_crisis_resources_uses_fallback_for_unknown_country():
    resources = get_crisis_resources("XX")
    assert len(resources) == 3
    assert "Emergencias" in resources[0]
