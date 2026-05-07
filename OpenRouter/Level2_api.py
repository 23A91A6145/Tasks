import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

messages = [
    {
        "role": "system",
        "content": "You are a helpful AI tutor for beginners learning Python. Keep answers simple, use examples, and be encouraging."
    }
]

print("🤖 Python Tutor Bot — type 'quit' to exit\n")

while True:
    user_input = input("You: ")

    if user_input.lower() == "quit":
        break

    messages.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model="openrouter/auto",   # ✅ FIXED
            messages=messages,
            temperature=0.7
        )

        reply = response.choices[0].message.content

        messages.append({"role": "assistant", "content": reply})

        print(f"\n🤖 Bot: {reply}\n")

    except Exception as e:
        print(f"\n❌ Error: {e}\n")