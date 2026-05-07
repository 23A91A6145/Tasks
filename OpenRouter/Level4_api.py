import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

def smart_ask(prompt, task_type="general"):
    model_map = {
        "general": "openrouter/auto",
        "complex": "openai/gpt-4o-mini",
        "math": "openrouter/auto",
        "fast": "google/gemma-2-9b-it",
        "long": "openrouter/auto"
    }

    model = model_map.get(task_type, model_map["general"])
    print(f"📡 Using: {model}")

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        return resp.choices[0].message.content

    except Exception as e:
        return f"❌ Error: {e}"


# Examples
print(smart_ask("What is Python?", "general"))
print(smart_ask("Solve: x² + 3x - 4 = 0", "math"))
print(smart_ask("Quick joke about programming", "fast"))