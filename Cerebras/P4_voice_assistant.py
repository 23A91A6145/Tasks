import os
import time
import scipy.io.wavfile as wav
import sounddevice as sd

from groq import Groq
from gtts import gTTS
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

import pygame

# =========================
# LOAD ENV
# =========================

load_dotenv()

groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

cerebras_client = Cerebras(
    api_key=os.getenv("CEREBRAS_API_KEY")
)

# =========================
# AUDIO SETTINGS
# =========================

SAMPLE_RATE = 16000
DURATION = 3

INPUT_FILE = "temp_input.wav"
OUTPUT_FILE = "response.mp3"

# =========================
# RECORD AUDIO
# =========================

def record_audio():

    print("\n🎤 Speak now...")

    recording = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype='int16'
    )

    sd.wait()

    wav.write(INPUT_FILE, SAMPLE_RATE, recording)

    print("✅ Recording complete.")

# =========================
# TRANSCRIBE
# =========================

def transcribe_audio():

    print("🧠 Transcribing...")

    with open(INPUT_FILE, "rb") as file:

        transcription = groq_client.audio.transcriptions.create(
            file=file,
            model="whisper-large-v3"
        )

    text = transcription.text

    print(f"\n🗣 You said: {text}")

    return text

# =========================
# GENERATE RESPONSE
# =========================

def generate_response(user_text):

    print("\n⚡ Cerebras thinking...")

    response = cerebras_client.chat.completions.create(
        model="llama3.1-8b",
        messages=[
            {
                "role": "system",
                "content": "You are Kiran, a helpful AI assistant."
            },
            {
                "role": "user",
                "content": user_text
            }
        ],
        max_tokens=200
    )

    ai_text = response.choices[0].message.content

    print(f"\n🤖 AI: {ai_text}")

    return ai_text

# =========================
# SPEAK RESPONSE
# =========================

def speak_text(text):

    print("\n🔊 Speaking...")

    tts = gTTS(text=text, lang='en')

    tts.save(OUTPUT_FILE)

    pygame.mixer.init()
    pygame.mixer.music.load(OUTPUT_FILE)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        continue

# =========================
# MAIN LOOP
# =========================

def main():

    print("=" * 50)
    print("🚀 REAL-TIME VOICE ASSISTANT")
    print("=" * 50)

    while True:

        start = time.time()

        record_audio()

        user_text = transcribe_audio()

        if "exit" in user_text.lower():
            print("👋 Exiting...")
            break

        ai_response = generate_response(user_text)

        speak_text(ai_response)

        total = time.time() - start

        print(f"\n⚡ Total latency: {total:.2f} sec")

# =========================
# RUN
# =========================

if __name__ == "__main__":
    main()