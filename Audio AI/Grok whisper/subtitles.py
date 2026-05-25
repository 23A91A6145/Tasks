from groq import Groq
from dotenv import load_dotenv
import os

# =========================
# LOAD API KEY
# =========================

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# =========================
# INPUT AUDIO / VIDEO
# =========================

audio_path = r"D:\Tasks\Audio AI\STT\Sample_audio\1_video.mp4"

# =========================
# OUTPUT SRT FILE
# =========================

output_path = r"D:\Tasks\Audio AI\STT\Audio_text_Outputs\subtitles.srt"

# =========================
# TRANSCRIBE AUDIO
# =========================

with open(audio_path, "rb") as file:

    result = client.audio.transcriptions.create(
        file=("1_video.mp4", file.read()),

        model="whisper-large-v3",

        response_format="verbose_json",

        temperature=0.0,

        timestamp_granularities=["segment"]
    )

# =========================
# TIME FORMAT FUNCTION
# =========================

def format_time(seconds):

    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)

    return f"{hrs:02}:{mins:02}:{secs:02},{millis:03}"

# =========================
# CREATE SRT FILE
# =========================

with open(output_path, "w", encoding="utf-8") as f:

    for i, segment in enumerate(result.segments, start=1):

        start = segment["start"]
        end = segment["end"]
        text = segment["text"].strip()

        f.write(f"{i}\n")
        f.write(f"{format_time(start)} --> {format_time(end)}\n")
        f.write(f"{text}\n\n")

print("\n✅ Subtitle file created successfully!")
print(f"📄 Saved at:\n{output_path}")