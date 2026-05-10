import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq()

messages = [{
    "role": "system",
    "content": """
You are Arya, a friendly AI mentor for Charan.

Rules:
- Explain simply
- Use beginner examples
- Be encouraging
- Explain coding step-by-step
"""
}]

print("\n🤖 Arya AI Mentor Started!")
print("Type 'exit' to stop.\n")

while True:

    user_input = input("Charan: ")

    if user_input.lower() in ["exit", "quit", "bye"]:
        print("\n🤖 Arya: Keep building AI projects! 🌟")
        break

    messages.append({
        "role": "user",
        "content": user_input
    })

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=300,
        temperature=0.7
    )

    reply = response.choices[0].message.content

    messages.append({
        "role": "assistant",
        "content": reply
    })

    print(f"\n🤖 Arya: {reply}\n")