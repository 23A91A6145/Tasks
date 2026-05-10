import os
import sys
import time

from groq import Groq
from dotenv import load_dotenv

# Load API key
load_dotenv()

# Create Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# User prompt
prompt = """
Write a short motivational poem about learning AI.
"""

print("\n🤖 AI Streaming Response:\n")
print("-" * 50)

# Start timer
start_time = time.perf_counter()

# Streaming API call
stream = client.chat.completions.create(
    model="llama-3.1-8b-instant",

    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],

    max_tokens=200,
    temperature=0.7,

    # Enable streaming
    stream=True
)

# Store full response
full_response = ""

# Receive streamed chunks
for chunk in stream:

    # Extract partial token
    delta = chunk.choices[0].delta.content

    if delta:

        # Print instantly
        print(delta, end="", flush=True)

        # Save response
        full_response += delta

# End timer
end_time = time.perf_counter()

elapsed = round(end_time - start_time, 2)

print("\n")
print("-" * 50)

# Stats
print(f"⚡ Stream Completed in: {elapsed} sec")
print(f"🧠 Total Characters: {len(full_response)}")

print("-" * 50)