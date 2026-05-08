import os
import json
import threading
from openai import OpenAI
from dotenv import load_dotenv

# Load API key
load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# Models
debate_models = [
    "google/gemma-2-9b-it",
    "deepseek/deepseek-r1",
    "openai/gpt-4o-mini"
]
judge_model = "openrouter/auto"
# Store responses
responses = {}
# Ask model function
def ask_model(model_name, question):

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant."
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            temperature=0.7
        )

        answer = response.choices[0].message.content

        responses[model_name] = answer

    except Exception as e:
        responses[model_name] = f"ERROR: {e}"

# User question
question = input("\n❓ Enter your question: ")

# Create threads
threads = []

for model in debate_models:

    t = threading.Thread(
        target=ask_model,
        args=(model, question)
    )

    threads.append(t)
    t.start()

# Wait for all
for t in threads:
    t.join()

# Display responses
print("\n⚖️ MODEL RESPONSES\n")

for model, answer in responses.items():

    print(f"\n🧠 MODEL: {model}\n")
    print(answer)
    print("-" * 60)

# Create judge prompt
judge_prompt = f"""
You are an expert AI judge.

Question:
{question}

Answers:

"""

for model, answer in responses.items():
    judge_prompt += f"\nMODEL: {model}\nANSWER:\n{answer}\n"

judge_prompt += """
Pick the BEST answer.

Explain:
1. Which model won
2. Why it won
3. Strengths and weaknesses of each answer
"""

# Judge response
judge_response = client.chat.completions.create(
    model=judge_model,
    messages=[
        {
            "role": "system",
            "content": "You are a strict AI evaluator."
        },
        {
            "role": "user",
            "content": judge_prompt
        }
    ],
    temperature=0.3
)

verdict = judge_response.choices[0].message.content

# Show verdict
print("\n🏆 JUDGE VERDICT\n")
print(verdict)

# Save to JSON
log_data = {
    "question": question,
    "responses": responses,
    "verdict": verdict
}

with open("debate_logs.json", "a", encoding="utf-8") as f:
    json.dump(log_data, f, indent=4)
    f.write("\n")

print("\n✅ Results saved to debate_logs.json")