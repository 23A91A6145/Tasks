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

audio_path = r"D:\Tasks\Audio AI\STT\Sample_audio\3_let.mp3"

# =========================
# OUTPUT FILE
# =========================

output_path = r"D:\Tasks\Audio AI\STT\Audio_text_Outputs\word_timestamps.txt"

# =========================
# TRANSCRIBE
# =========================

with open(audio_path, "rb") as file:

    result = client.audio.transcriptions.create(
        file=("3_let.mp3", file.read()),

        model="whisper-large-v3",

        response_format="verbose_json",

        timestamp_granularities=["word"],

        temperature=0.0
    )

# =========================
# SAVE WORD TIMESTAMPS
# =========================

with open(output_path, "w", encoding="utf-8") as f:

    for word in result.words:

        start_time = word["start"]
        end_time = word["end"]
        text_word = word["word"]

        line = f"{start_time:.2f}s --> {end_time:.2f}s : {text_word}\n"

        f.write(line)

print("\n✅ Word timestamps saved successfully!")
print(f"📄 Output: {output_path}")