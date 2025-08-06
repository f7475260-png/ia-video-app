import streamlit as st
from gtts import gTTS
from moviepy.editor import *
from PIL import Image
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

# === UTILITAIRES ===
def load_credits():
    if not os.path.exists(CREDIT_FILE):
        data = {"short": {"used":0,"last_reset":str(datetime.now())},
                "long": {"used":0,"last_reset":str(datetime.now())}}
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

def generate_voice(text):
    tts = gTTS(text)
    path = tempfile.mktemp(suffix=".mp3")
    tts.save(path)
    return path

# === INTERFACE STREAMLIT ===
st.set_page_config("streamlit_app", layout="centered")
st.title("🎬 Vidéo scène par scène (test default image)")

credits = reset_credits(load_credits())
remaining_short = SHORT_MAX_CREDITS - credits["short"]["used"]
remaining_long = LONG_MAX_CREDITS - credits["long"]["used"]

st.markdown(f"**Courtes (<1 min)**: {remaining_short}/{SHORT_MAX_CREDITS}   \n**Longues (<10 min)**: {remaining_long}/{LONG_MAX_CREDITS}")

text_input = st.text_area("Entrez votre script (phrases séparées par des points)")
video_type = st.radio("Type vidéo :", ["Courte (<1 min)", "Longue (<10 min)"])
if st.button("Générer vidéo"):
    scenes = split_text(text_input)
    total_duration = 0
    clips = []
    quota = "short" if video_type.startswith("Courte") else "long"
    max_dur = SHORT_MAX_DURATION if quota=="short" else LONG_MAX_DURATION
    limit = SHORT_MAX_CREDITS if quota=="short" else LONG_MAX_CREDITS

    if credits[quota]["used"] >= limit:
        st.error("Quota épuisé.")
    else:
        for i, scene in enumerate(scenes):
            try:
                voice = generate_voice(scene)
                audio = AudioFileClip(voice)
                if total_duration + audio.duration > max_dur:
                    st.warning("Durée max atteinte.")
                    break

                img_clip = ImageClip("default.jpg").set_duration(audio.duration)
                img_clip = img_clip.set_audio(audio).set_fps(24)
                txt = TextClip(scene, fontsize=40, color="white", bg_color="black", size=(1280, 100))
                txt = txt.set_duration(audio.duration).set_position(("center","bottom"))
                clip = CompositeVideoClip([img_clip, txt]).fadein(0.5).fadeout(0.5)
                clips.append(clip)
                total_duration += audio.duration
            except Exception as e:
                st.error(f"Erreur scène {i+1}: {e}")

        if clips:
            video = concatenate_videoclips(clips, method="compose", padding=-0.5)
            path = tempfile.mktemp(suffix=".mp4")
            video.write_videofile(path, codec="libx264", audio_codec="aac")
            st.video(path)
            credits[quota]["used"] += 1
            save_credits(credits)
        else:
            st.error("Aucune scène valide générée.")
