import os
import time
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SmartRouter:

    # WORKING MODELS
    FREE_MODELS = {
        "general": "openrouter/auto",
        "smart": "openrouter/auto",
        "math": "deepseek/deepseek-r1",
        "fast": "openrouter/auto",
        "long": "openrouter/auto"
    }

    def __init__(self):

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY")
        )

        self.total_tokens = 0
        self.call_count = 0

    def chat(self, messages, task="general", max_retries=3):

        model = self.FREE_MODELS.get(
            task,
            self.FREE_MODELS["general"]
        )

        print(f"\n📡 TASK: {task.upper()}")
        print(f"🤖 MODEL: {model}")

        for attempt in range(max_retries):

            try:

                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.5
                )

                # Track usage
                if response.usage:
                    self.total_tokens += response.usage.total_tokens

                self.call_count += 1

                answer = response.choices[0].message.content

                return answer

            except Exception as e:

                print(f"\n⚠️ Attempt {attempt+1} failed")
                print(f"Error: {e}")

                if attempt < max_retries - 1:

                    wait_time = 2 ** attempt

                    print(f"⏳ Retrying in {wait_time} seconds...")

                    time.sleep(wait_time)

        return "❌ All retries failed."

    def stats(self):

        print("\n📊 SESSION STATS")
        print("-" * 30)

        print(f"API Calls: {self.call_count}")
        print(f"Total Tokens: {self.total_tokens}")


# Run App
if __name__ == "__main__":

    router = SmartRouter()

    # General Task
    msgs1 = [
        {
            "role": "user",
            "content": "Explain Python simply"
        }
    ]

    print("\n🤖 RESPONSE:")
    print(router.chat(msgs1, task="general"))

    # Math Task
    msgs2 = [
        {
            "role": "user",
            "content": "Solve: 2x + 5 = 13"
        }
    ]

    print("\n🧮 RESPONSE:")
    print(router.chat(msgs2, task="math"))

    # Stats
    router.stats()