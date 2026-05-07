import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

messages = [
    {"role": "user", "content": "Explain AI simply"}
]

response = client.chat.completions.create(
    model="openrouter/auto",
    messages=messages,
    extra_body={
        "route": "fallback",
        "models": [
            "google/gemma-2-9b-it",
            "openai/gpt-4o-mini",
            "openrouter/auto"
        ]
    }
)

print(response.choices[0].message.content)