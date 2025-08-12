import os
import uuid
from gtts import gTTS

LANG_MAP = {"fr": "fr", "en": "en"}

def generate_voiceover(text: str, language: str = "fr") -> str:
    lang = LANG_MAP.get(language, "fr")
    os.makedirs("output", exist_ok=True)
    out_path = os.path.join("output", f"voice_{uuid.uuid4().hex}.mp3")
    tts = gTTS(text=text, lang=lang)
    tts.save(out_path)
    return out_path
