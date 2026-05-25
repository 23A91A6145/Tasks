from groq import Groq
from dotenv import load_dotenv
import os
import sounddevice as sd
from scipy.io.wavfile import write

# =========================
# LOAD ENV
# =========================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("❌ API key not found in .env")
    exit()

client = Groq(api_key=api_key)

# =========================
# PATHS
# =========================

audio_folder = r"D:\Tasks\Audio AI\STT\temp_audio"
output_folder = r"D:\Tasks\Audio AI\STT\Audio_text_Outputs"

# Create folders automatically
os.makedirs(audio_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

audio_path = os.path.join(audio_folder, "user_input.wav")

transcript_path = os.path.join(output_folder, "transcript.txt")

response_path = os.path.join(output_folder, "ai_response.txt")

# =========================
# AUDIO SETTINGS
# =========================

sample_rate = 44100
duration = 5  # seconds

# =========================
# RECORD USER AUDIO
# =========================

print("\n🎤 Speak now...")
print(f"⏱️ Recording for {duration} seconds...\n")

try:

    recording = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='int16'
    )

    sd.wait()

    print("✅ Recording completed")

except Exception as e:

    print(f"❌ Recording error: {e}")
    exit()

# =========================
# SAVE AUDIO
# =========================

write(audio_path, sample_rate, recording)

print(f"✅ Audio saved:\n{audio_path}")

# =========================
# TRANSCRIBE AUDIO
# =========================

try:

    with open(audio_path, "rb") as file:

        transcript = client.audio.transcriptions.create(
            file=("user_input.wav", file.read()),

            model="whisper-large-v3",

            response_format="text",

            temperature=0.0
        )

except Exception as e:

    print(f"❌ Transcription error: {e}")
    exit()

# =========================
# USER TEXT
# =========================

user_text = transcript

print("\n📝 USER SAID:\n")
print(user_text)

# =========================
# AI RESPONSE
# =========================

ai_response = f"""
USER ASKED:
{user_text}

AI RESPONSE:
I understood your speech successfully.
"""

print("\n🤖 AI RESPONSE:\n")
print(ai_response)

# =========================
# SAVE TRANSCRIPT
# =========================

with open(transcript_path, "w", encoding="utf-8") as f:
    f.write(user_text)

# =========================
# SAVE AI RESPONSE
# =========================

with open(response_path, "w", encoding="utf-8") as f:
    f.write(ai_response)

print("\n✅ Files saved successfully")
print(f"📄 Transcript: {transcript_path}")
print(f"📄 Response: {response_path}")