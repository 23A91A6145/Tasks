import os
import tempfile
import sounddevice as sd
from scipy.io.wavfile import write
from groq import Groq
from dotenv import load_dotenv
import google.generativeai as genai
from elevenlabs.client import ElevenLabs
from elevenlabs import save
import pygame

# =========================
# LOAD ENV
# =========================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# =========================
# INIT CLIENTS
# =========================

groq_client = Groq(api_key=GROQ_API_KEY)

genai.configure(api_key=GEMINI_API_KEY)

gemini_model = genai.GenerativeModel(
    "gemini-2.0-flash"
)

eleven_client = ElevenLabs(
    api_key=ELEVENLABS_API_KEY
)

# =========================
# RECORD AUDIO
# =========================

duration = 5
sample_rate = 44100

print("\n🎤 Speak now...\n")

audio = sd.rec(
    int(duration * sample_rate),
    samplerate=sample_rate,
    channels=1,
    dtype="int16"
)

sd.wait()

temp_audio = tempfile.NamedTemporaryFile(
    delete=False,
    suffix=".wav"
)

write(
    temp_audio.name,
    sample_rate,
    audio
)

print("✅ Audio recorded")

# =========================
# SPEECH TO TEXT
# =========================

with open(temp_audio.name, "rb") as file:

    transcription = groq_client.audio.transcriptions.create(
        file=("audio.wav", file.read()),
        model="whisper-large-v3",
        response_format="json"
    )

user_text = transcription.text

print("\n📝 USER SAID:")
print(user_text)

# =========================
# GEMINI RESPONSE
# =========================

prompt = f"""
You are a helpful AI voice assistant.

User said:
{user_text}

Reply naturally and conversationally.
"""

response = gemini_model.generate_content(
    prompt
)

ai_text = response.text

print("\n🤖 AI RESPONSE:")
print(ai_text)

# =========================
# TEXT TO SPEECH
# =========================

audio = eleven_client.text_to_speech.convert(
    voice_id="EXAVITQu4vr4xnSDxMaL",

    model_id="eleven_turbo_v2_5",

    text=ai_text,

    voice_settings={
        "stability": 0.45,
        "similarity_boost": 0.80,
        "style": 0.0,
        "use_speaker_boost": True
    }
)

output_path = "response.mp3"

save(audio, output_path)

print("\n🔊 Playing response...")

# =========================
# PLAY AUDIO
# =========================

pygame.init()
pygame.mixer.init()

pygame.mixer.music.load(output_path)
pygame.mixer.music.play()

while pygame.mixer.music.get_busy():
    continue

print("\n✅ Done")