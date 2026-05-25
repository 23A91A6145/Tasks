from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import os

# =========================
# LOAD ENV VARIABLES
# =========================

load_dotenv()

# =========================
# GET API KEY
# =========================

api_key = os.getenv("ELEVENLABS_API_KEY")

# =========================
# CREATE ELEVENLABS CLIENT
# =========================

client = ElevenLabs(api_key=api_key)

# =========================
# AUDIO OUTPUT FOLDER
# =========================

output_folder = r"D:\Tasks\Audio AI\Audios"

# Create folder automatically if missing
os.makedirs(output_folder, exist_ok=True)

# Output file path
output_path = os.path.join(output_folder, "output.mp3")

# =========================
# GENERATE AUDIO
# =========================

audio = client.text_to_speech.convert(
    voice_id="EXAVITQu4vr4xnSDxMaL",   # Rachel Voice
    text="""
    Hello Charan.
    
    Welcome to ElevenLabs AI Voice Generation.
    
    Your setup is now working successfully.
    """,
    model_id="eleven_turbo_v2_5"
)

# =========================
# SAVE AUDIO FILE
# =========================

with open(output_path, "wb") as f:
    for chunk in audio:
        if chunk:
            f.write(chunk)

# =========================
# SUCCESS MESSAGE
# =========================

print(f"Audio saved successfully at:\n{output_path}")