import ollama
import time

# Models to compare
MODELS = ['llama3.2', 'phi3', 'qwen2.5:7b']

# Test prompts
PROMPTS = [
    "What is machine learning? Explain in 2 sentences.",
    "Write a Python function to reverse a string.",
    "What is the capital of Japan?"
]

results = {}

# Run benchmark
for model in MODELS:
    results[model] = []
    print(f"\n🔄 Testing {model}...\n")

    for prompt in PROMPTS:
        print(f"Prompt: {prompt}")

        start = time.time()

        response = ollama.chat(
            model=model,
            messages=[{'role': 'user', 'content': prompt}]
        )

        elapsed = time.time() - start
        reply = response['message']['content']

        word_count = len(reply.split())

        results[model].append({
            'prompt': prompt,
            'reply': reply,
            'time': elapsed,
            'words': word_count
        })

        print(f"✅ {elapsed:.1f}s | {word_count} words\n")

# Summary
print("\n\n📊 RESULTS SUMMARY")
print("=" * 60)

for model, data in results.items():
    avg_time = sum(d['time'] for d in data) / len(data)
    avg_words = sum(d['words'] for d in data) / len(data)

    print(f"{model:<12} → Avg Time: {avg_time:.1f}s | Avg Words: {avg_words:.0f}")