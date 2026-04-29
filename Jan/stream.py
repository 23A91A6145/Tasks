from openai import OpenAI

# Initialize client
client = OpenAI(
    base_url="http://localhost:1337/v1",
    api_key="jan"
)

# Function for streaming response
def chat_stream(prompt, model_name="local-model"):
    print(f"\n🤖 {model_name}: ", end="")

    try:
        stream = client.chat.completions.create(
            model=model_name,   # keep this as local-model for stability
            messages=[
                {"role": "system", "content": "You are a helpful teacher."},
                {"role": "user", "content": prompt}
            ],
            stream=True
        )

        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                print(content, end="", flush=True)

        print("\n")

    except Exception as e:
        print("\n❌ Error:", e)


# ---- MULTIPLE QUERIES ----
chat_stream("Explain AI in 3 points")
chat_stream("What is Machine Learning?")
chat_stream("Explain Python in simple terms")