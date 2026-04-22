from app.services.privacy_service import redact_pii


def test_redact_pii_masks_email_phone_and_id():
    text = "Mi email es user@example.com y mi teléfono +34 600 123 456 con DNI 12345678Z."
    redacted, was_redacted, detected = redact_pii(text)

    assert was_redacted is True
    assert "[EMAIL_REDACTED]" in redacted
    assert "[PHONE_REDACTED]" in redacted
    assert "[ID_REDACTED]" in redacted
    assert set(detected) == {"email", "phone", "id"}


def test_redact_pii_returns_original_when_no_pii():
    text = "Hoy me siento algo preocupado por el trabajo."
    redacted, was_redacted, detected = redact_pii(text)

    assert redacted == text
    assert was_redacted is False
    assert detected == []