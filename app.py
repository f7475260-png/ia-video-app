import streamlit as st
from moviepy.editor import TextClip, CompositeVideoClip
from gtts import gTTS
from PIL import Image
import os

st.title("🎬 Générateur de vidéo IA – Style InVideo")

# 1. Texte utilisateur
script = st.text_area("✏️ Entrez votre script ici :")

# 2. Choix de voix
language = st.selectbox("🗣️ Choisissez la langue de la voix", ["fr", "en", "es", "de"])

# 3. Image de fond (optionnelle)
uploaded_image = st.file_uploader("📷 Ajoutez une image de fond (facultatif)", type=["jpg", "png"])

# 4. Génération audio
if script and st.button("🎤 Générer voix et vidéo"):
    tts = gTTS(text=script, lang=language)
    tts.save("voice.mp3")

    clip = TextClip(script, fontsize=50, color='white', bg_color='black', size=(1280, 720)).set_duration(10)

    if uploaded_image:
        bg_image = Image.open(uploaded_image).resize((1280, 720))
        bg_image.save("bg.png")
        image_clip = ImageClip("bg.png").set_duration(10)
        video = CompositeVideoClip([image_clip, clip.set_position("center")])
    else:
        video = clip

    video.write_videofile("final_video.mp4", fps=24)
    st.video("final_video.mp4")

    st.success("✅ Vidéo générée avec succès !")
