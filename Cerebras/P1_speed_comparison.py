import os
import time
import threading

from cerebras.cloud.sdk import Cerebras
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create clients
cerebras_client = Cerebras(
    api_key=os.environ.get("CEREBRAS_API_KEY")
)

groq_client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY")
)

# Store results
results = {}

# Prompt
prompt = "Explain quantum computing in 3 simple sentences."


# Cerebras benchmark
def test_cerebras():
    start = time.time()
    response = cerebras_client.chat.completions.create(
        model="llama3.1-8b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=200
    )
    elapsed = time.time() - start
    tokens = response.usage.total_tokens
    results["Cerebras"] = {
        "time": elapsed,
        "tokens": tokens,
        "speed": tokens / elapsed
    }


# Groq benchmark
def test_groq():

    start = time.time()

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=200
    )

    elapsed = time.time() - start

    tokens = response.usage.total_tokens

    results["Groq"] = {
        "time": elapsed,
        "tokens": tokens,
        "speed": tokens / elapsed
    }


# Create threads
t1 = threading.Thread(target=test_cerebras)
t2 = threading.Thread(target=test_groq)

# Start simultaneously
t1.start()
t2.start()

# Wait until complete
t1.join()
t2.join()

# Print results
print("\n⚡ AI SPEED COMPARISON\n")

for provider, data in results.items():

    print(f"{provider}")
    print("-" * 30)

    print(f"Time Taken : {data['time']:.2f} sec")
    print(f"Tokens Used: {data['tokens']}")
    print(f"Speed      : {data['speed']:.2f} tok/sec")

    print()