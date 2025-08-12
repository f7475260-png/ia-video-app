import os
import time
import random
from typing import List
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeAudioClip,
    concatenate_videoclips, afx, ColorClip
)
from utils.music_selector import get_music
from utils.text_to_speech import generate_voiceover
from utils.script_generator import generate_script

def _list_images(directory: str = "assets/images") -> List[str]:
    if not os.path.isdir(directory):
        return []
    exts = (".jpg", ".jpeg", ".png")
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.lower().endswith(exts)]
    files.sort()
    return files

def _target_resolution(format_type: str) -> tuple[int, int]:
    if format_type in {"tiktok", "short"}:
        return (1080, 1920)
    return (1920, 1080)

def generate_video(data: dict) -> str:
    theme = data.get("theme", "inspiration")
    language = data.get("language", "fr")
    duration_target = int(data.get("duration", 60))
    format_type = data.get("format", "youtube")

    os.makedirs("output", exist_ok=True)

    # 1) Script + voix
    script = generate_script(theme, language)
    voice_path = generate_voiceover(script, language)
    voice_clip = AudioFileClip(voice_path)
    voice_dur = voice_clip.duration
    duration = max(10, min(int(max(duration_target, voice_dur * 0.9)), int(voice_dur * 1.1)))

    # 2) Images
    images = _list_images()
    if not images:
        w, h = _target_resolution(format_type)
        video_clip = ColorClip(size=(w, h), color=(10, 10, 10), duration=duration)
    else:
        random.shuffle(images)
        w, h = _target_resolution(format_type)
        n_clips = max(1, min(len(images), int(duration // 4)))
        per_clip = duration / n_clips
        clips = []
        for i in range(n_clips):
            img = images[i % len(images)]
            c = ImageClip(img).set_duration(per_clip).resize(height=h)
            if i > 0:
                c = c.crossfadein(0.7)
            clips.append(c)
        video_clip = concatenate_videoclips(clips, method="compose")

    # 3) Musique (optionnelle)
    tracks = [voice_clip.volumex(1.0)]
    music_path = get_music(format_type)
    if music_path:
        music_clip = AudioFileClip(music_path).fx(afx.audio_loop, duration=video_clip.duration)
        music_clip = music_clip.volumex(0.12).audio_fadeout(1.0)
        tracks.append(music_clip)

    # 4) Mixage et export
    final = video_clip.set_audio(CompositeAudioClip(tracks).set_duration(video_clip.duration))
    out_path = os.path.join("output", f"video_{int(time.time())}.mp4")
    final.write_videofile(out_path, fps=24, codec="libx264", audio_codec="aac", preset="medium", threads=2, verbose=False, logger=None)
    try:
        voice_clip.close()
        if music_path:
            music_clip.close()
    except Exception:
        pass
    return out_path
