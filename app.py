import streamlit as st
from gtts import gTTS
from moviepy.editor import *
import requests
import tempfile
import os

# === UTILS ===

def split_text(text):
    # Découpe texte en scènes à chaque phrase
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
    except Exception as e:
        print("Erreur génération image:", e)
        return None

def generate_voice(text):
    tts = gTTS(text)
    path = tempfile.mktemp(suffix=".mp3")
    tts.save(path)
    return path

# === UI ===

st.set_page_config("IA Multi-Scène Vidéo", layout="centered")
st.title("🎨 IA Vidéo Multi-Scènes (style InVideo)")

text_input = st.text_area("✍️ Entre ton script (chaque phrase = une scène)")

start = st.button("🎬 Générer vidéo multi-scène")

if start:
    if not text_input.strip():
        st.warning("Entrez du texte.")
    else:
        scenes = split_text(text_input)
        clips = []
        total_duration = 0
        max_duration = 600  # 10 minutes max (sans quota)

        st.info(f"🎥 Génération de {len(scenes)} scènes...")

        for i, scene in enumerate(scenes):
            try:
                st.write(f"🧠 Scène {i+1} : {scene[:60]}...")

                voice_path = generate_voice(scene)
                audio = AudioFileClip(voice_path)

                if total_duration + audio.duration > max_duration:
                    st.warning("⏱️ Durée max atteinte. Arrêt de la génération.")
                    break

                img_path = generate_image(scene)
                if img_path is None:
                    st.warning(f"⚠️ Image non trouvée pour la scène {i+1}, fond noir utilisé.")
                    img_clip = ColorClip(size=(1280, 720), color=(0, 0, 0), duration=audio.duration)
                else:
                    img_clip = ImageClip(img_path).set_duration(audio.duration)

                img_clip = img_clip.set_audio(audio).set_fps(24)

                # Texte sur la vidéo
                txt = TextClip(scene, fontsize=40, color="white", bg_color="black", size=(1280, 100))
                txt = txt.set_duration(audio.duration).set_position(("center", "bottom"))

                final_clip = CompositeVideoClip([img_clip, txt]).fadein(0.5).fadeout(0.5)
                clips.append(final_clip)

                total_duration += audio.duration

            except Exception as e:
                st.warning(f"❌ Erreur scène {i+1}: {e}")
                continue

        if clips:
            video = concatenate_videoclips(clips, method="compose", padding=-0.5)
            video.fps = 24  # très important !
            video_path = tempfile.mktemp(suffix=".mp4")
            video.write_videofile(video_path, codec="libx264", audio_codec="aac")

            st.success("✅ Vidéo générée !")
            st.video(video_path)
        else:
            st.error("Aucune scène valide n’a pu être générée.")
