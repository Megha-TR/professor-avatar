# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import subprocess
import os # Added for absolute paths

app = FastAPI()
origins = ["http://localhost:8000"]

# Define API routes BEFORE mounting static files
@app.post("/generate")
async def generate(req: Request):
    data = await req.json()
    text = data["text"]

    # Define relative paths from the perspective of main.py
    base_static_path = os.path.abspath("static") # Absolute path to the static directory
    tts_audio_filename = "generated.wav"
    input_video_filename = "input_video.mp4"
    final_output_filename = "final_output.mp4"

    # Construct absolute paths for all files
    abs_tts_audio_path = os.path.join(base_static_path, tts_audio_filename)
    abs_input_video_for_wav2lip = os.path.join(base_static_path, input_video_filename)
    abs_final_output_video_path = os.path.join(base_static_path, final_output_filename)
    abs_speaker_wav_path = os.path.join(base_static_path, "output.wav")

    # Determine project root dynamically
    # __file__ is the path to main.py
    # os.path.dirname(__file__) is the directory of main.py (e.g., project_root/frontend/my-js-app/)
    # project_root is assumed to be two levels up from script_dir
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", "..")) 

    # Assume Wav2Lip directory is at the project root
    # wav2lip_root_path = os.path.join(project_root, "Wav2Lip") # This was incorrect
    wav2lip_root_path = "/home/megha-tr/Wav2Lip" # Corrected hardcoded path
    wav2lip_checkpoint_path = os.path.join(wav2lip_root_path, "checkpoints/wav2lip_gan.pth")
    wav2lip_inference_script = os.path.join(wav2lip_root_path, "inference.py")

    try:
        # Step 1: Text-to-Speech
        print("🚀 Starting TTS generation...")
        tts_result = subprocess.run([
            "python", "-m", "TTS.bin.synthesize",
            "--text", text,
            "--model_name", "tts_models/multilingual/multi-dataset/xtts_v2",
            "--speaker_wav", abs_speaker_wav_path,
            "--language_idx", "en",
            "--out_path", abs_tts_audio_path
        ], check=True, capture_output=True, text=True)
        print("✅ TTS generation successful.")
        # print("TTS STDOUT:", tts_result.stdout) # Can be verbose

        # Step 2: Wav2Lip
        print(f"🚀 Starting Wav2Lip generation with audio: {abs_tts_audio_path} and video: {abs_input_video_for_wav2lip}")
        wav2lip_command = [
            "python", wav2lip_inference_script,
            "--checkpoint_path", wav2lip_checkpoint_path,
            "--face", abs_input_video_for_wav2lip, # Use absolute path (reverted)
            "--audio", abs_tts_audio_path,          # Use absolute path (reverted)
            "--outfile", abs_final_output_video_path # Use absolute path (reverted)
        ]
        print(f"Executing Wav2Lip command: {' '.join(wav2lip_command)}")

        wav2lip_result = subprocess.run(
            wav2lip_command,
            check=True, capture_output=True, text=True,
            cwd=wav2lip_root_path # Run Wav2Lip from its directory
        )
        print("✅ Wav2Lip generation successful.")
        # print("Wav2Lip STDOUT:", wav2lip_result.stdout) # Can be verbose
        if wav2lip_result.stderr:
            print("Wav2Lip STDERR:", wav2lip_result.stderr)

        return { "video_url": f"http://localhost:8002/static/{final_output_filename}" }

    except subprocess.CalledProcessError as e:
        error_message = f"🔥 Error during processing: {e}"
        if hasattr(e, 'cmd') and "tts" in e.cmd:
            error_message = f"🔥 TTS generation failed: {e}"
        elif hasattr(e, 'cmd') and "inference.py" in e.cmd:
            error_message = f"🔥 Wav2Lip generation failed: {e}"
        
        print(error_message)
        if e.stderr:
            print("🔥 STDERR:", e.stderr)
        if e.stdout:
            print("🔥 STDOUT:", e.stdout)
        return { "error": error_message, "stderr": e.stderr, "stdout": e.stdout }
    except Exception as e:
        print(f"🚨 An unexpected error occurred: {str(e)}")
        return { "error": f"An unexpected error occurred: {str(e)}" }


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the 'build' directory (output of npm run build) to serve the React app from the root
app.mount("/", StaticFiles(directory="build", html=True), name="app") # Changed name to avoid conflict if you also have a directory named "build"

# This serves files like generated.wav and final_output.mp4
app.mount("/static", StaticFiles(directory="static"), name="static_generated") # Renamed to avoid potential conflict with React's build/static

