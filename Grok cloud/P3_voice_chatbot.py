import os
import time
import pyttsx3

from groq import Groq
from dotenv import load_dotenv

# ========================================
# LOAD ENV
# ========================================

load_dotenv()

# ========================================
# GROQ CLIENT
# ========================================

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# ========================================
# TEXT TO SPEECH SETUP
# ========================================

tts = pyttsx3.init()

# Speech speed
tts.setProperty("rate", 175)

# Volume
tts.setProperty("volume", 0.9)

# ========================================
# CHAT MEMORY
# ========================================

messages = [
    {
        "role": "system",
        "content": (
            "You are a fast AI voice assistant. "
            "Keep responses under 50 words. "
            "Speak clearly and simply."
        )
    }
]

# ========================================
# START APP
# ========================================

print("=" * 50)
print("🎙️ REAL-TIME VOICE CHATBOT")
print("=" * 50)

print("\nType 'quit' anytime to stop.\n")

# ========================================
# MAIN LOOP
# ========================================

while True:

    # User input
    user_input = input("🧑 You: ")

    # Exit condition
    if user_input.lower() in ["quit", "exit", "bye"]:

        print("\n👋 Exiting chatbot...")
        break

    # Add user message
    messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    print("\n🤖 AI: ", end="", flush=True)

    full_reply = ""

    start_time = time.time()

    # ====================================
    # STREAM RESPONSE
    # ====================================

    stream = client.chat.completions.create(

        model="llama-3.1-8b-instant",

        messages=messages,

        max_tokens=120,

        temperature=0.7,

        stream=True
    )

    # Read stream chunks
    for chunk in stream:

        delta = chunk.choices[0].delta.content

        if delta:

            print(delta, end="", flush=True)

            full_reply += delta

    # Timing
    elapsed = time.time() - start_time

    print(f"\n\n⚡ Response Time: {elapsed:.2f}s\n")

    # Save assistant response
    messages.append(
        {
            "role": "assistant",
            "content": full_reply
        }
    )

    # ====================================
    # SPEAK RESPONSE
    # ====================================

    tts.say(full_reply)

    tts.runAndWait()