import os
import time

from groq import Groq
from openai import OpenAI
from dotenv import load_dotenv

# -----------------------------------
# LOAD ENV VARIABLES
# -----------------------------------

load_dotenv()

# -----------------------------------
# GROQ CLIENT
# -----------------------------------

groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# -----------------------------------
# OPENROUTER CLIENT
# -----------------------------------

openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# -----------------------------------
# TEST PROMPT
# -----------------------------------

prompt = "Explain Machine Learning in 2 simple sentences."

# ===================================
# GROQ TEST
# ===================================
print("\n🚀 Testing Groq...\n")
groq_start = time.perf_counter()
groq_response = groq_client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    max_tokens=100
)
groq_time = time.perf_counter() - groq_start
groq_text = groq_response.choices[0].message.content
# ===================================
# OPENROUTER TEST
# ===================================

print("🐢 Testing OpenRouter...\n")

openrouter_start = time.perf_counter()

openrouter_response = openrouter_client.chat.completions.create(

    # FIXED MODEL
    model="meta-llama/llama-3-8b-instruct",

    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],

    max_tokens=100
)

openrouter_time = time.perf_counter() - openrouter_start

openrouter_text = openrouter_response.choices[0].message.content

# ===================================
# RESULTS
# ===================================

print("\n" + "=" * 50)
print("📊 AI SPEED COMPARISON")
print("=" * 50)

print(f"\n📝 Prompt:\n{prompt}")

# GROQ
print("\n🚀 GROQ")
print(f"⚡ Time: {groq_time:.2f} sec")
print("🧠 Model: llama-3.1-8b-instant")

# OPENROUTER
print("\n🐢 OPENROUTER")
print(f"⚡ Time: {openrouter_time:.2f} sec")
print("🧠 Model: meta-llama/llama-3-8b-instruct")

# WINNER
if groq_time < openrouter_time:

    speedup = round(openrouter_time / groq_time, 1)

    print(f"\n🏆 Winner: GROQ")
    print(f"⚡ {speedup}x Faster")

else:

    speedup = round(groq_time / openrouter_time, 1)

    print(f"\n🏆 Winner: OPENROUTER")
    print(f"⚡ {speedup}x Faster")

print("\n" + "=" * 50)

# OPTIONAL OUTPUTS
print("\n📌 GROQ RESPONSE:\n")
print(groq_text)

print("\n📌 OPENROUTER RESPONSE:\n")
print(openrouter_text)

print("\n✅ Benchmark Complete!")