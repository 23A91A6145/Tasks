from fireworks.client import Fireworks
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Fireworks client
client = Fireworks(
    api_key=os.getenv("FIREWORKS_API_KEY")
)

# Create chat completion
response = client.chat.completions.create(
    model="accounts/fireworks/models/qwen3-8b",
    messages=[
        {
            "role": "user",
            "content": "Explain AI agents in simple beginner-friendly words."
        }
    ],
    max_tokens=200,
    temperature=0.7
)

# Print response
print("\nAI RESPONSE:\n")
print(response.choices[0].message.content)

# Token usage
print("\nTOKENS USED:")
print(response.usage.total_tokens)