from __future__ import annotations

import re
from collections import Counter


EMOTION_LABELS = {
    "ansiedad",
    "estres",
    "tristeza",
    "neutral",
    "positivo",
    "crisis",
}


EMOTION_PATTERNS: dict[str, list[str]] = {
    "ansiedad": [
        "ansiedad",
        "ansioso",
        "ansiosa",
        "nervioso",
        "nerviosa",
        "pánico",
        "panico",
        "preocupado",
        "preocupada",
        "rumiar",
    ],
    "estrés": [
        "estrés",
        "estres",
        "estresado",
        "estresada",
        "saturado",
        "saturada",
        "agotado",
        "agotada",
        "quemado",
        "quemada",
        "sobrepasado",
        "sobrepasada",
        "presión",
        "presion",
    ],
    "tristeza": [
        "triste",
        "deprimido",
        "deprimida",
        "vacío",
        "vacio",
        "solo",
        "sola",
        "desanimado",
        "desanimada",
        "llorar",
        "sin ganas",
    ],
    "positivo": [
        "feliz",
        "contento",
        "contenta",
        "motivado",
        "motivada",
        "tranquilo",
        "tranquila",
        "agradecido",
        "agradecida",
        "esperanzado",
        "esperanzada",
        "orgulloso",
        "orgullosa",
        "alegre",
    ],
    "crisis": [
        "suicidio",
        "suicid",
        "quitarme la vida",
        "no quiero vivir",
        "me quiero morir",
        "hacerme daño",
        "autoles",
    ],
}


INTENSIFIERS = {"muy", "demasiado", "mucho", "totalmente", "bastante"}
NEGATIONS = {"no", "nunca", "jamás", "jamas"}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _score_by_keywords(text: str) -> Counter:
    normalized = _normalize(text)
    tokens = normalized.split()
    token_set = set(tokens)

    scores: Counter = Counter()

    for label, patterns in EMOTION_PATTERNS.items():
        for pattern in patterns:
            if " " in pattern:
                if pattern in normalized:
                    scores[label] += 2
            elif pattern in token_set or pattern in normalized:
                scores[label] += 1

    for idx, token in enumerate(tokens):
        if token in INTENSIFIERS and idx + 1 < len(tokens):
            next_token = tokens[idx + 1]
            for label, patterns in EMOTION_PATTERNS.items():
                if next_token in patterns:
                    scores[label] += 1

        if token in NEGATIONS and idx + 1 < len(tokens):
            next_token = tokens[idx + 1]
            if next_token in EMOTION_PATTERNS["positivo"]:
                scores["tristeza"] += 1
                scores["positivo"] = max(scores["positivo"] - 1, 0)

    return scores


def detect_emotion(text: str) -> str:
    if not text or not text.strip():
        return "neutral"

    scores = _score_by_keywords(text)

    if scores.get("crisis", 0) > 0:
        return "crisis"

    if not scores:
        return "neutral"

    ordered = ["ansiedad", "estrés", "tristeza", "positivo", "neutral"]
    best = max(ordered, key=lambda label: (scores.get(label, 0), -ordered.index(label)))

    if scores.get(best, 0) == 0:
        return "neutral"

    return best