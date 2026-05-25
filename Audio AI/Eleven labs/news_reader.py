from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import os

load_dotenv("D:/Tasks/Audio AI/.env")

client = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY")
)

audio = client.text_to_speech.convert(
    voice_id="N2lVS1w4EtoT3dr4eOWO",
    text="Breaking news. AI companies are now deploying multimodal agents across global enterprise systems.",
    model_id="eleven_turbo_v2_5",
    output_format="mp3_44100_128",
    voice_settings={
        "stability": 0.80,
        "similarity_boost": 0.75,
        "style": 0.10,
        "use_speaker_boost": True
    }
)

output_path = r"D:\Tasks\Audio AI\Audios\news_reader.mp3"

with open(output_path, "wb") as f:
    for chunk in audio:
        f.write(chunk)

print("Saved:", output_path)