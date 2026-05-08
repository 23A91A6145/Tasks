import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

messages = [
    {"role": "user", "content": "Explain Python simply"}
]

response = client.chat.completions.create(
    model="openrouter/auto",
    messages=messages,
    temperature=0.1  # based on purpose.
)

print(response.choices[0].message.content)