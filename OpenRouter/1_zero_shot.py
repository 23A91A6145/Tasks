import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API key
load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)
prompt = """
List 5 Python data types with
one example each.

Format as a numbered list.
"""
response = client.chat.completions.create(
    model="openrouter/auto",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0.3
)

print(response.choices[0].message.content)