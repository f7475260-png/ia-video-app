import os
import random

def get_music(format_type: str = "youtube") -> str | None:
    music_dir = "assets/music"
    if not os.path.isdir(music_dir):
        return None
    files = [os.path.join(music_dir, f) for f in os.listdir(music_dir) if f.lower().endswith(".mp3")]
    return random.choice(files) if files else None
