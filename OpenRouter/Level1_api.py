import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)
response = client.chat.completions.create(
    model="inclusionai/ling-2.6-1t:free",
    messages=[
        {"role": "user", "content": "Explain RAG in 3 bullet points"}
    ]
)

print(response.choices[0].message.content)