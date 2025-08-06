import openai
import requests
from gtts import gTTS
from moviepy.editor import *
import streamlit as st
import os

# Clés API
OPENAI_API_KEY = "TA_CLE_OPENAI"
INVIDEO_API_KEY = "TA_CLE_INVIDEO"  # Si tu as accès à leur API privée

openai.api_key = OPENAI_API_KEY

st.title("🎥 Générateur Ultra IA – Niveau Pro")

# 1. Entrée utilisateur
topic = st.text_input("🎯 Sujet de la vidéo")

# 2. Choix de la voix
voice_lang = st.selectbox("🗣️ Langue de la voix", ["fr", "en", "es", "de"])

if st.button("🚀 Générer la vidéo"):
    # 🔥 GPT – Génération du script vidéo
    prompt = f"Génère un script vidéo YouTube percutant et informatif sur le thème '{topic}'"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    video_script = response['choices'][0]['message']['content']
    st.text_area("📝 Script généré :", value=video_script, height=300)

    # 🎙️ Génération audio
    tts = gTTS(text=video_script, lang=voice_lang)
    tts.save("voice.mp3")

    # 🖼️ DALL·E – Génération d'image
    dalle_prompt = f"Image d'illustration stylée pour une vidéo sur : {topic}"
    dalle_response = openai.Image.create(prompt=dalle_prompt, n=1, size="1280x720")
    img_url = dalle_response['data'][0]['url']
    img_data = requests.get(img_url).content
    with open("image.png", "wb") as f:
        f.write(img_data)

    # 🎬 Composition vidéo
    image_clip = ImageClip("image.png").set_duration(20)
    audio_clip = AudioFileClip("voice.mp3")
    final_video = image_clip.set_audio(audio_clip)

    # 🧨 Export
    final_video.write_videofile("output_pro.mp4", fps=24)
    st.video("output_pro.mp4")

    # 🚀 Option : Envoi direct vers InVideo (si accès API)
    # headers = {"Authorization": f"Bearer {INVIDEO_API_KEY}"}
    # files = {"file": open("output_pro.mp4", "rb")}
    # requests.post("https://api.invideo.io/videos", headers=headers, files=files)

    st.success("✅ Vidéo générée et prête à être publiée !")

