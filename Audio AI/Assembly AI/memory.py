import assemblyai as aai
from dotenv import load_dotenv
import os
import json

# =====================================
# LOAD ENV VARIABLES
# =====================================

load_dotenv()

aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

# =====================================
# AUDIO INPUT
# =====================================

audio_path = r"D:\Tasks\Audio AI\STT\Sample_audio\1_pro.wav"

# =====================================
# OUTPUT FOLDER
# =====================================

output_folder = r"D:\Tasks\Audio AI\STT\Audio_text_Outputs"

os.makedirs(output_folder, exist_ok=True)

# =====================================
# OUTPUT FILES
# =====================================

transcript_output = os.path.join(
    output_folder,
    "transcript.txt"
)

summary_output = os.path.join(
    output_folder,
    "summary.txt"
)

chapters_output = os.path.join(
    output_folder,
    "chapters.txt"
)

memory_output = os.path.join(
    output_folder,
    "memory.json"
)

# =====================================
# TRANSCRIPTION CONFIG
# =====================================

config = aai.TranscriptionConfig(

    # WORKING MODEL
    speech_model=aai.SpeechModel.best,

    # FEATURES
    speaker_labels=True,

    auto_chapters=True,

    summarization=True,

    sentiment_analysis=True,

    entity_detection=True
)

# =====================================
# CREATE TRANSCRIBER
# =====================================

transcriber = aai.Transcriber(config=config)

# =====================================
# START TRANSCRIPTION
# =====================================

print("\n🎤 Uploading Audio...\n")

transcript = transcriber.transcribe(audio_path)

# =====================================
# CHECK ERRORS
# =====================================

if transcript.status == "error":

    print("\n❌ ERROR:\n")

    print(transcript.error)

    exit()

# =====================================
# PRINT TRANSCRIPT
# =====================================

print("\n===== TRANSCRIPT =====\n")

print(transcript.text)

# =====================================
# SAVE TRANSCRIPT
# =====================================

with open(transcript_output, "w", encoding="utf-8") as f:

    f.write(transcript.text)

# =====================================
# SAVE SUMMARY
# =====================================

if transcript.summary:

    with open(summary_output, "w", encoding="utf-8") as f:

        f.write(transcript.summary)

# =====================================
# SAVE CHAPTERS
# =====================================

if transcript.chapters:

    with open(chapters_output, "w", encoding="utf-8") as f:

        for chapter in transcript.chapters:

            start_time = chapter.start / 1000

            f.write(
                f"{start_time:.0f}s - "
                f"{chapter.headline}\n"
            )

# =====================================
# MEMORY SYSTEM
# =====================================

memory_data = []

# LOAD OLD MEMORY
if os.path.exists(memory_output):

    try:

        with open(memory_output, "r", encoding="utf-8") as f:

            memory_data = json.load(f)

    except:

        memory_data = []

# =====================================
# ADD NEW MEMORY
# =====================================

memory_data.append({

    "audio_file": os.path.basename(audio_path),

    "transcript": transcript.text,

    "summary": transcript.summary,

    "status": transcript.status
})

# =====================================
# SAVE MEMORY
# =====================================

with open(memory_output, "w", encoding="utf-8") as f:

    json.dump(memory_data, f, indent=4)

# =====================================
# SUCCESS
# =====================================

print("\n✅ Transcript Saved")
print("✅ Summary Saved")
print("✅ Chapters Saved")
print("✅ Memory Updated")

print("\n📁 Output Folder:")
print(output_folder)