import asyncio
import time
import os

from groq import AsyncGroq
from dotenv import load_dotenv

# Load API key
load_dotenv()

# Create async client
client = AsyncGroq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Single async API call
async def single_call(prompt, task_id):

    print(f"🚀 Starting Task {task_id}")

    response = await client.chat.completions.create(
        model="llama-3.1-8b-instant",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        max_tokens=100,
        temperature=0.5
    )

    reply = response.choices[0].message.content

    print(f"✅ Task {task_id} Completed")

    return {
        "task_id": task_id,
        "reply": reply
    }

# Parallel execution function
async def run_parallel_calls():

    prompts = [
        f"Give one interesting fact about Indian city #{i+1}"
        for i in range(10)
    ]

    print("\n⚡ RUNNING PARALLEL AI CALLS")
    print("=" * 50)

    start_time = time.perf_counter()

    # Create all tasks
    tasks = [
        single_call(prompt, i + 1)
        for i, prompt in enumerate(prompts)
    ]

    # Run ALL tasks simultaneously
    results = await asyncio.gather(
        *tasks,
        return_exceptions=True
    )

    end_time = time.perf_counter()

    elapsed = round(end_time - start_time, 2)

    print("\n" + "=" * 50)
    print("📊 FINAL RESULTS")
    print("=" * 50)

    for result in results:

        if isinstance(result, Exception):
            print(f"❌ Error: {result}")
        else:
            print(
                f"\n🧠 Task {result['task_id']} Response:"
            )
            print(result['reply'][:120])

    print("\n" + "=" * 50)
    print(f"⚡ Total Time: {elapsed} sec")
    print(f"🚀 Parallel Speed Improvement Enabled!")
    print("=" * 50)

# Run async program
asyncio.run(run_parallel_calls())