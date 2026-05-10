import os
import wave
import sounddevice as sd
import numpy as np

from groq import Groq
from dotenv import load_dotenv

# =========================================
# LOAD ENV VARIABLES
# =========================================

load_dotenv()

# =========================================
# GROQ CLIENT
# =========================================

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# =========================================
# RECORD AUDIO FUNCTION
# =========================================

def record_audio(seconds=10, sample_rate=16000):

    print(f"\n🔴 Recording for {seconds} seconds...")
    print("🎤 Speak now!\n")

    audio = sd.rec(
        int(seconds * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='int16'
    )

    sd.wait()

    filename = "temp_recording.wav"

    # Save WAV file
    with wave.open(filename, "wb") as wf:

        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)

        wf.writeframes(audio.tobytes())

    print("✅ Recording saved!")

    return filename

# =========================================
# TRANSCRIBE AUDIO
# =========================================

def transcribe_audio(audio_file):

    print("\n📝 Transcribing audio...\n")

    with open(audio_file, "rb") as f:

        transcript = client.audio.transcriptions.create(

            file=(audio_file, f.read()),

            model="whisper-large-v3-turbo",

            response_format="verbose_json"
        )

    return transcript.text

# =========================================
# SUMMARIZE TEXT
# =========================================

def summarize_text(text):

    print("\n🤖 Generating study notes...\n")

    response = client.chat.completions.create(

        model="llama-3.1-8b-instant",

        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful study notes assistant."
                )
            },

            {
                "role": "user",
                "content": f"""
Create clean study notes from this transcript.

Include:
1. Key Points
2. Important Concepts
3. Action Items
4. Quick Summary

Transcript:
{text}
"""
            }
        ],

        temperature=0.3,

        max_tokens=400
    )

    return response.choices[0].message.content

# =========================================
# SAVE NOTES
# =========================================

def save_notes(notes):

    os.makedirs("notes", exist_ok=True)

    filepath = os.path.join(
        "notes",
        "study_notes.txt"
    )

    with open(filepath, "w", encoding="utf-8") as f:

        f.write(notes)

    print(f"\n💾 Notes saved:")
    print(filepath)

# =========================================
# MAIN PROGRAM
# =========================================
def main():
    print("=" * 50)
    print("🎙️ GROQ VOICE NOTE SUMMARIZER")
    print("=" * 50)
    try:
        # Step 1 — Record
        audio_file = record_audio(seconds=15)

        # Step 2 — Transcribe
        transcript = transcribe_audio(audio_file)

        print("\n🗣️ TRANSCRIPT:\n")
        print(transcript)

        # Step 3 — Summarize
        notes = summarize_text(transcript)

        print("\n📚 STUDY NOTES:\n")
        print(notes)

        # Step 4 — Save
        save_notes(notes)

        print("\n✅ Process Complete!")

    except Exception as e:

        print("\n❌ ERROR:")
        print(e)

# =========================================
# RUN PROGRAM
# =========================================

if __name__ == "__main__":
    main()