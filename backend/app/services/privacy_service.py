import re


EMAIL_PATTERN = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b")
PHONE_PATTERN = re.compile(r"\b(?:\+?\d{1,3}[\s-]?)?(?:\d[\s-]?){8,14}\d\b")
ID_PATTERN = re.compile(r"\b\d{8}[A-Za-z]\b")


def redact_pii(text: str) -> tuple[str, bool, list[str]]:
    """
    Redacta patrones comunes de información sensible antes de enviar texto a la IA.
    Devuelve:
    - texto redaccionado
    - si se aplicó redacción
    - tipos detectados
    """
    if not text:
        return text, False, []

    redacted = text
    detected_types: list[str] = []

    if EMAIL_PATTERN.search(redacted):
        redacted = EMAIL_PATTERN.sub("[EMAIL_REDACTED]", redacted)
        detected_types.append("email")

    if PHONE_PATTERN.search(redacted):
        redacted = PHONE_PATTERN.sub("[PHONE_REDACTED]", redacted)
        detected_types.append("phone")

    if ID_PATTERN.search(redacted):
        redacted = ID_PATTERN.sub("[ID_REDACTED]", redacted)
        detected_types.append("id")

    was_redacted = redacted != text
    return redacted, was_redacted, detected_types