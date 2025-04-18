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
        subprocess.run([
            "tts",
            "--text", text,
            "--model_name", "tts_models/multilingual/multi-dataset/your_tts",
            "--speaker_wav", "output.wav",
            "--out_path", "static/output.wav"
        ], check=True)

        return { "audio_url": "http://localhost:8000/static/output.wav" }

    except subprocess.CalledProcessError as e:
        print("🔥 TTS ERROR:", e)
        return { "error": "TTS generation failed" }

