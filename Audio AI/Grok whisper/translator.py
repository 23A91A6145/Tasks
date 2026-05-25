from groq import Groq
from dotenv import load_dotenv
import os

# =========================
# LOAD ENV
# =========================

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# =========================
# INPUT AUDIO
# =========================

audio_path = r"D:\Tasks\Audio AI\STT\Sample_audio\4_power.mp3"

# =========================
# OUTPUT TEXT
# =========================

output_path = r"D:\Tasks\Audio AI\STT\Audio_text_Outputs\Telugu_translation.txt"

# =========================
# TRANSLATE AUDIO
# =========================

with open(audio_path, "rb") as file:

    result = client.audio.translations.create(

        file=("4_power.mp3", file.read()),

        model="whisper-large-v3"
    )

# =========================
# PRINT OUTPUT
# =========================

print("\n===== TRANSLATION =====\n")

print(result.text)

# =========================
# SAVE OUTPUT
# =========================

with open(output_path, "w", encoding="utf-8") as f:
    f.write(result.text)

print("\n✅ Translation Saved")