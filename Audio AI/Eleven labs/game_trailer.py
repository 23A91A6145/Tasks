from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv(r"D:\Tasks\Audio AI\.env")

# Get API key
api_key = os.getenv("ELEVENLABS_API_KEY")

# Check API key
if not api_key:
    raise ValueError("ELEVENLABS_API_KEY not found in .env file")

# Initialize client
client = ElevenLabs(api_key=api_key)

# Generate audio
audio = client.text_to_speech.convert(
    voice_id="TxGEqnHWrfWFTfGW9XjX",  # Josh voice
    text="""
    In a world controlled by artificial intelligence,
    one human must fight to survive.
    """,
    model_id="eleven_turbo_v2_5",
    output_format="mp3_44100_128",
    voice_settings={
        "stability": 0.5,
        "similarity_boost": 0.8,
        "style": 0.6,
        "use_speaker_boost": True
    }
)

# Output path
output_path = r"D:\Tasks\Audio AI\Audios\game_trailer_fixed.mp3"

# Save audio
with open(output_path, "wb") as f:
    for chunk in audio:
        if chunk:
            f.write(chunk)

print(f"✅ Audio saved successfully:\n{output_path}")