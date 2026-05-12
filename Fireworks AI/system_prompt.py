from openai import OpenAI
from dotenv import load_dotenv
import os

# Load API key
load_dotenv()

# Create Fireworks-compatible client
client = OpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key=os.getenv("FIREWORKS_API_KEY")
)

# ---------------- SYSTEM PROMPTS ---------------- #

TUTOR_PROMPT = """
You are Charan's personal AI tutor.

Rules:
- Use simple beginner-friendly language
- Explain like teaching a 15-year-old student
- Give one real-world example
- Keep answers under 120 words
- End with a short practice tip
"""

FORMAT_PROMPT = """
Always respond in this format:

📌 ANSWER:
[short answer]

🔑 KEY POINTS:
• point 1
• point 2
• point 3

💡 EXAMPLE:
[real-world example]
"""

STYLE_PROMPT = """
You are a professional AI engineer.

Style Rules:
- concise
- practical
- structured
- use numbered steps
- avoid unnecessary jargon
"""

# ---------------- REQUEST ---------------- #

response = client.chat.completions.create(
    model="accounts/fireworks/models/qwen3-8b",
    messages=[
        {
            "role": "system",
            "content": TUTOR_PROMPT
        },
        {
            "role": "user",
            "content": "What is an API?"
        }
    ],
    max_tokens=200,
    temperature=0.7
)

# Print response
print("\nAI RESPONSE:\n")
print(response.choices[0].message.content)