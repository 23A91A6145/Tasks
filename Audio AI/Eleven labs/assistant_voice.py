from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import os

load_dotenv("D:/Tasks/Audio AI/.env")

client = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY")
)

audio = client.text_to_speech.convert(
    voice_id="TxGEqnHWrfWFTfGW9XjX",
    text="Hello Charan. Your AI automation workflow has completed successfully.",
    model_id="eleven_flash_v2",
    output_format="mp3_44100_128",
    voice_settings={
        "stability": 0.60,
        "similarity_boost": 0.80,
        "style": 0.30,
        "use_speaker_boost": True
    }
)

output_path = r"D:\Tasks\Audio AI\Audios\assistant_voice.mp3"

with open(output_path, "wb") as f:
    for chunk in audio:
        f.write(chunk)

print("Saved:", output_path)