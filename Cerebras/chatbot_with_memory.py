import os
from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Cerebras client
client = Cerebras(
    api_key=os.environ.get("CEREBRAS_API_KEY")
)

# Conversation memory
conversation_history = [
    {
        "role": "system",
        "content": "You are a helpful AI assistant named Kiran."
    }
]

# Chat function
def chat(user_message):

    # Store user message
    conversation_history.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    # Send full history
    response = client.chat.completions.create(
        model="llama3.1-8b",
        messages=conversation_history,
        max_tokens=512
    )

    # Extract AI response
    ai_message = response.choices[0].message.content

    # Store AI response
    conversation_history.append(
        {
            "role": "assistant",
            "content": ai_message
        }
    )

    return ai_message

# Chat loop
print("🤖 Chat with Kiran!")
print("Type 'quit' to exit.\n")

while True:

    user_input = input("You: ")

    if user_input.lower() == "quit":
        break

    response = chat(user_input)

    print(f"\nKiran: {response}\n")