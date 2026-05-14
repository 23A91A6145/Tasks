import os
from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create client
client = Cerebras(
    api_key=os.environ.get("CEREBRAS_API_KEY")
)

print("🤖 AI: ", end="", flush=True)

# Streaming response
stream = client.chat.completions.create(
    model="llama3.1-8b",
    messages=[
        {
            "role": "user",
            "content": "Write a short poem about coding."
        }
    ],
    max_tokens=300,
    stream=True
)

# Print streamed tokens
for chunk in stream:

    # Check content exists
    if chunk.choices[0].delta.content:

        print(
            chunk.choices[0].delta.content,
            end="",
            flush=True
        )

print()