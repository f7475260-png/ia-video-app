import streamlit as st
from gtts import gTTS
from moviepy.editor import *
from PIL import Image
import requests
import tempfile
import os
import json
from datetime import datetime, timedelta

# === QUOTAS ===
SHORT_MAX_DURATION = 60
SHORT_MAX_CREDITS = 5
SHORT_RESET_DAYS = 14

LONG_MAX_DURATION = 600
LONG_MAX_CREDITS = 1
LONG_RESET_DAYS = 30
CREDIT_FILE = "credits.json"

# === UTILS ===
def load_credits():
    if not os.path.exists(CREDIT_FILE):
        data = {
            "short": {"used": 0, "last_reset": str(datetime.now())},
            "long": {"used": 0, "last_reset": str(datetime.now())}
        }
        with open(CREDIT_FILE, "w") as f:
            json.dump(data, f)
        return data
    with open(CREDIT_FILE, "r") as f:
        return json.load(f)

def save_credits(data):
    with open(CREDIT_FILE, "w") as f:
        json.dump(data, f)

def reset_credits(data):
    now = datetime.now()
    for key, days in [("short", SHORT_RESET_DAYS), ("long", LONG_RESET_DAYS)]:
        last = datetime.fromisoformat(data[key]["last_reset"])
        if now - last > timedelta(days=days):
            data[key]["used"] = 0
            data[key]["last_reset"] = str(now)
    return data

def split_text(text):
    return [s.strip() for s in text.replace("\n", ". ").split(". ") if s.strip()]

def generate_image(prompt):
    try:
        url = f"https://lexica.art/api/v1/search?q={prompt}"
        r = requests.get(url).json()
        img_url = r["images"][0]["srcSmall"]
        img_data = requests.get(img_url).content
        path = tempfile.mktemp(suffix=".jpg")
        with open(path, "wb") as f:
            f.write(img_data)
        return path
    except:
        return None

def generate_voice(text):
    tts = gTTS(text)
    path = tempfile.mktemp(suffix=".mp3")
    tts.save(path)
    return path

# === UI ===
st.set_page_config("IA Multi-Scène Vidéo", layout="centered")
st.title("🎨 IA Vidéo Multi-Scènes (style InVideo)")

credits = reset_credits(load_credits())
remaining_short = SHORT_MAX_CREDITS - credits["short"]["used"]
remaining_long = LONG_MAX_CREDITS - credits["long"]["used"]

st.markdown(f"""
**🔵 Vidéos courtes (<1 min)** : `{remaining_short}/{SHORT_MAX_CREDITS}`  
**🔶 Vidéos longues (<10 min)** : `{remaining_long}/{LONG_MAX_CREDITS}`
""")

text_input = st.text_area("✍️ Entre ton script (chaque phrase = une scène)")
video_type = st.radio("Type de vidéo :", ["📌 Courte (<1 min)", "📺 Longue (<10 min)"])
start = st.button("🎬 Générer vidéo multi-scène")

if start:
    if not text_input.strip():
        st.warning("Entrez du texte.")
    else:
        scenes = split_text(text_input)
        clips = []
        total_duration = 0
        quota_type = "short" if video_type.startswith("📌") else "long"
        max_duration = SHORT_MAX_DURATION if quota_type == "short" else LONG_MAX_DURATION
        quota_limit = SHORT_MAX_CREDITS if quota_type == "short" else LONG_MAX_CREDITS

        if credits[quota_type]["used"] >= quota_limit:
            st.error(f"Quota de vidéo {quota_type} épuisé.")
        else:
            st.info(f"🎥 Génération de {len(scenes)} scènes...")
            for i, scene in enumerate(scenes):
                try:
                    st.write(f"🧠 Scène {i+1} : {scene[:60]}...")
                    voice = generate_voice(scene)
                    audio = AudioFileClip(voice)

                    if total_duration + audio.duration > max_duration:
                        st.warning("⏱️ Durée max atteinte. Arrêt de la génération.")
                        break

                    img = generate_image(scene) or "default.jpg"
                    img_clip = ImageClip(img).set_duration(audio.duration).set_audio(audio).set_fps(24)

                    txt = TextClip(scene, fontsize=40, color="white", bg_color="black", size=(1280, 100))
                    txt = txt.set_duration(audio.duration).set_position(("center", "bottom"))

                    final = CompositeVideoClip([img_clip, txt])
                    final = final.fadein(0.5).fadeout(0.5)
                    clips.append(final)
                    total_duration += audio.duration

                except Exception as e:
                    st.warning(f"❌ Erreur scène {i+1}: {e}")
                    continue

            if clips:
                video = concatenate_videoclips(clips, method="compose", padding=-0.5)
                path = tempfile.mktemp(suffix=".mp4")
                video.write_videofile(path, codec="libx264", audio_codec="aac")

                st.success("✅ Vidéo générée !")
                st.video(path)

                credits[quota_type]["used"] += 1
                save_credits(credits)
            else:
                st.error("Aucune scène valide n’a pu être générée.")
