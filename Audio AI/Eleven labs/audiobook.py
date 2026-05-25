from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import os

load_dotenv("D:/Tasks/Audio AI/.env")

client = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY")
)

audio = client.text_to_speech.convert(
    voice_id="EXAVITQu4vr4xnSDxMaL",
    text="As the rain poured through the silent city, she realized everything had changed forever.",
    model_id="eleven_multilingual_v2",
    output_format="mp3_44100_128",
    voice_settings={
        "stability": 0.35,
        "similarity_boost": 0.90,
        "style": 0.70,
        "use_speaker_boost": True
    }
)

output_path = r"D:\Tasks\Audio AI\Audios\audiobook_story.mp3"

with open(output_path, "wb") as f:
    for chunk in audio:
        f.write(chunk)

print("Saved:", output_path)