import os
import time
import random
import logging

from groq import (
    Groq,
    RateLimitError,
    APIStatusError
)

from dotenv import load_dotenv
from functools import wraps

# Load API key
load_dotenv()

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s"
)

logger = logging.getLogger("GroqClient")

# Retry decorator
def with_retry(max_retries=5, base_delay=1):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            for attempt in range(max_retries):

                try:
                    return func(*args, **kwargs)

                except RateLimitError:

                    wait_time = (
                        base_delay * (2 ** attempt)
                        + random.uniform(0, 0.5)
                    )

                    logger.warning(
                        f"⚠️ Rate limit hit "
                        f"(Attempt {attempt+1}/{max_retries})"
                    )

                    logger.info(
                        f"⏳ Waiting {wait_time:.1f} sec..."
                    )

                    time.sleep(wait_time)

                except APIStatusError as e:

                    if e.status_code >= 500:

                        wait_time = base_delay * (2 ** attempt)

                        logger.warning(
                            f"⚠️ Server Error {e.status_code}"
                        )

                        logger.info(
                            f"⏳ Retrying in {wait_time:.1f} sec..."
                        )

                        time.sleep(wait_time)

                    else:
                        raise

            raise Exception("❌ Max retries exceeded.")

        return wrapper

    return decorator

# Production-ready client
class RobustGroqClient:

    def __init__(self):

        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

        self.total_calls = 0
        self.total_tokens = 0

    @with_retry(max_retries=5)
    def chat(self, prompt):

        self.total_calls += 1

        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            max_tokens=150,
            temperature=0.5
        )

        # Track tokens
        self.total_tokens += response.usage.total_tokens

        return response.choices[0].message.content

    def show_stats(self):

        print("\n📊 CLIENT STATS")
        print("=" * 40)

        print(f"📞 Total Calls  : {self.total_calls}")
        print(f"🧠 Total Tokens : {self.total_tokens}")

        print("=" * 40)

# Create AI client
ai = RobustGroqClient()

# Example prompts
prompts = [
    "What is Groq?",
    "Explain AI agents simply.",
    "What is an API?"
]

# Run prompts
for i, prompt in enumerate(prompts, start=1):

    print(f"\n🚀 Request {i}")
    print("-" * 40)

    try:

        result = ai.chat(prompt)

        print("🤖 AI Response:")
        print(result[:250])

    except Exception as e:

        print(f"❌ Failed: {e}")

# Show statistics
ai.show_stats()      