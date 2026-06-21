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

    # Expresiones coloquiales que contienen verbos sensibles pero no expresan riesgo real.
    # Se evalúan antes de los patrones conservadores para reducir falsos positivos obvios.
    benign_idiom_patterns = [
        r"\b(me quiero morir de risa|me muero de risa|morirme de risa)\b",
        r"\b(quiero matar el tiempo|matar el tiempo)\b",
        r"\b(me tiro|me voy a tirar|voy a tirarme)\b.*\b(piscina)\b.*\b(verano|vacaciones|entrenamiento|competicion|competición|clase|fiesta)\b",
    ]
    dangerous_override_patterns = [
        r"\b(ahogarme|ahogarse|no salir|no volver|desaparecer|morirme|no puedo mas|no aguanto mas|me da igual|corriente|tragar|arrastrar)\b",
    ]
    benign_matches = _match_regex(text, benign_idiom_patterns)
    if benign_matches and not _match_regex(text, dangerous_override_patterns):
        return _result("low", "normal", "Expresión coloquial sin señales de riesgo relevantes.", benign_matches, True)

    psychotic_crisis_patterns = [
        r"\b(voces|voz)\b.*\b(me dicen|me ordenan|me piden|quieren que|me mandan)\b.*\b(mate|matar|matarme|suicid|salte|saltar|tirarme|lanzarme|hacer dano|danar|apuñal|apunala|dispar|pegar|paliza)",
        r"\b(oigo|escucho)\b.*\b(voces|voz)\b.*\b(mate|matar|matarme|suicid|salte|saltar|tirarme|lanzarme|hacer dano|danar|pegar|paliza)",
        r"\b(las voces|una voz)\b.*\b(ordena|ordenan|manda|mandan|dice|dicen)\b.*\b(hacer dano|danar|matar|matarme|saltar|tirarme|pegar|atacar)",
        r"\b(dios|un demonio|el demonio|una entidad|alguien invisible)\b.*\b(me ordena|me manda|me dice|me pide)\b.*\b(hacer dano|haga dano|hacerme dano|danar|matar|mate|matarme|suicid|saltar|salte|tirarme|atacar)",
    ]
    matches = _match_regex(text, psychotic_crisis_patterns)
    if matches:
        return _result("crisis", "psychotic_symptoms", "Síntomas psicóticos con posible orden de daño.", matches, False)

    early_harm_to_others_patterns = [
        r"\b(voy a|quiero|me voy a|pienso|he decidido|tengo ganas de|estoy pensando en)\b.*\b(matar|asesinar|apuñalar|apunalar|disparar|atacar|golpear|pegar|hacer dano|hacerle dano|danar|envenenar|atropellar|empujar)\b.*\b(a alguien|a una persona|a mi|a mi jefe|a mi pareja|a mi madre|a mi padre|a mi hermano|a mi hermana|a mi compañero|a mi companero|a mi profesor|a mis vecinos|a la gente|en clase|en el trabajo|en el colegio|en el instituto)",
        r"\b(voy a|quiero|me voy a|pienso)\b.*\b(hacer explotar|explotar|poner una bomba|detonar|volar)\b.*\b(colegio|instituto|universidad|oficina|trabajo|casa|edificio|clase)",
        r"\b(voy a|quiero|me voy a|pienso)\b.*\b(atropellar|arrollar|pasar por encima)\b.*\b(a alguien|a una persona|a la gente|a mi jefe|a mi pareja|a mi compañero|a mi companero)",
    ]
    matches = _match_regex(text, early_harm_to_others_patterns)
    if matches:
        return _result("crisis", "harm_to_others", "Posible intención de dañar a terceros.", matches, False)

    self_harm_patterns = [
        r"\b(me quiero|quiero|voy a|me voy a|pienso|necesito|he decidido|estoy pensando en)\b.*\b(suicidar|suicidarme|matarme|morirme|morir|quitarme la vida|quitar la vida|acabar con mi vida|acabar con todo|acabar con esto)",
        r"\b(tengo un plan|he preparado un plan|ya lo tengo planeado)\b.*\b(acabar con mi vida|matarme|suicidarme|quitarme la vida|morir)",
        r"\b(no quiero|no puedo)\b.*\b(seguir viviendo|vivir mas|continuar viviendo|existir|despertar)",
        r"\b(no quiero existir|ojala no despertar|ojala no me despierte|no despertar nunca|desearia no despertar|ojala estuviera muerto|ojala estuviese muerto|ojala estuviera muerta|ojala estuviese muerta|quiero dormirme y no despertar|me voy a dormir para siempre)\b",
        r"\b(no merece la pena|no vale la pena)\b.*\b(vivir|seguir|existir)",
        r"\b(seria mejor|estaria mejor)\b.*\b(muerto|muerta|desaparecer|no estar|no existir)",
        r"\b(me quiero|quiero|voy a|me voy a|pienso|estoy pensando en|necesito)\b.*\b(hacerme dano|danarme|autolesionarme|autolesionar|cortar|hacer cortes|hacerme cortes|cortarme|cortarme las venas|abrirme las venas|rajar|rajarme|rajarme las muñecas|rajarme las munecas|cortar las venas|ahorcarme|ahorcar|colgarme|colgar|dispararme|quemarme|degollarme|apuñalarme|apunalarme|apuñalar|apunalar|desangrarme)",
        r"\b(cortare|me cortare|cortar[eé]|voy a cortarme|me corto|me quiero cortar)\b.*\b(venas|muñecas|munecas|brazos|piernas)",
        r"\b(rajarme|rajar|abrirme|abrir)\b.*\b(venas|muñecas|munecas)",
        r"\b(desaparecer para siempre|acabar con todo|terminar con todo|acabar con esto|quitarme de en medio)\b",
        r"\b(me da igual todo|ya no me importa nada)\b.*\b(vivir|morir|vida|existir)",
        r"\b(me quiero|quiero|voy a|me voy a|pienso|estoy pensando en)\b.*\b(pegarme un tiro|darme un tiro|volarme la cabeza|usar una pistola|usar un arma|dispararme)",
        r"\b(pegarme un tiro|darme un tiro|volarme la cabeza|dispararme|me voy a pegar un tiro|voy a pegarme un tiro)\b",
        r"\b(me quiero|quiero|voy a|me voy a|pienso|estoy pensando en)\b.*\b(clavarme un cuchillo|clavar un cuchillo|apuñalarme|apunalarme|apuñalar|apunalar|degollarme|cortarme el cuello|hacerme una herida profunda|sangrar hasta|desangrarme)",
        r"\b(me quiero|quiero|voy a|me voy a|pienso|estoy pensando en)\b.*\b(colgarme|colgar|ahorcarme|ahorcar|hacerme un nudo|ponerme una soga|ponerme una cuerda)",
        r"\b(cuerda|soga)\b.*\b(cuello|colgarme|ahorcarme|ahorcar|nudo)",
        r"\b(he comprado|he preparado|tengo preparada|tengo listo|tengo lista)\b.*\b(cuerda|soga|nudo)",
        r"\b(voy a dormir|quiero dormir|dormirme)\b.*\b(para siempre|y no despertar|sin despertar)",
        r"\b(ojala|ojal[aá]|me gustaria|preferiria)\b.*\b(no despertar|morirme|estar muerto|estar muerta|me atropelle|desaparecer)",
        r"\b(no me importaria|me da igual)\b.*\b(morir|morirme|no despertar|que me pase algo)",
        r"\b(me estoy cortando|me acabo de cortar|estoy sangrando mucho|me estoy desangrando|he sangrado mucho)\b",
        r"\b(necesito|quiero)\b.*\b(cortarme|hacerme dano|autolesionarme)\b.*\b(sentir algo|calmarme|aguantar)",
        r"\b(no quiero estar aqui|me quiero ir para siempre|quiero irme para siempre|ya no quiero seguir|no pienso seguir|quiero desaparecer)\b",
        r"\b(no pienso|no quiero|no voy a|ojala no|ojal[aá] no)\b.*\b(despertar|levantarme)\b.*\b(mañana|manana|nunca|otra vez)\b",
        r"\b(hoy|esta noche|ahora)\b.*\b(despedirme de todos|me despido de todos|despedirme|decir adios|decir adiós)\b.*\b(luego hacerlo|despues hacerlo|después hacerlo|hacerlo)\b",
        r"\b(voy a|quiero|me voy a|pienso|necesito)\b.*\b(poner fin a esto|terminar con mi sufrimiento|terminar con esto|acabar con mi sufrimiento|terminar de una vez)\b",
        r"\b(esta es mi ultima noche|esta sera mi ultima noche|hoy es mi ultima noche|ultima noche)\b",
        r"\b(adios a todos|adiós a todos)\b.*\b(gracias por todo|perdon|lo siento)\b",
        r"\b(he repartido|voy a repartir|estoy repartiendo)\b.*\b(mis cosas|mis pertenencias|todo lo mio)\b",
        r"\b(necesito|quiero|voy a)\b.*\b(ver sangre|sangrar|hacerme sangrar)\b",
    ]
    matches = _match_regex(text, self_harm_patterns)
    if matches:
        return _result("crisis", "self_harm", "Ideación suicida o autolesiva explícita o altamente probable.", matches, False)

    overdose_patterns = [
        r"\b(tomar|tomarme|ingerir|tragar|tragarme|beber|beberme)\b.*\b(todas|muchas|un monton|demasiadas|varias|caja|bote|\d+)\b.*\b(pastillas|medicacion|medicamentos|ansioliticos|antidepresivos|ibuprofeno|paracetamol)",
        r"\b(tomar|tomarme|ingerir|tragar|tragarme|beber|beberme)\b.*\b(pastillas|medicacion|medicamentos|ansioliticos|antidepresivos|ibuprofeno|paracetamol)\b.*\b(todas|muchas|un monton|demasiadas|varias|caja|bote|\d+)",
        r"\b(tomar|tomarme|ingerir|tragar|tragarme|he tomado|me he tomado)\b.*\b\d+\b.*\b(pastillas|medicamentos|paracetamol|ibuprofeno|ansioliticos|antidepresivos)",
        r"\b(beber|beberme|he bebido|me he bebido|tomar|tomarme|ingerir|tragar|tragarme)\b.*\b(lejia|cloro|veneno|raticida|matarratas|amoniaco|salfuman|acido|gasolina|alcohol de quemar|anticongelante)",
        r"\b(inhalar|respirar|abrir|poner)\b.*\b(gas|monoxido|butano)",
        r"\b(sobredosis|overdose)\b",
        r"\b(mezclar|mezclarme|combinar|combinarme)\b.*\b(alcohol|cerveza|vodka|vino)\b.*\b(pastillas|medicacion|medicamentos|ansioliticos|antidepresivos|benzodiacepinas|somniferos)",
        r"\b(mezclar|mezclarme|combinar|combinarme)\b.*\b(pastillas|medicacion|medicamentos|ansioliticos|antidepresivos|benzodiacepinas|somniferos)\b.*\b(alcohol|cerveza|vodka|vino)",
        r"\b(tomar|tomarme|tragar|tragarme)\b.*\b(un bote entero|la caja entera|todo el bote|toda la caja|muchos somniferos|pastillas para dormir)",
        r"\b(coche|auto|vehiculo)\b.*\b(garaje|garage)\b.*\b(encendido|arrancado|escape|humo)",
        r"\b(coche|auto|vehiculo)\b.*\b(encendido|arrancado|escape|humo)\b.*\b(garaje|garage)",
        r"\b(monoxido|monoxido de carbono|humo del coche|tubo de escape|escape del coche|brasero|intoxicarme con humo|intoxicar con humo|asfixiarme con humo)\b",
        r"\b(intoxicarme|asfixiarme)\b.*\b(humo|gas|monoxido)",
        r"\b(dejar|dejare|voy a dejar)\b.*\b(brasero|calefactor|estufa|gas)\b.*\b(encendido|abierto)\b.*\b(dormir|no despertar)",
        r"\b(cerrar|cerrado|he cerrado|encerrarme|me encierro)\b.*\b(garaje|garage)\b.*\b(coche|auto|vehiculo)\b.*\b(arrancado|encendido|humo|escape)",
        r"\b(garaje|garage)\b.*\b(coche|auto|vehiculo)\b.*\b(arrancado|encendido|humo|escape)",
        r"\b(voy a|quiero|me voy a|pienso)\b.*\b(beber|tomar|ingerir|tragar)\b.*\b(lejia|lejía|veneno|raticida|matarratas|salfuman|salfumán|acido|ácido)",
    ]
    matches = _match_regex(text, overdose_patterns)
    if matches:
        return _result("crisis", "substance_or_overdose", "Riesgo de intoxicación, sobredosis o ingesta peligrosa.", matches, False)

    dangerous_behavior_patterns = [
        r"\b(saltar|tirar|tirarme|lanzar|lanzarme|arrojar|arrojarme|precipitar|precipitarme|brincar|caerme)\b.*\b(puente|ventana|balcon|azotea|tejado|precipicio|acantilado|terraza|barranco|vacio|cornisa|mirador|edificio|piso|decimo|noveno|octavo|septimo|sexto|quinto|cuarto|tercero|segundo)",
        r"\b(puente|ventana|balcon|azotea|tejado|precipicio|acantilado|terraza|barranco|vacio|cornisa|mirador|edificio|piso|decimo|noveno|octavo|septimo|sexto|quinto|cuarto|tercero|segundo)\b.*\b(saltar|tirar|tirarme|lanzar|lanzarme|arrojar|arrojarme|precipitar|precipitarme|brincar|caerme)",
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
        r"\b(tirar|tirarme|lanzar|lanzarme|arrojar|arrojarme|meter|meterme|entrar|entrarme|saltar|me tiro|me lanzo)\b.*\b(rio|mar|lago|pantano|embalse|canal|corriente|agua|presa|muelle|piscina)",
        r"\b(rio|mar|lago|pantano|embalse|canal|corriente|agua|presa|muelle|piscina)\b.*\b(tirar|tirarme|lanzar|lanzarme|arrojar|arrojarme|meter|meterme|entrar|saltar|me tiro|me lanzo|tragar|trague|traga|arrastrar|arrastre|llevar|lleve)",
        r"\b(ahogarme|ahogarse|asfixiarme|asfixiarse)\b",
        r"\b(dejarme|me voy a dejar|voy a dejarme)\b.*\b(llevar|arrastrar|tragar|trague|traga)\b.*\b(corriente|rio|mar|agua)",
        r"\b(no salir|no volver|desaparecer)\b.*\b(rio|mar|agua|corriente|lago|pantano|embalse|canal|piscina)",
        r"\b(nadar|irme nadando|me voy nadando|me voy a ir nadando|meterme en el agua)\b.*\b(hasta no poder volver|hasta cansarme|sin volver|y no volver)",
        r"\b(ya esta|no puedo mas|no aguanto mas|no veo salida|me da igual)\b.*\b(rio|mar|agua|corriente|ahogarme|tirarme|lanzarme)",
        r"\b(tirar|tirarme|lanzar|lanzarme|saltar|arrojar|arrojarme|precipitar|precipitarme)\b.*\b(edificio|piso|planta|mirador|muro alto|sitio alto|lugar alto)",
        r"\b(edificio|piso|planta|mirador|muro alto|sitio alto|lugar alto)\b.*\b(tirar|tirarme|lanzar|lanzarme|saltar|arrojar|arrojarme|precipitar|precipitarme)",
        r"\b(sentarse|sentarme|tumbarme|dormir|dormirme|ponerme)\b.*\b(vias|via del tren|vias del tren|tren|metro)",
        r"\b(tirarme|lanzarme|ponerme|meterme|tumbarme|sentarme)\b.*\b(carretera|autopista|autovia|calzada|trafico|camion|coche|bus)",
        r"\b(electrocutarme|meter los dedos en el enchufe|tocar cables pelados|meterme en cables|tostadora en la bañera|tostadora en la banera|bañera con electricidad|banera con electricidad)\b",
        r"\b(meter|meterme|poner|ponerme|atar|atarme)\b.*\b(bolsa|plastico)\b.*\b(cabeza|cara|cuello|respirar|asfixiarme)",
        r"\b(asfixiarme|asfixiar)\b.*\b(bolsa|plastico|cabeza)",
        r"\b(meter|meterme|poner|ponerme|atar|atarme)\b.*\b(cabeza|cara)\b.*\b(bolsa|plastico)",
        r"\b(subo|subirme|me subo|ponerme|me voy a poner)\b.*\b(cornisa|borde de la azotea|borde del balcon|borde del puente|borde)",
        r"\b(estampar|estamparme|chocar|chocarme|provocar un accidente|causar un accidente)\b.*\b(coche|moto|vehiculo|muro|arbol|carretera)",
        r"\b(voy a provocar|quiero provocar|provocare|causare|voy a causar)\b.*\b(accidente|choque)",
        r"\b(saltar|tirarme|lanzarme|meterme|ponerme)\b.*\b(trafico|transito|coches|camiones|calzada)",
        r"\b(abrir el gas|dejar el gas abierto|encender el gas)\b.*\b(encerrado|encerrada|habitacion|cocina|casa|dormir|no despertar)",
        r"\b(he puesto|me he puesto|me puse|ponerme|poner|atar|atarme)\b.*\b(bolsa|plastico|plástico)\b.*\b(cabeza|cara|cuello)",
        r"\b(he puesto|me he puesto|me puse|ponerme|poner|atar|atarme)\b.*\b(cabeza|cara|cuello)\b.*\b(bolsa|plastico|plástico)",
        r"\b(acercar|acercarme|asomar|asomarme|ponerme|sentarme|estar)\b.*\b(borde|cornisa)\b.*\b(barranco|azotea|balcon|balcón|puente|precipicio|acantilado|ventana)",
        r"\b(borde|cornisa)\b.*\b(barranco|azotea|balcon|balcón|puente|precipicio|acantilado|ventana)\b.*\b(ya vere|ya veré|a ver que pasa|me da igual|no me importa|no puedo mas|no aguanto mas)",
        r"\b(no quiero seguir|no puedo mas|no aguanto mas|ya esta|se acabo|me rindo)\b.*\b(voy|me voy|ire|iré)\b.*\b(rio|río|mar|lago|pantano|embalse|canal|corriente|agua)",
        r"\b(caminar|andar|irme|meterme|entrar)\b.*\b(mar|rio|río|lago|agua)\b.*\b(hasta perderme|hasta no volver|sin volver|de noche|y que pase lo que tenga que pasar)",
        r"\b(quedarme|quedar|permanecer)\b.*\b(bajo el agua|debajo del agua|sumergido|sumergida)",
        r"\b(hundirme|sumergirme)\b.*\b(rio|río|mar|lago|agua|pantano|embalse)",
        r"\b(asomarme|me asomo|asomar)\b.*\b(ventana|balcon|balcón|azotea|terraza)\b.*\b(no pienso volver atras|no pienso volver atrás|no volver|me da igual)",
        r"\b(quiero|voy a|me voy a|pienso)\b.*\b(caer|lanzarme|tirarme)\b.*\b(desde muy alto|de muy alto|lugar alto|sitio alto)",
        r"\b(voy a|quiero|me voy a|pienso)\b.*\b(soltar el volante|quitar las manos del volante|cerrar los ojos conduciendo)",
        r"\b(voy a|quiero|me voy a|pienso)\b.*\b(aguantar la respiracion|aguantar la respiración|dejar de respirar)\b.*\b(hasta no poder mas|hasta no poder más|hasta desmayarme|hasta perder el conocimiento)",
        r"\b(voy a|quiero|me voy a|pienso|necesito)\b.*\b(dejar de respirar|no respirar)\b",
    ]
    matches = _match_regex(text, dangerous_behavior_patterns)
    if matches:
        return _result("crisis", "dangerous_behavior", "Conducta física peligrosa o ambigua con riesgo inmediato.", matches, False)

    harm_to_others_patterns = [
        r"\b(quiero|voy a|me voy a|pienso|he decidido|tengo ganas de|estoy pensando en)\b.*\b(matar|asesinar|hacer una masacre|masacre|hacer dano|hacerle dano|danar|atacar|apuñalar|apunalar|disparar|pegar|pegarle|dar una paliza|darle una paliza|quemar|envenenar|empujar)\b",
        r"\b(matar|asesinar|apuñalar|apunalar|disparar|atacar|pegarle|darle una paliza|dar una paliza)\b.*\b(a mi|a alguien|a mi hermano|a mi hermana|a mi madre|a mi padre|a mi pareja|a mi familia|a mis vecinos|a mi jefe|a un companero|a una persona)",
        r"\b(voy a pegarle|quiero pegarle|voy a darle una paliza|quiero darle una paliza|quiero reventarle la cara|voy a reventarle la cara)\b.*\b(a mi|a alguien|a mi hermano|a mi hermana|a mi madre|a mi padre|a mi pareja|a mi familia|a mis vecinos|a mi jefe|a un companero|a una persona)?",
        r"\b(vengarme|venganza)\b.*\b(hacer dano|danar|matar|atacar|pegar|paliza)",
        r"\b(voy con|llevo|voy a llevar|he cogido|tengo)\b.*\b(cuchillo|navaja|pistola|arma|bate)\b.*\b(instituto|colegio|universidad|trabajo|oficina|casa de|calle|clase)",
        r"\b(poner|poner una|voy a poner|fabricar|explotar)\b.*\b(bomba|explosivo)",
        r"\b(quemar|incendiar|prender fuego)\b.*\b(casa|coche|oficina|colegio|instituto|trabajo|persona|gente)",
        r"\b(envenenar|echar veneno|poner veneno)\b.*\b(jefe|pareja|familia|vecino|vecina|comida|bebida|alguien)",
        r"\b(empujar|tirar)\b.*\b(a alguien|a una persona|a mi jefe|a mi pareja)\b.*\b(vias|tren|metro|carretera|balcon|puente)",
        r"\b(voy a ir|ire|iré|me presentare|me presentaré|aparecere|apareceré)\b.*\b(trabajo|clase|instituto|colegio|universidad|oficina)\b.*\b(con|llevando)\b.*\b(cuchillo|navaja|pistola|arma|bate)",
        r"\b(voy a|quiero|me voy a|pienso)\b.*\b(hacer explotar|explotar|poner una bomba|detonar|volar)\b.*\b(colegio|instituto|universidad|oficina|trabajo|casa|edificio|clase)",
        r"\b(voy a|quiero|me voy a|pienso)\b.*\b(atropellar|arrollar)\b.*\b(a alguien|a una persona|a la gente)",
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
        r"\b(la ia|el algoritmo|internet)\b.*\b(me manda mensajes|me envia mensajes|me habla|me da señales|me da senales)",
        r"\b(oigo|escucho)\b.*\b(voces|susurros)\b.*\b(insultan|amenazan|persiguen|controlan)",
        r"\b(los extraterrestres|extraterrestres|alienigenas|aliens)\b.*\b(me hablan|me mandan mensajes|me envian señales|me envian senales|me controlan)",
        r"\b(veo|estoy viendo)\b.*\b(gente|personas|figuras|sombras)\b.*\b(que nadie mas ve|que nadie más ve|que otros no ven)",
        r"\b(hay|veo)\b.*\b(sombras|figuras)\b.*\b(en mi cuarto|en mi habitacion|en mi habitación|en casa|al lado de mi cama)",
    ]
    matches = _match_regex(text, psychotic_patterns)
    if matches:
        return _result("high", "psychotic_symptoms", "Indicadores de posible pérdida de contacto con la realidad o síntomas psicóticos.", matches, False)

    delusion_paranoia_patterns = [
        r"\b(vecinos|policia|gobierno|familia|compañeros|companeros|jefe|empresa|todos|alguien|movil|telefono)\b.*\b(me vigilan|me vigila|me espian|me espia|me controlan|me controla|me persiguen|me persigue|me siguen|me sigue|conspiran|me quieren envenenar|me quiere envenenar|quieren envenenarme|quiere envenenarme|me quieren hacer dano|me quiere hacer dano)",
        r"\b(me vigilan|me vigila|me espian|me espia|me estan vigilando|me estan espiando|vigilandome|espiandome|me persiguen|me siguen|me sigue)\b",
        r"\b(el gobierno|la policia|mis vecinos|mi familia)\b.*\b(me sigue|me siguen|me vigila|me vigilan|me controla|me controlan|me espia|me espian)",
        r"\b(camaras ocultas|microfonos ocultos|microfonos en casa|me han puesto microfonos|me han puesto un chip|tengo un chip|chip en la cabeza)",
        r"\b(camaras|camara)\b.*\b(vigilandome|espiandome|observandome|en mi casa|en mi habitacion)",
        r"\b(camaras|camara)\b.*\b(me miran|me vigilan|me observan|me espian)",
        r"\b(me controlan la mente|me leen la mente|leen mis pensamientos|la gente puede leer mi mente|control mental|me controlan por el movil|me controlan desde el movil|me controla el movil|me controla desde el movil|el movil me controla|mi movil me controla|mi movil me escucha y me persigue)",
        r"\b(hombres de negro|personas desconocidas|gente extraña|gente extrana)\b.*\b(me siguen|me persiguen|me vigilan|siguiendo)",
        r"\b(me estan siguiendo|me siguen|me persiguen|me vigilan)\b.*\b(hombres de negro|personas desconocidas|gente extraña|gente extrana)",
        r"\b(me quieren envenenar|me quiere envenenar|quieren envenenarme|quiere envenenarme|mi comida esta envenenada)",
        r"\b(satelites|drones|antenas|5g)\b.*\b(me vigilan|me controlan|me espian|me siguen|leen mi mente|leen mis pensamientos)",
        r"\b(me han implantado|me implantaron|tengo implantado)\b.*\b(chip|dispositivo|microchip)",
        r"\b(hackean|hackearon|controlan)\b.*\b(mi cerebro|mi mente|mis pensamientos)",
        r"\b(todos estan contra mi|todo el mundo esta contra mi)\b.*\b(conspiracion|conspiran|me persiguen|me quieren hacer dano)",
        r"\b(vecinos|policia|gobierno|familia|alguien)\b.*\b(han puesto|pusieron|instalaron|me pusieron)\b.*\b(microfonos|microfono|camaras|camara)\b.*\b(casa|habitacion|piso)",
        r"\b(me estan leyendo|me leen|leen)\b.*\b(mente|pensamientos)\b.*\b(antena|antenas|5g|satelite|satelites|dron|drones)",
        r"\b(antena|antenas|5g|satelite|satelites|dron|drones)\b.*\b(me lee|me leen|me estan leyendo|lee mi mente|leen mi mente|leen mis pensamientos)",
        r"\b(gobierno|policia|policía|servicios secretos|cia|fbi)\b.*\b(me esta siguiendo|me está siguiendo|me estan siguiendo|me están siguiendo|me vigila|me vigilan|me controla|me controlan)",
        r"\b(me han puesto|han puesto|instalaron|han instalado)\b.*\b(camaras|cámaras|camara|cámara|microfonos|micrófonos)\b.*\b(baño|bano|ducha|habitacion|habitación|casa|piso)",
        r"\b(me estan controlando|me están controlando|me controlan|me controla)\b.*\b(ondas|wifi|wi fi|internet|radiofrecuencia|antenas|5g)",
        r"\b(hay|tengo)\b.*\b(chip|microchip|dispositivo)\b.*\b(brazo|mano|cuerpo|piel|cabeza)",
        r"\b(tele|television|televisión|tv|radio)\b.*\b(me manda|me envia|me envía|me habla)\b.*\b(señales|senales|mensajes|ordenes|órdenes)",
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
        r"\b(he dejado|deje|dejé|voy a dejar|dejo)\b.*\b(medicacion|medicación|medicamento|pastillas|antidepresivo|ansiolitico|ansiolítico|tratamiento)\b.*\b(me controla|me controlan|porque me controla|porque me controlan)",
        r"\b(me voy a tomar|voy a tomar|tomare|tomaré|quiero tomar)\b.*\b(doble|el doble|dos veces|mas|más)\b.*\b(medicacion|medicación|medicamento|pastillas|dosis|antidepresivo|ansiolitico|ansiolítico)",
    ]
    matches = _match_regex(text, medical_patterns)
    if matches:
        return _result("high", "medical_or_clinical_advice", "Solicitud de diagnóstico, medicación o modificación de tratamiento.", matches, False)

    # Fallback contextual: combina desesperanza/finalidad con medios o lugares peligrosos.
    # Esto reduce falsos negativos ante frases que no usan las expresiones exactas anteriores.
    finality_or_despair_patterns = [
        r"\b(ya esta|se acabo|hasta aqui|no puedo mas|no aguanto mas|no veo salida|me rindo|me despido|adios a todos|adiós a todos|perdonadme por todo|no vais a volver a verme|esta noche termina todo|hoy termina todo|hoy se acaba todo|ultima noche|última noche|poner fin|terminar con mi sufrimiento|hacer algo malo|no respondo de mis actos|hacer una tonteria|hacer una tontería)\b",
    ]
    danger_context_patterns = [
        r"\b(rio|río|mar|lago|pantano|embalse|canal|corriente|agua|puente|ventana|balcon|balcón|azotea|tejado|edificio|piso|tren|metro|vias|vías|carretera|autopista|coche|camion|camión|gas|monoxido|monóxido|pastillas|medicacion|medicación|cuchillo|navaja|cuerda|soga|arma|pistola|veneno|lejia|lejía|cloro|garaje|garage|volante|bolsa|plastico|plástico)\b",
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
        r"\b(no vais a volver a verme|perdonadme por todo|gracias por todo y adios|gracias por todo y adiós|adios a todos gracias por todo|adiós a todos gracias por todo|me despido de todos|esta es mi despedida|esta noche termina todo|hoy termina todo|hoy se acaba todo|nota de despedida|carta de despedida|si mañana no estoy|si manana no estoy|esta es mi ultima noche|esta es mi última noche)\b",
    ]
    matches = _match_regex(text, farewell_patterns)
    if matches:
        return _result("crisis", "self_harm", "Mensaje de despedida o finalidad con posible riesgo autolesivo.", matches, False)

    ambiguous_high_risk_patterns = [
        r"\b(voy a hacer una locura|voy a cometer una locura|voy a hacer una estupidez|voy a hacer algo irreversible|voy a hacer algo de lo que me arrepentire|voy a hacer algo de lo que me arrepentiré|voy a hacer algo malo|no respondo de mis actos|puede que hoy haga una tonteria|puede que hoy haga una tontería)\b",
    ]
    matches = _match_regex(text, ambiguous_high_risk_patterns)
    if matches:
        return _result("high", "unknown_high_risk", "Amenaza ambigua de acción peligrosa o irreversible.", matches, False)

    severe_distress_patterns = [
        r"\b(no puedo mas|no aguanto mas|no aguanto|estoy desesperado|estoy desesperada|todo me supera|no veo salida|me siento atrapado|me siento atrapada|me siento roto|me siento rota)",
        r"\b(no puedo seguir asi|esto es insoportable|no se que hacer con mi vida|estoy fatal no aguanto|voy a hacer una locura|voy a cometer una locura|voy a hacer una estupidez)",
    ]
    matches = _match_regex(text, severe_distress_patterns)
    if matches:
        return _result("medium", "emotional_distress", "Malestar emocional intenso sin plan explícito de daño.", matches, True)

    return _result("low", "normal", "Sin señales de riesgo relevantes.", [], True)
