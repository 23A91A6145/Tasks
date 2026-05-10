import os
from groq import Groq
from dotenv import load_dotenv

# Load API key
load_dotenv()

# Create Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Function to test AI behavior
def test_temperature(prompt, temperatures):

    print("\n" + "=" * 60)
    print(f"📌 PROMPT:\n{prompt}")
    print("=" * 60)

    for temp in temperatures:

        print(f"\n🌡️ Temperature: {temp}")
        print("-" * 40)

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            # Main parameters
            temperature=temp,
            max_tokens=120,
            top_p=0.9,

            # Optional stop sequence
            stop=["\n\n"],

            # Reproducibility
            seed=42 if temp == 0 else None
        )

        reply = response.choices[0].message.content
        finish_reason = response.choices[0].finish_reason

        print(f"🤖 Response:\n{reply}\n")
        print(f"🛑 Finish Reason: {finish_reason}")

# Test 1 — Creative prompt
test_temperature(
    prompt="Continue this sci-fi story: 'The robot woke up in Hyderabad railway station...'",
    temperatures=[0.0, 0.7, 1.3]
)

# Test 2 — Factual prompt
test_temperature(
    prompt="What is the capital of India?",
    temperatures=[0.0, 1.0]
)

# Parameter Guide
print("\n" + "=" * 60)
print("📚 PARAMETER GUIDE")
print("=" * 60)

print("""
temperature = 0.0
→ factual, stable, deterministic

temperature = 0.7
→ balanced chatbot behavior

temperature = 1.2+
→ creative writing + brainstorming

max_tokens
→ controls response size

top_p
→ controls token probability selection

seed
→ reproducible outputs

stop
→ tells AI where to stop generating
""")