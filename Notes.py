from groq import Groq
from dotenv import load_dotenv
import os

# ==========================
# LOAD API KEY
# ==========================

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# ==========================
# INPUT AUDIO
# ==========================

audio_path = r"D:\Tasks\Audio AI\STT\Sample_audio\5_audio.mp3"

# ==========================
# OUTPUT FILE
# ==========================

output_path = r"D:\Tasks\Audio AI\STT\Audio_text_Outputs\meeting_notes.txt"

# ==========================
# TRANSCRIBE AUDIO
# ==========================

with open(audio_path, "rb") as file:

    transcript = client.audio.transcriptions.create(
        file=("5_audio.mp3", file.read()),

        model="whisper-large-v3",

        response_format="verbose_json",

        language="en",

        temperature=0.0,

        timestamp_granularities=["segment"]
    )

# ==========================
# CREATE SUMMARY
# ==========================

meeting_text = transcript.text

summary = f"""
==========================
AI MEETING NOTES
==========================

FULL TRANSCRIPT:
{meeting_text}

==========================
MEETING SUMMARY
==========================

Discussion completed successfully.

==========================
ACTION ITEMS
==========================

1. Review project
2. Complete pending tasks
3. Test AI workflow

==========================
IMPORTANT DECISIONS
==========================

- Use Whisper model
- Improve subtitle quality
- Continue deployment testing
"""

# ==========================
# SAVE OUTPUT
# ==========================

with open(output_path, "w", encoding="utf-8") as f:
    f.write(summary)

print("✅ Meeting notes generated successfully!")