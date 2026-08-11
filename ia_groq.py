"""
Modulo compartido para llamar a la IA de Groq (gratuita) desde los tres
lugares que la usan: avance_infante, avance_alumno y actividades_postcrisis.

Requiere la variable de entorno GROQ_API_KEY (console.groq.com/keys).
Si la key no esta configurada, o la llamada falla por cualquier razon
(limite de uso, red, modelo caido, etc.), generar_texto_ia devuelve None
para que el que la llama use su propio texto de respaldo basado en reglas.
La pagina NUNCA debe tronar ni mostrar un error por culpa de la IA.

Este archivo va en la RAIZ del repo (junto a app.py), no dentro de un modulo.
"""
import os

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
MODELO_GROQ = "openai/gpt-oss-120b"
MODELO_GROQ_RESPALDO = "llama-3.1-8b-instant"


def generar_texto_ia(prompt, system=None, max_tokens=900):
    if not GROQ_API_KEY:
        return None
    try:
        from groq import Groq
        cliente = Groq(api_key=GROQ_API_KEY)
        mensajes = []
        if system:
            mensajes.append({"role": "system", "content": system})
        mensajes.append({"role": "user", "content": prompt})
        for modelo in (MODELO_GROQ, MODELO_GROQ_RESPALDO):
            try:
                respuesta = cliente.chat.completions.create(
                    model=modelo,
                    messages=mensajes,
                    temperature=0.6,
                    max_tokens=max_tokens,
                )
                texto = (respuesta.choices[0].message.content or "").strip()
                if texto:
                    return texto
            except Exception:
                continue
        return None
    except Exception:
        return None