import assemblyai as aai
from dotenv import load_dotenv
import os

# =========================
# LOAD API KEY
# =========================

load_dotenv()

aai.settings.api_key = os.getenv(
    "ASSEMBLYAI_API_KEY"
)

# =========================
# INPUT AUDIO FILE
# =========================

audio_file = (
    r"D:\Tasks\Audio AI\STT\Sample_audio\podcast1.mp3"
)

# =========================
# OUTPUT PATHS
# =========================

output_folder = (
    r"D:\Tasks\Audio AI\STT\Audio_text_Outputs\subtitles"
)

srt_output = os.path.join(
    output_folder,
    "podcast1.srt"
)

txt_output = os.path.join(
    output_folder,
    "podcast1.txt"
)

# =========================
# CONFIGURATION
# =========================

config = aai.TranscriptionConfig(

    speech_model=aai.SpeechModel.best,

    punctuate=True,

    format_text=True
)

# =========================
# TRANSCRIBE
# =========================

transcriber = aai.Transcriber()

transcript = transcriber.transcribe(
    audio_file,
    config=config
)

# =========================
# SAVE TRANSCRIPT
# =========================

with open(
    txt_output,
    "w",
    encoding="utf-8"
) as f:

    f.write(transcript.text)

# =========================
# EXPORT SRT SUBTITLES
# =========================

srt = transcript.export_subtitles_srt()

with open(
    srt_output,
    "w",
    encoding="utf-8"
) as f:

    f.write(srt)

# =========================
# DONE
# =========================

print("\n✅ Subtitle Generated")
print(f"\nSaved SRT:\n{srt_output}")