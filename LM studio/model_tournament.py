from openai import OpenAI
import time, json

# Connect to LM Studio
client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)

# ⚠️ Replace with your actual model name
MODEL_NAME = input("Enter current model name: ")

# Benchmark tasks
BENCHMARK_TASKS = [
    {"name": "factual", "prompt": "What is the boiling point of water in Celsius? Answer in 1 sentence only."},

    {"name": "coding", "prompt": "Write a Python function that checks if a number is prime. Include one example."},

    {"name": "reasoning", "prompt": "If 5 cats catch 5 mice in 5 minutes, how many cats to catch 100 mice in 100 minutes? Explain."},

    {"name": "creative", "prompt": "Write a 4-line poem about artificial intelligence learning."},

    {"name": "summary", "prompt": "Summarize in 2 sentences: Machine learning is a subset of AI that enables systems to learn from data and improve from experience without being explicitly programmed."}
]

results = {
    "model": MODEL_NAME,
    "tasks": []
}

print(f"\n🏆 Running benchmark for: {MODEL_NAME}\n")

# Run tasks
for task in BENCHMARK_TASKS:
    start = time.time()

    response = client.chat.completions.create(
        model=MODEL_NAME,   # ✅ FIXED (not local-model)
        messages=[{"role": "user", "content": task["prompt"]}],
        temperature=0.3,
        max_tokens=300
    )

    elapsed = round(time.time() - start, 2)
    reply = response.choices[0].message.content
    words = len(reply.split())

    results["tasks"].append({
        "task": task["name"],
        "time_sec": elapsed,
        "words": words,
        "response": reply
    })

    print(f"✅ {task['name']:12} | {elapsed}s | {words} words")

# Save report
filename = f"benchmark_{MODEL_NAME}.json"

with open(filename, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

# Average time
avg_time = sum([t["time_sec"] for t in results["tasks"]]) / len(BENCHMARK_TASKS)

print(f"\n📊 Avg response time: {avg_time:.2f}s")
print(f"💾 Report saved: {filename}")