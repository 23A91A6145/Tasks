from groq import Groq
from dotenv import load_dotenv
import os
from datetime import datetime

# =========================
# LOAD ENV VARIABLES
# =========================

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# =========================
# INPUT / OUTPUT FOLDERS
# =========================

INPUT_FOLDER = r"D:\Tasks\Audio AI\STT\Sample_audio"

OUTPUT_FOLDER = r"D:\Tasks\Audio AI\STT\Audio_text_Outputs"

# =========================
# SUPPORTED AUDIO TYPES
# =========================

SUPPORTED_FORMATS = (
    ".mp3",
    ".wav",
    ".m4a",
    ".flac",
    ".ogg"
)

# =========================
# START PROCESS
# =========================

print("\n🎤 Batch Transcription Started...\n")

for filename in os.listdir(INPUT_FOLDER):

    if filename.lower().endswith(SUPPORTED_FORMATS):

        try:

            audio_path = os.path.join(INPUT_FOLDER, filename)

            base_name = os.path.splitext(filename)[0]

            output_path = os.path.join(
                OUTPUT_FOLDER,
                f"{base_name}.txt"
            )

            print(f"📂 Processing: {filename}")

            with open(audio_path, "rb") as audio_file:

                result = client.audio.transcriptions.create(
                    file=(filename, audio_file.read()),

                    model="whisper-large-v3",

                    response_format="verbose_json",

                    language="en",

                    temperature=0.0,

                    timestamp_granularities=["segment"]
                )

            with open(output_path, "w", encoding="utf-8") as f:

                f.write("===== TRANSCRIPT =====\n\n")

                f.write(result.text)

            print(f"✅ Saved: {output_path}\n")

        except Exception as e:

            print(f"❌ Error processing {filename}")
            print(e)

print("\n🚀 ALL FILES COMPLETED")