import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

print("🤖 Response: ", end="", flush=True)

stream = client.chat.completions.create(
    model="openrouter/auto",  # ✅ FIXED
    messages=[
        {"role": "user", "content": "Write a short poem about coding"}
    ],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)

print()