import os
from flask import Flask, render_template, request, send_file, abort
from dotenv import load_dotenv
from utils.video_generator import generate_video

load_dotenv()
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.form.to_dict()
    data["duration"] = max(10, min(int(data.get("duration", 60)), 180))
    data["theme"] = data.get("theme", "inspiration").strip()[:120]
    data["language"] = data.get("language", "fr")
    data["format"] = data.get("format", "youtube")
    video_path = generate_video(data)
    return render_template("index.html", video_path=video_path)

@app.route("/file")
def serve_file():
    path = request.args.get("path")
    if not path or not os.path.isfile(path):
        return abort(404)
    return send_file(path, as_attachment=False)

if __name__ == "__main__":
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "7860"))
    app.run(host=host, port=port, debug=True)
