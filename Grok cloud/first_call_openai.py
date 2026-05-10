import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()

# Create client
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

# Send request
chat = client.chat.completions.create(
    model="llama-3.1-8b-instant",   # Fast + lightweight
    messages=[
        {
            "role": "system",
            "content": "You are a helpful AI mentor."
        },
        {
            "role": "user",
            "content": "Explain what Groq Cloud is in simple words."
        }
    ],
    max_tokens=100,
    temperature=0.5
)

# Print response
print("\n🤖 AI Response:\n")
print(chat.choices[0].message.content)