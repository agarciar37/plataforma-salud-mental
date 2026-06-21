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
    """Normaliza texto libre para reducir fallos por tildes, mayúsculas o abreviaturas."""
    txt = (message or "").lower().strip()
    txt = unicodedata.normalize("NFD", txt)
    txt = "".join(ch for ch in txt if unicodedata.category(ch) != "Mn")
    txt = txt.replace("¿", " ").replace("?", " ").replace("¡", " ").replace("!", " ")
    txt = re.sub(r"\bq\b", "que", txt)
    txt = re.sub(r"\bk\b", "que", txt)
    txt = re.sub(r"[^a-z0-9ñ\s]", " ", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt


def _match_regex(text: str, patterns: list[str]) -> list[str]:
    return [pattern for pattern in patterns if re.search(pattern, text)]


def _result(
    risk_level: RiskLevel,
    risk_type: RiskType,
    reason: str,
    matched_patterns: list[str],
    ai_allowed: bool | None = None,
) -> SafetyResult:
    if ai_allowed is None:
        ai_allowed = risk_level in {"low", "medium"}
    return SafetyResult(
        risk_level=risk_level,
        risk_type=risk_type,
        safety_triggered=risk_level != "low",
        ai_allowed=ai_allowed,
        reason=reason,
        matched_patterns=matched_patterns,
    )


def classify_safety(message: str) -> SafetyResult:
    """
    Clasificación heurística y conservadora de seguridad.

    Principio de diseño: ante duda razonable en un contexto de salud mental, se eleva el nivel
    de riesgo para evitar que el modelo generativo responda libremente a situaciones críticas.
    Esta función no realiza diagnóstico clínico; solo activa medidas de seguridad del sistema.
    """
    text = normalize_text(message)

    if not text:
        return _result("low", "normal", "Mensaje vacío o sin contenido analizable.", [], True)

    psychotic_crisis_patterns = [
        r"\b(voces|voz)\b.*\b(me dicen|me ordenan|me piden|quieren que|me mandan)\b.*\b(mate|matar|matarme|suicid|salte|saltar|tirarme|lanzarme|hacer dano|danar|apuñal|apunala|dispar|pegar|paliza)",
        r"\b(oigo|escucho)\b.*\b(voces|voz)\b.*\b(mate|matar|matarme|suicid|salte|saltar|tirarme|lanzarme|hacer dano|danar|pegar|paliza)",
        r"\b(las voces|una voz)\b.*\b(ordena|ordenan|manda|mandan|dice|dicen)\b.*\b(hacer dano|danar|matar|matarme|saltar|tirarme|pegar|atacar)",
    ]
    matches = _match_regex(text, psychotic_crisis_patterns)
    if matches:
        return _result("crisis", "psychotic_symptoms", "Síntomas psicóticos con posible orden de daño.", matches, False)

    self_harm_patterns = [
        r"\b(me quiero|quiero|voy a|me voy a|pienso|necesito|he decidido|estoy pensando en)\b.*\b(suicidar|suicidarme|matarme|morirme|morir|quitarme la vida|quitar la vida|acabar con mi vida|acabar con todo|acabar con esto)",
        r"\b(no quiero|no puedo)\b.*\b(seguir viviendo|vivir mas|continuar viviendo|existir|despertar)",
        r"\b(no quiero existir|ojala no despertar|ojala no me despierte|no despertar nunca|desearia no despertar|ojala estuviera muerto|ojala estuviese muerto|ojala estuviera muerta|ojala estuviese muerta|quiero dormirme y no despertar)\b",
        r"\b(no merece la pena|no vale la pena)\b.*\b(vivir|seguir|existir)",
        r"\b(seria mejor|estaria mejor)\b.*\b(muerto|muerta|desaparecer|no estar|no existir)",
        r"\b(me quiero|quiero|voy a|me voy a|pienso|estoy pensando en)\b.*\b(hacerme dano|danarme|autolesionarme|cortar|hacer cortes|hacerme cortes|cortarme|cortarme las venas|abrirme las venas|rajar|rajarme|rajarme las muñecas|rajarme las munecas|cortar las venas|ahorcarme|colgarme|dispararme|quemarme)",
        r"\b(cortare|me cortare|cortar[eé]|voy a cortarme|me corto|me quiero cortar)\b.*\b(venas|muñecas|munecas|brazos|piernas)",
        r"\b(rajarme|rajar|abrirme|abrir)\b.*\b(venas|muñecas|munecas)",
        r"\b(desaparecer para siempre|acabar con todo|terminar con todo|acabar con esto|quitarme de en medio)\b",
        r"\b(me da igual todo|ya no me importa nada)\b.*\b(vivir|morir|vida|existir)",
        r"\b(me quiero|quiero|voy a|me voy a|pienso|estoy pensando en)\b.*\b(pegarme un tiro|darme un tiro|volarme la cabeza|usar una pistola|usar un arma|dispararme)",
        r"\b(pegarme un tiro|darme un tiro|volarme la cabeza|dispararme)\b",
        r"\b(me quiero|quiero|voy a|me voy a|pienso|estoy pensando en)\b.*\b(clavarme un cuchillo|clavar un cuchillo|apuñalarme|apunalarme|hacerme una herida profunda|sangrar hasta)",
        r"\b(me quiero|quiero|voy a|me voy a|pienso|estoy pensando en)\b.*\b(colgarme|ahorcarme|hacerme un nudo|ponerme una soga|ponerme una cuerda)",
        r"\b(cuerda|soga)\b.*\b(cuello|colgarme|ahorcarme|nudo)",
        r"\b(voy a dormir|quiero dormir|dormirme)\b.*\b(para siempre|y no despertar|sin despertar)",
        r"\b(ojala|ojal[aá]|me gustaria|preferiria)\b.*\b(no despertar|morirme|estar muerto|estar muerta|me atropelle|desaparecer)",
        r"\b(no me importaria|me da igual)\b.*\b(morir|morirme|no despertar|que me pase algo)",
    ]
    matches = _match_regex(text, self_harm_patterns)
    if matches:
        return _result("crisis", "self_harm", "Ideación suicida o autolesiva explícita o altamente probable.", matches, False)

    overdose_patterns = [
        r"\b(tomar|tomarme|ingerir|tragar|tragarme|beber|beberme)\b.*\b(todas|muchas|un monton|demasiadas|varias|caja|bote|\d+)\b.*\b(pastillas|medicacion|medicamentos|ansioliticos|antidepresivos|ibuprofeno|paracetamol)",
        r"\b(tomar|tomarme|ingerir|tragar|tragarme|beber|beberme)\b.*\b(pastillas|medicacion|medicamentos|ansioliticos|antidepresivos|ibuprofeno|paracetamol)\b.*\b(todas|muchas|un monton|demasiadas|varias|caja|bote|\d+)",
        r"\b(tomar|tomarme|ingerir|tragar|tragarme|he tomado|me he tomado)\b.*\b\d+\b.*\b(pastillas|medicamentos|paracetamol|ibuprofeno|ansioliticos|antidepresivos)",
        r"\b(beber|beberme|he bebido|me he bebido|tomar|tomarme|ingerir|tragar|tragarme)\b.*\b(lejia|cloro|veneno|raticida|amoniaco|gasolina|alcohol de quemar|anticongelante)",
        r"\b(inhalar|respirar|abrir|poner)\b.*\b(gas|monoxido|butano)",
        r"\b(sobredosis|overdose)\b",
        r"\b(mezclar|mezclarme|combinar|combinarme)\b.*\b(alcohol|cerveza|vodka|vino)\b.*\b(pastillas|medicacion|medicamentos|ansioliticos|antidepresivos|benzodiacepinas|somniferos)",
        r"\b(mezclar|mezclarme|combinar|combinarme)\b.*\b(pastillas|medicacion|medicamentos|ansioliticos|antidepresivos|benzodiacepinas|somniferos)\b.*\b(alcohol|cerveza|vodka|vino)",
        r"\b(tomar|tomarme|tragar|tragarme)\b.*\b(un bote entero|la caja entera|todo el bote|toda la caja|muchos somniferos|pastillas para dormir)",
        r"\b(coche|auto|vehiculo)\b.*\b(garaje|garage)\b.*\b(encendido|arrancado|escape|humo)",
        r"\b(coche|auto|vehiculo)\b.*\b(encendido|arrancado|escape|humo)\b.*\b(garaje|garage)",
        r"\b(monoxido|monoxido de carbono|humo del coche|tubo de escape|escape del coche|brasero)\b",
    ]
    matches = _match_regex(text, overdose_patterns)
    if matches:
        return _result("crisis", "substance_or_overdose", "Riesgo de intoxicación, sobredosis o ingesta peligrosa.", matches, False)

    dangerous_behavior_patterns = [
        r"\b(saltar|tirar|tirarme|lanzar|lanzarme|arrojar|arrojarme|precipitar|precipitarme|brincar|caerme)\b.*\b(puente|ventana|balcon|azotea|tejado|precipicio|acantilado|terraza)",
        r"\b(puente|ventana|balcon|azotea|tejado|precipicio|acantilado|terraza)\b.*\b(saltar|tirar|tirarme|lanzar|lanzarme|arrojar|arrojarme|precipitar|precipitarme|brincar|caerme)",
        r"\b(saltar|tirar|tirarme|lanzar|lanzarme|arrojar|arrojarme|precipitar|precipitarme|brincar|caerme)\b.*\b(a ver que pasa|a ver que se siente|a ver que sensacion|por probar|quiero sentir algo|me da igual|no me importa)",
        r"\b(meter|meterme|tumbar|tumbarme|poner|ponerme|entrar|tirar|tirarme|lanzar|lanzarme|saltar|me tiro)\b.*\b(vias del tren|vias|tren|metro)",
        r"\b(me tiro|me lanzo|me voy a tirar|me voy a lanzar)\b.*\b(al tren|al metro|a las vias|vias)",
        r"\b(cruzar|meterme)\b.*\b(carretera|autopista)\b.*\b(sin mirar|a ver que pasa)",
        r"\b(conducir|manejar|estrellar|estrellarme)\b.*\b(coche|auto|vehiculo|muy rapido|a toda velocidad|sin frenar|contra un muro|contra un arbol|a ver que pasa)",
        r"\b(no respirar|dejar de respirar|aguantar la respiracion)\b.*\b(a ver|que se siente|sensacion|hasta desmayarme|por probar)",
        r"\b(ponerme|poner|colocarme|colocar|meterme|meter)\b.*\b(delante de un coche|frente a un coche|delante de un camion|frente a un camion|en mitad de la carretera|en medio de la carretera)",
        r"\b(quiero saber|voy a probar|por probar)\b.*\b(que se siente|sensacion)\b.*\b(no respirar|ahogarse|asfixiarse|saltar|caer)",
        r"\b(me da igual|no me importa|total da igual)\b.*\b(saltar|tirarme|lanzarme|conducir|pastillas|lejia|cloro|gas|cortarme|ahogarme|rio|mar|corriente)",

        # Agua / ahogamiento. Estos patrones cubren frases ambiguas o formuladas como
        # "curiosidad" que realmente implican riesgo inmediato: tirarse al río, dejarse
        # llevar por la corriente, meterse en el mar sin intención de salir, etc.
        r"\b(tirar|tirarme|lanzar|lanzarme|arrojar|arrojarme|meter|meterme|entrar|entrarme|saltar|me tiro|me lanzo)\b.*\b(rio|mar|lago|pantano|embalse|canal|corriente|agua|presa|muelle)",
        r"\b(rio|mar|lago|pantano|embalse|canal|corriente|agua|presa|muelle)\b.*\b(tirar|tirarme|lanzar|lanzarme|arrojar|arrojarme|meter|meterme|entrar|saltar|me tiro|me lanzo|tragar|trague|traga|arrastrar|arrastre|llevar|lleve)",
        r"\b(ahogarme|ahogarse|asfixiarme|asfixiarse)\b",
        r"\b(dejarme|me voy a dejar|voy a dejarme)\b.*\b(llevar|arrastrar|tragar|trague|traga)\b.*\b(corriente|rio|mar|agua)",
        r"\b(no salir|no volver|desaparecer)\b.*\b(rio|mar|agua|corriente|lago|pantano|embalse|canal)",
        r"\b(ya esta|no puedo mas|no aguanto mas|no veo salida|me da igual)\b.*\b(rio|mar|agua|corriente|ahogarme|tirarme|lanzarme)",
        r"\b(tirar|tirarme|lanzar|lanzarme|saltar|arrojar|arrojarme|precipitar|precipitarme)\b.*\b(edificio|piso|planta|mirador|muro alto|sitio alto|lugar alto)",
        r"\b(edificio|piso|planta|mirador|muro alto|sitio alto|lugar alto)\b.*\b(tirar|tirarme|lanzar|lanzarme|saltar|arrojar|arrojarme|precipitar|precipitarme)",
        r"\b(sentarse|sentarme|tumbarme|dormir|dormirme|ponerme)\b.*\b(vias|via del tren|vias del tren|tren|metro)",
        r"\b(tirarme|lanzarme|ponerme|meterme|tumbarme|sentarme)\b.*\b(carretera|autopista|autovia|calzada|trafico|camion|coche|bus)",
        r"\b(electrocutarme|meter los dedos en el enchufe|tocar cables pelados|meterme en cables)\b",
        r"\b(abrir el gas|dejar el gas abierto|encender el gas)\b.*\b(encerrado|encerrada|habitacion|cocina|casa|dormir|no despertar)",
    ]
    matches = _match_regex(text, dangerous_behavior_patterns)
    if matches:
        return _result("crisis", "dangerous_behavior", "Conducta física peligrosa o ambigua con riesgo inmediato.", matches, False)

    harm_to_others_patterns = [
        r"\b(quiero|voy a|me voy a|pienso|he decidido|tengo ganas de|estoy pensando en)\b.*\b(matar|asesinar|hacer dano|hacerle dano|danar|atacar|apuñalar|apunalar|disparar|pegar|pegarle|dar una paliza|darle una paliza|quemar)\b",
        r"\b(matar|asesinar|apuñalar|apunalar|disparar|atacar|pegarle|darle una paliza|dar una paliza)\b.*\b(a mi|a alguien|a mi hermano|a mi hermana|a mi madre|a mi padre|a mi pareja|a mi familia|a mis vecinos|a mi jefe|a un companero|a una persona)",
        r"\b(voy a pegarle|quiero pegarle|voy a darle una paliza|quiero darle una paliza|quiero reventarle la cara|voy a reventarle la cara)\b.*\b(a mi|a alguien|a mi hermano|a mi hermana|a mi madre|a mi padre|a mi pareja|a mi familia|a mis vecinos|a mi jefe|a un companero|a una persona)?",
        r"\b(vengarme|venganza)\b.*\b(hacer dano|danar|matar|atacar|pegar|paliza)",
        r"\b(voy con|llevo|voy a llevar|he cogido|tengo)\b.*\b(cuchillo|navaja|pistola|arma|bate)\b.*\b(instituto|universidad|trabajo|oficina|casa de|calle|clase)",
        r"\b(poner|poner una|voy a poner|fabricar|explotar)\b.*\b(bomba|explosivo)",
        r"\b(quemar|incendiar|prender fuego)\b.*\b(casa|coche|oficina|colegio|instituto|trabajo|persona|gente)",
    ]
    matches = _match_regex(text, harm_to_others_patterns)
    if matches:
        return _result("crisis", "harm_to_others", "Posible intención de dañar a terceros.", matches, False)

    psychotic_patterns = [
        r"\b(oigo|escucho)\b.*\b(voces|voz)\b",
        r"\b(las voces|una voz)\b.*\b(me dicen|me habla|me ordena|me manda)",
        r"\b(veo cosas|veo sombras|veo personas)\b.*\b(que otros no ven|que nadie ve)",
        r"\b(no se que es real|no distingo la realidad|estoy perdiendo la realidad|perdiendo la realidad)",
        r"\b(recibo mensajes secretos|mensajes secretos)",
        r"\b(la tele|la television|la tv|la radio)\b.*\b(me habla|me manda mensajes|me envia mensajes|me envia señales|me envia senales|me manda señales|me manda senales)",
        r"\b(veo sombras|veo figuras|veo personas)\b.*\b(me siguen|me persiguen|me observan|me amenazan)",
        r"\b(oigo|escucho)\b.*\b(voces|susurros)\b.*\b(insultan|amenazan|persiguen|controlan)",
    ]
    matches = _match_regex(text, psychotic_patterns)
    if matches:
        return _result("high", "psychotic_symptoms", "Indicadores de posible pérdida de contacto con la realidad o síntomas psicóticos.", matches, False)

    delusion_paranoia_patterns = [
        r"\b(vecinos|policia|gobierno|familia|compañeros|companeros|jefe|empresa|todos|alguien|movil|telefono)\b.*\b(me vigilan|me vigila|me espian|me espia|me controlan|me controla|me persiguen|me persigue|me siguen|me sigue|conspiran|me quieren envenenar|me quiere envenenar|quieren envenenarme|quiere envenenarme|me quieren hacer dano|me quiere hacer dano)",
        r"\b(me vigilan|me vigila|me espian|me espia|me estan vigilando|me estan espiando|me persiguen|me siguen|me sigue)\b",
        r"\b(el gobierno|la policia|mis vecinos|mi familia)\b.*\b(me sigue|me siguen|me vigila|me vigilan|me controla|me controlan|me espia|me espian)",
        r"\b(camaras ocultas|microfonos ocultos|me han puesto un chip|tengo un chip|chip en la cabeza)",
        r"\b(me controlan la mente|me leen la mente|leen mis pensamientos|control mental|me controlan por el movil|me controlan desde el movil|me controla el movil|me controla desde el movil|el movil me controla|mi movil me controla)",
        r"\b(me quieren envenenar|me quiere envenenar|quieren envenenarme|quiere envenenarme|mi comida esta envenenada)",
        r"\b(satelites|drones|antenas|5g)\b.*\b(me vigilan|me controlan|me espian|me siguen|leen mi mente|leen mis pensamientos)",
        r"\b(me han implantado|me implantaron|tengo implantado)\b.*\b(chip|dispositivo|microchip)",
        r"\b(hackean|hackearon|controlan)\b.*\b(mi cerebro|mi mente|mis pensamientos)",
        r"\b(todos estan contra mi|todo el mundo esta contra mi)\b.*\b(conspiracion|conspiran|me persiguen|me quieren hacer dano)",
    ]
    matches = _match_regex(text, delusion_paranoia_patterns)
    if matches:
        return _result("high", "delusion_paranoia", "Indicadores de paranoia, delirio persecutorio o creencias potencialmente peligrosas.", matches, False)

    medical_patterns = [
        r"\b(dejar|dejo|voy a dejar|suspender|suspendo|quitar|quitarme|dejar de tomar|dejo de tomar|abandonar)\b.*\b(medicacion|medicamento|pastillas|antidepresivo|antidepresivos|ansiolitico|ansioliticos|tratamiento)",
        r"\b(puedo|deberia|puedo dejar|es seguro)\b.*\b(dejar|suspender|quitar|dejar de tomar)\b.*\b(medicacion|medicamento|pastillas|antidepresivos|ansioliticos|tratamiento)",
        r"\b(que dosis|cuanta dosis|cuantas pastillas|que medicamento|que medicacion)\b",
        r"\b(diagnosticame|diagnostico|tengo depresion clinica|tengo esquizofrenia|tengo trastorno bipolar|soy bipolar)",
        r"\b(duplicar|doblar|subir|aumentar|bajar|reducir)\b.*\b(dosis|medicacion|medicamento|pastillas|antidepresivo|ansiolitico)",
        r"\b(voy a tomar mas|me voy a tomar mas|tomare mas)\b.*\b(medicacion|medicamento|pastillas|antidepresivo|ansiolitico)",
        r"\b(no voy a comer|dejar de comer|voy a dejar de comer)\b.*\b(hasta desaparecer|hasta morirme|para siempre|no me importa)",
    ]
    matches = _match_regex(text, medical_patterns)
    if matches:
        return _result("high", "medical_or_clinical_advice", "Solicitud de diagnóstico, medicación o modificación de tratamiento.", matches, False)

    # Fallback contextual: combina desesperanza/finalidad con medios o lugares peligrosos.
    # Esto reduce falsos negativos ante frases que no usan las expresiones exactas anteriores.
    finality_or_despair_patterns = [
        r"\b(ya esta|se acabo|hasta aqui|no puedo mas|no aguanto mas|no veo salida|me rindo|me despido|adios a todos|perdonadme por todo|no vais a volver a verme|esta noche termina todo|hoy termina todo|hoy se acaba todo)\b",
    ]
    danger_context_patterns = [
        r"\b(rio|mar|lago|pantano|embalse|canal|corriente|agua|puente|ventana|balcon|azotea|tejado|edificio|piso|tren|metro|vias|carretera|autopista|coche|camion|gas|monoxido|pastillas|medicacion|cuchillo|navaja|cuerda|soga|arma|pistola|veneno|lejia|cloro)\b",
    ]
    finality_matches = _match_regex(text, finality_or_despair_patterns)
    danger_matches = _match_regex(text, danger_context_patterns)
    if finality_matches and danger_matches:
        return _result(
            "crisis",
            "dangerous_behavior",
            "Desesperanza o despedida combinada con medio, lugar u objeto peligroso.",
            finality_matches + danger_matches,
            False,
        )

    farewell_patterns = [
        r"\b(no vais a volver a verme|perdonadme por todo|gracias por todo y adios|me despido de todos|esta es mi despedida|esta noche termina todo|hoy termina todo|hoy se acaba todo)\b",
    ]
    matches = _match_regex(text, farewell_patterns)
    if matches:
        return _result("crisis", "self_harm", "Mensaje de despedida o finalidad con posible riesgo autolesivo.", matches, False)

    severe_distress_patterns = [
        r"\b(no puedo mas|no aguanto mas|no aguanto|estoy desesperado|estoy desesperada|todo me supera|no veo salida|me siento atrapado|me siento atrapada|me siento roto|me siento rota)",
        r"\b(no puedo seguir asi|esto es insoportable|no se que hacer con mi vida|estoy fatal no aguanto)",
    ]
    matches = _match_regex(text, severe_distress_patterns)
    if matches:
        return _result("medium", "emotional_distress", "Malestar emocional intenso sin plan explícito de daño.", matches, True)

    return _result("low", "normal", "Sin señales de riesgo relevantes.", [], True)
