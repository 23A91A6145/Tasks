from openai import OpenAI
from dotenv import load_dotenv
import os
import json

# Load API key
load_dotenv()

# Fireworks-compatible client
client = OpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key=os.getenv("FIREWORKS_API_KEY")
)

# ---------------- PARAMETERS ---------------- #

TEMPERATURE = 0.7
MAX_TOKENS = 200
TOP_P = 0.9

# ---------------- REQUEST ---------------- #

response = client.chat.completions.create(
    model="accounts/fireworks/models/qwen3-8b",

    messages=[
        {
            "role": "system",
            "content": "You are a beginner-friendly AI mentor."
        },
        {
            "role": "user",
            "content": "Explain what AI agents are."
        }
    ],

    temperature=TEMPERATURE,
    max_tokens=MAX_TOKENS,
    top_p=TOP_P
)

# ---------------- OUTPUT ---------------- #

print("\nAI RESPONSE:\n")
print(response.choices[0].message.content)

print("\nTOKEN USAGE:")
print(response.usage.total_tokens)