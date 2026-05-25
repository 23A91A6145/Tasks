from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import os

load_dotenv("D:/Tasks/Audio AI/.env")

client = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY")
)

audio = client.text_to_speech.convert(
    voice_id="ErXwobaYiN019PkySvjV",
    text="Artificial intelligence is rapidly transforming the future of humanity.",
    model_id="eleven_turbo_v2_5",
    output_format="mp3_44100_128",
    voice_settings={
        "stability": 0.50,
        "similarity_boost": 0.85,
        "style": 0.20,
        "use_speaker_boost": True
    }
)

output_path = r"D:\Tasks\Audio AI\Audios\youtube_documentary.mp3"

with open(output_path, "wb") as f:
    for chunk in audio:
        f.write(chunk)

print("Saved:", output_path)