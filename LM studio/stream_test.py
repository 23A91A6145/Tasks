from openai import OpenAI

# Connect to LM Studio
client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)

print("🤖 AI: ", end="")

# Streaming response    
for chunk in client.chat.completions.create(
    model="local-model",
    messages=[
        {"role": "user", "content": "Explain AI in simple terms"}
    ],
    stream=True  # 🔥 Enables streaming
):
    content = chunk.choices[0].delta.content
    
    if content:
        print(content, end="", flush=True)

print("\n\n✅ Done!")