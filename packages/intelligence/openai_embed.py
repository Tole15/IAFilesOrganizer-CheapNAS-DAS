import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def embed_text(text: str, model: str) -> list[float]:
    # recorta por seguridad (evita textos gigantes)
    text = text.strip()
    if len(text) > 20000:
        text = text[:20000]

    resp = client.embeddings.create(
        model=model,
        input=text
    )
    return resp.data[0].embedding