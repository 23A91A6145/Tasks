import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)
system_prompt = """
You are a technical writer.
DO NOT:
- Use phrases like "Great question!"
- Write more than 150 words
- Use emojis
- Use bullet points unless necessary
ALWAYS:
- Be concise
- Use active voice
- Give practical examples
"""
user_prompt = """
Explain what an API is for beginners.
"""
response = client.chat.completions.create(
    model="openrouter/auto",
    messages=[
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ],
    temperature=0.2
)

print(response.choices[0].message.content)