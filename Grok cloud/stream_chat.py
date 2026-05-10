import os
import time

from groq import Groq
from dotenv import load_dotenv

# Load API key
load_dotenv()

# Create Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Conversation memory
messages = [
    {
        "role": "system",
        "content": """
        You are Arya, a friendly AI mentor.
        Keep answers simple and helpful.
        """
    }
]

print("\n⚡ ARYA STREAMING CHAT")
print("Type 'quit' to exit.\n")

while True:

    # User input
    user_input = input("🧑 You: ")

    # Exit condition
    if user_input.lower() in ["quit", "exit"]:
        print("\n👋 Goodbye! Keep learning AI!")
        break

    # Save user message
    messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # Start timing
    start_time = time.perf_counter()

    first_token_time = None

    full_reply = ""

    print("\n🤖 Arya: ", end="", flush=True)

    # Streaming API call
    stream = client.chat.completions.create(
        model="llama-3.1-8b-instant",

        messages=messages,

        max_tokens=300,
        temperature=0.7,

        stream=True
    )

    # Process stream
    for chunk in stream:

        delta = chunk.choices[0].delta.content

        if delta:

            # Measure first token latency
            if first_token_time is None:
                first_token_time = (
                    time.perf_counter() - start_time
                )

            # Print instantly
            print(delta, end="", flush=True)

            # Save response
            full_reply += delta

    # Total response time
    total_time = (
        time.perf_counter() - start_time
    )

    # Save assistant reply
    messages.append(
        {
            "role": "assistant",
            "content": full_reply
        }
    )

    # Metrics
    print("\n")

    print("-" * 50)

    print(
        f"⚡ First Token: "
        f"{first_token_time:.3f} sec"
    )

    print(
        f"🕒 Total Time : "
        f"{total_time:.2f} sec"
    )

    print(
        f"🧠 Conversation Messages: "
        f"{len(messages)}"
    )

    print("-" * 50)