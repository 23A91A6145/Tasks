import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError("❌ API key not found. Check your .env file.")

# Create client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

try:
    response = client.chat.completions.create(
        model="meta-llama/llama-3.2-3b-instruct",
        messages=[
            {"role": "user", "content": "Hello! What can you do?"}
        ],
        temperature=0.7,
        max_tokens=200
    )

    print("\n🤖 Response:\n")
    print(response.choices[0].message.content)

except Exception as e:
    print(f"\n❌ Error: {e}")