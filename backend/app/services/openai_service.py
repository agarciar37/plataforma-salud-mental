from openai import OpenAI
from app.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_chat_response(user_message: str, emotion: str) -> str:
    system_prompt = (
        "Eres un asistente de apoyo emocional. "
        "Debes responder con empatía, claridad y tono calmado. "
        "No debes diagnosticar ni sustituir ayuda profesional. "
        "Si detectas malestar, ofrece orientación general y recomendaciones breves de bienestar. "
        f"El estado emocional detectado del usuario es: {emotion}."
    )

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.7,
        max_tokens=300,
    )

    return response.choices[0].message.content or "No he podido generar una respuesta en este momento."