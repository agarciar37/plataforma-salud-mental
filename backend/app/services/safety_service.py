from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata
from typing import Literal

RiskLevel = Literal["low", "medium", "high", "crisis"]
RiskType = Literal[
    "normal",
    "emotional_distress",
    "self_harm",
    "dangerous_behavior",
    "harm_to_others",
    "delusion_paranoia",
    "psychotic_symptoms",
    "medical_or_clinical_advice",
    "substance_or_overdose",
    "unknown_high_risk",
]

@dataclass
class SafetyResult:
    risk_level: RiskLevel
    risk_type: RiskType
    safety_triggered: bool
    ai_allowed: bool
    reason: str
    matched_patterns: list[str]


CRISIS_RESOURCES_BY_COUNTRY = {"ES": ["112", "024"]}


def normalize_text(message: str) -> str:
    txt = message.lower().strip()
    txt = unicodedata.normalize("NFD", txt)
    txt = "".join(ch for ch in txt if unicodedata.category(ch) != "Mn")
    txt = re.sub(r"\bq\b", "que", txt)
    txt = re.sub(r"\s+", " ", txt)
    return txt


def _contains_any(text: str, patterns: list[str]) -> list[str]:
    return [p for p in patterns if p in text]


def classify_safety(message: str) -> SafetyResult:
    text = normalize_text(message)

    dangerous_actions = ["saltar", "tirar", "tirarme", "lanzarme", "meterme", "conducir", "beber lejia", "no respirar", "al no respirar", "tomarme", "ingerir", "cortarme", "ahorcarme", "estrellarme"]
    dangerous_means = ["puente", "balcon", "ventana", "azotea", "vias del tren", "tren", "coche", "carretera", "pastillas", "lejia", "veneno", "gas", "precipicio", "rio", "mar"]
    ambiguous_danger = ["a ver que pasa", "a ver que se siente", "que se siente", "a ver que sensacion", "me da igual", "no me importa", "quiero sentir algo", "ya vere", "total da igual", "no pasa nada"]

    self_harm = ["me quiero suicidar", "quitarme la vida", "quiero quitar la vida", "me quiero quitar la vida", "quiero morirme", "me quiero morir", "no quiero seguir viviendo", "hacerme dano", "quiero hacerme dano", "no merece la pena vivir", "desaparecer para siempre"]
    harm_others = ["voy a matar", "quiero matar", "voy a hacer dano a", "quiero hacerle dano", "voy a apunalar", "voy a disparar", "voy a atacar"]
    paranoia = ["me persiguen", "me espian", "me estan vigilando", "camaras ocultas", "me controlan la mente", "me leen la mente", "me quieren envenenar", "mi familia me quiere envenenar", "todos conspiran contra mi", "me han puesto un chip", "television me habla"]
    psychotic = ["oigo voces", "escucho voces", "las voces me dicen", "veo cosas que otros no ven", "recibo mensajes secretos", "no se que es real", "perdiendo la realidad", "television me manda mensajes"]
    psychotic_commands = ["las voces me dicen que me mate", "las voces me dicen que haga dano", "las voces me dicen que salte", "voces que me dicen que salte"]
    medical = ["dejar la medicacion", "dejar las pastillas", "antidepresivos", "que dosis", "diagnosticame", "medicamento tomar", "tengo esquizofrenia", "tengo depresion clinica"]
    distress = ["no puedo mas", "estoy desesperado", "todo me supera", "no aguanto mas", "me siento atrapado", "me siento roto", "no veo salida"]

    cmd = _contains_any(text, psychotic_commands)
    if cmd:
        return SafetyResult("crisis", "psychotic_symptoms", True, False, "Comandos de daño asociados a voces.", cmd)

    sh = _contains_any(text, self_harm)
    if sh:
        return SafetyResult("crisis", "self_harm", True, False, "Ideación suicida/autolesiva explícita.", sh)

    ho = _contains_any(text, harm_others)
    if ho:
        return SafetyResult("crisis", "harm_to_others", True, False, "Posible daño a terceros.", ho)

    da = _contains_any(text, dangerous_actions)
    dm = _contains_any(text, dangerous_means)
    ad = _contains_any(text, ambiguous_danger)
    if (da and dm) or (da and ad):
        m = da + dm + ad
        rtype: RiskType = "substance_or_overdose" if any(x in text for x in ["pastillas", "lejia", "ingerir", "tomarme"]) else "dangerous_behavior"
        return SafetyResult("crisis", rtype, True, False, "Combinación de conducta peligrosa con medio/contexto de riesgo.", m)
    if dm and ad:
        return SafetyResult("high", "dangerous_behavior", True, False, "Contexto ambiguo con medio peligroso.", dm + ad)

    dp = _contains_any(text, paranoia)
    if dp:
        return SafetyResult("high", "delusion_paranoia", True, False, "Indicadores de paranoia/delirio persecutorio.", dp)

    ps = _contains_any(text, psychotic)
    if ps:
        return SafetyResult("high", "psychotic_symptoms", True, False, "Indicadores de síntomas psicóticos.", ps)

    md = _contains_any(text, medical)
    if md:
        return SafetyResult("high", "medical_or_clinical_advice", True, False, "Solicitud de diagnóstico o ajuste de medicación.", md)

    ds = _contains_any(text, distress)
    if ds:
        return SafetyResult("medium", "emotional_distress", True, True, "Malestar emocional intenso sin plan de daño explícito.", ds)

    return SafetyResult("low", "normal", False, True, "Sin señales de riesgo relevantes.", [])