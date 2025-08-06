import streamlit as st
from gtts import gTTS
from moviepy.editor import *
import requests
import tempfile

FPS = 24
MAX_DURATION_SHORT = 60
MAX_DURATION_LONG = 600

def fetch_image(prompt):
    try:
        url = f"https://lexica.art/api/v1/search?q={prompt}"
        response = requests.get(url).json()
        img_url = response["images"][0]["srcSmall"]
        img_data = requests.get(img_url).content
        tmp_path = tempfile.mktemp(suffix=".jpg")
        with open(tmp_path, "wb") as f:
            f.write(img_data)
        return tmp_path
    except:
        return None

def generate_audio(text):
    tts = gTTS(text)
    tmp_audio = tempfile.mktemp(suffix=".mp3")
    tts.save(tmp_audio)
    return tmp_audio

def create_clip(image_path, audio_path, text):
    audio_clip = AudioFileClip(audio_path)
    if image_path:
        img_clip = ImageClip(image_path).set_duration(audio_clip.duration)
    else:
        img_clip = ColorClip(size=(1280, 720), color=(0, 0, 0), duration=audio_clip.duration)
    img_clip = img_clip.set_audio(audio_clip).set_fps(FPS)

    txt_clip = TextClip(text, fontsize=40, color="white", bg_color="black", size=(1280, 100))
    txt_clip = txt_clip.set_duration(audio_clip.duration).set_position(("center", "bottom"))

    final = CompositeVideoClip([img_clip, txt_clip]).fadein(0.5).fadeout(0.5)
    final.fps = FPS
    return final

# --- UI Streamlit ---

st.title("🎬 IA Vidéo Multi-Scènes (sans split automatique)")

video_type = st.radio("Type de vidéo :", ["Courte (<1 min)", "Longue (<10 min)"])
max_duration = MAX_DURATION_SHORT if video_type == "Courte (<1 min)" else MAX_DURATION_LONG

num_scenes = st.number_input("Nombre de scènes", min_value=1, max_value=20, value=3)

scenes = []
for i in range(num_scenes):
    st.markdown(f"### Scène {i+1}")
    text = st.text_area(f"Texte de la scène {i+1}", key=f"text_{i}")
    prompt_img = st.text_input(f"Description image scène {i+1} (pour générer l'image)", key=f"img_{i}")
    scenes.append({"text": text, "img_prompt": prompt_img})

if st.button("Générer la vidéo"):
    clips = []
    total_duration = 0
    for idx, scene in enumerate(scenes):
        text = scene["text"].strip()
        img_prompt = scene["img_prompt"].strip()

        if not text:
            st.warning(f"Texte vide pour la scène {idx+1}, ignorée.")
            continue

        st.write(f"🎥 Génération scène {idx+1}...")
        audio_path = generate_audio(text)

        audio_clip = AudioFileClip(audio_path)
        if total_duration + audio_clip.duration > max_duration:
            st.warning("⏰ Durée max atteinte, arrêt.")
            break

        image_path = fetch_image(img_prompt) if img_prompt else None

        clip = create_clip(image_path, audio_path, text)
        clips.append(clip)
        total_duration += audio_clip.duration

    if clips:
        final_video = concatenate_videoclips(clips, method="compose")
        final_video.fps = FPS
        output_path = tempfile.mktemp(suffix=".mp4")
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
        st.success("✅ Vidéo générée !")
        st.video(output_path)
    else:
        st.error("❌ Aucune scène valide générée.")


