import os
from dotenv import load_dotenv
from together import Together

# Load environment variables
load_dotenv()

# Get API key safely
api_key = os.getenv("TOGETHER_API_KEY")

# Check if key exists
if not api_key:
    print("❌ API key not found.")
    print("Create a .env file and add:")
    print("TOGETHER_API_KEY=your_key")
    exit()

# Create Together client
client = Together(api_key=api_key)

print("🚀 Sending request to Together AI...\n")

try:
    # Send chat request
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI tutor."
            },
            {
                "role": "user",
                "content": "Explain AI agents simply for beginners."
            }
        ],
        max_tokens=200,
        temperature=0.7,
    )

    # Print response
    print("🤖 AI RESPONSE:\n")
    print(response.choices[0].message.content)

except Exception as e:
    print("❌ Error occurred:")
    print(e)