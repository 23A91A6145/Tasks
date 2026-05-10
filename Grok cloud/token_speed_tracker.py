import time
from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Function to test speed + token usage
def benchmark_model(model_name, prompt, max_tokens=150):

    print(f"\n🔍 Testing: {model_name}")

    start_time = time.perf_counter()

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=max_tokens,
        temperature=0.5
    )

    end_time = time.perf_counter()
    # Time taken
    elapsed_time = round(end_time - start_time, 3)
    # Usage data
    usage = response.usage

    input_tokens = usage.prompt_tokens
    output_tokens = usage.completion_tokens
    total_tokens = usage.total_tokens

    # Speed calculation
    tokens_per_second = round(
        output_tokens / elapsed_time, 1
    ) if elapsed_time > 0 else 0

    # AI reply
    ai_reply = response.choices[0].message.content

    # Print results
    print("-" * 50)
    print(f"⏱️ Time Taken      : {elapsed_time} sec")
    print(f"📥 Input Tokens    : {input_tokens}")
    print(f"📤 Output Tokens   : {output_tokens}")
    print(f"📊 Total Tokens    : {total_tokens}")
    print(f"⚡ Tokens / Second : {tokens_per_second}")
    print("-" * 50)

    print("\n🤖 AI Response:\n")
    print(ai_reply[:300])   # limit long output

    return {
        "model": model_name,
        "time": elapsed_time,
        "tokens_per_sec": tokens_per_second
    }


# Prompt for testing
prompt = """
Explain API Gateway with a simple Indian traffic police analogy.
"""

# Models to compare
models = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile"
]

print("\n🚀 GROQ MODEL BENCHMARK TOOL")
print("=" * 50)

# Run benchmark
results = []

for model in models:
    result = benchmark_model(model, prompt)
    results.append(result)

# Final Summary
print("\n📈 FINAL SPEED COMPARISON")
print("=" * 50)

for r in results:
    print(
        f"{r['model']} → "
        f"{r['time']} sec | "
        f"{r['tokens_per_sec']} tokens/sec"
    )

print("\n💡 8B = faster")
print("💡 70B = smarter")
print("💡 Choose based on your task!")