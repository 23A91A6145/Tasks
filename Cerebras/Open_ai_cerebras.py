from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://api.cerebras.ai/v1",
    api_key=os.environ.get("CEREBRAS_API_KEY")
)

response = client.chat.completions.create(
    model="llama3.1-8b",
    messages=[
        {
            "role": "user",
            "content": "Explain AI in simple words."
        }
    ]
)

print(response.choices[0].message.content)