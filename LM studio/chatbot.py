from openai import OpenAI

# Connect to LM Studio
client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)

# 🧠 Conversation memory
history = [
    {
        "role": "system",
        "content": "You are a smart AI assistant. Be helpful, clear, and concise."
    }
]

print("💬 LM Studio Chatbot — type 'quit' to exit\n")

# 🔁 Chat loop
while True:
    user_msg = input("You: ")

    # Exit condition
    if user_msg.lower() in ["quit", "exit"]:
        print("👋 Goodbye!")
        break

    # Skip empty input
    if not user_msg.strip():
        continue

    # Add user message to memory
    history.append({"role": "user", "content": user_msg})

    print("AI: ", end="")

    full_reply = ""

    # ⚡ Streaming response
    for chunk in client.chat.completions.create(
        model="local-model",
        messages=history,
        stream=True,
        temperature=0.7
    ):
        content = chunk.choices[0].delta.content

        if content:
            print(content, end="", flush=True)
            full_reply += content

    print("\n")

    # Save AI response in memory
    history.append({"role": "assistant", "content": full_reply})