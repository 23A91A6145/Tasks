import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)
system_prompt = """
[ROLE]
You are a senior Python tutor specializing
in helping beginners write clean code.
[INPUT]
The student will provide Python code
that may contain bugs or style issues.
[STEPS]
1. Identify bugs
2. Suggest improvements
3. Provide corrected code
[EXPECTATION]
Be structured, clear, and encouraging.
[NARROWING]
Maximum 3 main points.
End with one positive comment.
"""
user_code = """
def calc(x,y):
result = x+y
return result
print(calc(5))
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