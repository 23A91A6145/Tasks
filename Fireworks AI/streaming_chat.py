from fireworks.client import Fireworks
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()

# Initialize client
client = Fireworks(
    api_key=os.getenv("FIREWORKS_API_KEY")
)

# Create streaming request
stream = client.chat.completions.create(
    model="accounts/fireworks/models/qwen3-8b",
    messages=[
        {
            "role": "user",
            "content": "Write a short motivational poem about AI."
        }
    ],
    stream=True,
    max_tokens=200,
    temperature=0.8
)
# Print streaming output
print("\nAI RESPONSE:\n")
for chunk in stream:
    if chunk.choices:
        delta = chunk.choices[0].delta.content
        if delta:
            print(delta, end="", flush=True)

print("\n")