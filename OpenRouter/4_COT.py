import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

prompt = """
Solve this step by step.

A store sells:
A = $12
B = $8
C = $15

I buy:
2A + 3B + 1C

Think through each step
before giving final answer.
"""

response = client.chat.completions.create(
    model="openrouter/auto",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0.2
)

print(response.choices[0].message.content)