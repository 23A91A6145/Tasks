import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize client
client = Groq()

chat = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "user",
            "content": "Explain what Groq is in 2 sentences."
        }
    ],
    max_tokens=200
)

print(chat.choices[0].message.content)