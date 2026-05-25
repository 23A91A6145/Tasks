from groq import Groq
from dotenv import load_dotenv
import os
# =========================
# LOAD ENV VARIABLES
# =========================
load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)
# =========================
# INPUT AUDIO FILE
# =========================
audio_path = r"D:\Tasks\Audio AI\STT\Sample_audio\2_life.mp3"
# =========================
# OUTPUT TEXT FILE
# =========================
output_text_path = r"D:\Tasks\Audio AI\STT\Audio_text_Outputs\output.txt"
# =========================
# TRANSCRIBE AUDIO
# =========================

with open(audio_path, "rb") as audio_file:

    result = client.audio.transcriptions.create(
        file=("sample.mp3", audio_file.read()),

        # BEST MODEL
        model="whisper-large-v3",

        # OUTPUT TYPE
        response_format="verbose_json",

        # OPTIONAL SETTINGS
        language="en",          # Remove for auto detect
        temperature=0.0,

        # TIMESTAMPS
        timestamp_granularities=["word", "segment"]
    )

# =========================
# PRINT TEXT
# =========================

print("\n===== TRANSCRIPT =====\n")
print(result.text)

# =========================
# SAVE OUTPUT
# =========================

with open(output_text_path, "w", encoding="utf-8") as f:
    f.write(result.text)

print(f"\n✅ Transcript saved to:\n{output_text_path}")