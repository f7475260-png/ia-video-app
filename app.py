import streamlit as st
from gtts import gTTS
from moviepy.editor import *
import tempfile
import os

st.title("🗣️ Générateur Vidéo Simple")

text = st.text_input("Texte à lire en vidéo")

if st.button("🎬 Générer"):
    if text.strip() == "":
        st.error("Merci d'écrire un texte.")
    else:
        # Génération audio
        tts = gTTS(text)
        audio_path = tempfile.mktemp(suffix=".mp3")
        tts.save(audio_path)

        # Clip vidéo noir avec audio
        clip = ColorClip(size=(1280, 720), color=(0, 0, 0), duration=5)
        clip = clip.set_audio(AudioFileClip(audio_path))
        video_path = tempfile.mktemp(suffix=".mp4")
        clip.write_videofile(video_path, codec="libx264", audio_codec="aac")

        st.success("✅ Vidéo générée !")
        st.video(video_path)

