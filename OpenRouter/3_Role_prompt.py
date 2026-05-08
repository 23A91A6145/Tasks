import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API key
load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

system_prompt = """
You are a senior Python developer
with 10 years of experience.

You review code carefully,
identify bugs,
give line-by-line feedback,
and suggest improvements.
"""

user_code = """
def add(a,b)
    return a+b
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
            "content": f"Review this code:\n{user_code}"
        }
    ],
    temperature=0.2
)

print(response.choices[0].message.content)