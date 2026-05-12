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

# ---------------- CHATBOT CLASS ---------------- #

class Chatbot:

    def __init__(self, system_prompt="You are a friendly AI tutor."):

        self.history = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]

        self.model = "accounts/fireworks/models/qwen3-8b"

    # Chat function
    def chat(self, user_msg):

        # Store user message
        self.history.append(
            {
                "role": "user",
                "content": user_msg
            }
        )

        # Generate AI response
        response = client.chat.completions.create(
            model=self.model,
            messages=self.history,
            max_tokens=300,
            temperature=0.7
        )

        # Extract reply
        reply = response.choices[0].message.content

        # Store assistant reply
        self.history.append(
            {
                "role": "assistant",
                "content": reply
            }
        )

        return reply

    # Clear conversation
    def clear(self):

        # Keep only system prompt
        self.history = [self.history[0]]

# ---------------- RUN CHATBOT ---------------- #

bot = Chatbot(
    "You are Charan's beginner-friendly AI mentor. "
    "Remember the user's name and explain simply."
)

print("\n🤖 AI Chatbot Ready!")
print("Type 'quit' to exit.")
print("Type 'clear' to reset memory.\n")

while True:

    user = input("You: ").strip()

    # Exit
    if user.lower() == "quit":
        print("\nGoodbye!\n")
        break

    # Clear memory
    if user.lower() == "clear":
        bot.clear()
        print("\n🧹 Memory Cleared!\n")
        continue

    # Generate reply
    try:
        reply = bot.chat(user)

        print(f"\n🤖 AI:\n{reply}\n")

    except Exception as e:
        print("\nERROR:\n")
        print(e)