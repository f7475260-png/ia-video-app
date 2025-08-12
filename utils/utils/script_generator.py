import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_API_URL = os.getenv("HF_API_URL", "https://api-inference.huggingface.co/models")
HF_MODEL_ID = os.getenv("HF_MODEL_ID", "gpt2")
HF_KEY = os.getenv("HUGGINGFACE_API_KEY")
HEADERS = {"Authorization": f"Bearer {HF_KEY}"} if HF_KEY else {}

def _fallback_script(theme: str, language: str) -> str:
    if language == "fr":
        return (
            f"Bienvenue dans cette vidéo sur {theme}. "
            "Aujourd’hui, on explore l’essentiel en 60 secondes : idées clés, conseils pratiques, et un final inspirant. "
            "Reste jusqu’au bout pour l’astuce bonus !"
        )
    return (
        f"Welcome to this short video about {theme}. "
        "In 60 seconds, we’ll cover the essentials, practical tips, and a quick inspiring takeaway. "
        "Stay to the end for a bonus tip!"
    )

def generate_script(theme: str, language: str = "fr") -> str:
    prompt = (
        f"Écris un script concis et percutant (120 à 180 mots) en {language} "
        f"pour une vidéo d'une minute sur le thème: {theme}. "
        "Structure: accroche, 3 points clés, conclusion motivante. Style clair, dynamique."
    )
    if not HF_KEY:
        return _fallback_script(theme, language)

    url = f"{HF_API_URL.rstrip('/')}/{HF_MODEL_ID}"
    try:
        resp = requests.post(url, headers=HEADERS, json={"inputs": prompt}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and data and "generated_text" in data[0]:
            return data[0]["generated_text"]
        if isinstance(data, dict) and "generated_text" in data:
            return data["generated_text"]
        return _fallback_script(theme, language)
    except Exception:
        return _fallback_script(theme, language)
