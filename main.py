# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import subprocess

app = FastAPI()
origins = ["http://localhost:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/generate")
async def generate(req: Request):
    data = await req.json()
    text = data["text"]

    try:
        result = subprocess.run([
            "tts",
            "--text", text,
            "--model_name", "tts_models/multilingual/multi-dataset/xtts_v2",
            "--speaker_wav", "static/output.wav",
            "--language_idx", "en",
            "--out_path", "static/generated.wav"
        ], check=True, capture_output=True, text=True)
        return { "audio_url": "http://localhost:8002/static/generated.wav" }

    except subprocess.CalledProcessError as e:
        print("🔥 TTS ERROR:", e)
        if e.stderr:
            print("🔥 TTS STDERR:", e.stderr)
        if e.stdout:
            print("🔥 TTS STDOUT:", e.stdout)
        return { "error": "TTS generation failed" }

