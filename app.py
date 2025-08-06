import streamlit as st
import cv2
import numpy as np
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
from gtts import gTTS
from PIL import Image

st.title("🎬 Générateur IA de vidéo simplifiée")

# 1. Texte utilisateur
script = st.text_area("📝 Écris ton script ici")

# 2. Langue de synthèse vocale
lang = st.selectbox("🌍 Choisis la langue de la voix", ["fr", "en", "es", "de"])

# 3. Image de fond
uploaded_img = st.file_uploader("🖼️ Ajoute une image de fond", type=["jpg", "png"])

if script and st.button("🎥 Générer la vidéo"):
    # Génération audio avec gTTS
    tts = gTTS(text=script, lang=lang)
    tts.save("voice.mp3")

    # Générer une image texte avec OpenCV
    image = np.zeros((720, 1280, 3), dtype=np.uint8)
    image[:] = (0, 0, 0)  # fond noir

    font = cv2.FONT_HERSHEY_SIMPLEX
    wrapped_text = script[:200] + "..." if len(script) > 200 else script
    cv2.putText(image, wrapped_text, (50, 360), font, 1.2, (255, 255, 255), 2, cv2.LINE_AA)

    # Sauver l’image
    cv2.imwrite("frame.png", image)

    # Charger l’image + audio dans MoviePy
    img_clip = ImageClip("frame.png").set_duration(10)
    audio_clip = AudioFileClip("voice.mp3")
    final = img_clip.set_audio(audio_clip)

    # Exporter la vidéo
    final.write_videofile("final_output.mp4", fps=24)
    st.video("final_output.mp4")
    st.success("✅ Vidéo créée avec succès !")
