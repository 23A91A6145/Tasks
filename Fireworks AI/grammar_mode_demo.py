import os
from dotenv import load_dotenv
from fireworks.client import Fireworks

# =========================================
# LOAD ENV VARIABLES
# =========================================

load_dotenv()

# =========================================
# INITIALIZE CLIENT
# =========================================

client = Fireworks(
    api_key=os.getenv("FIREWORKS_API_KEY")
)

# =========================================
# SIMPLE WORKING GRAMMAR
# =========================================

grammar = r"""
root ::= sentiment "\n" score

sentiment ::= "POSITIVE" | "NEGATIVE" | "NEUTRAL"

score ::= "SCORE: " number

number ::= "0.1" | "0.2" | "0.3" | "0.4" | "0.5" | "0.6" | "0.7" | "0.8" | "0.9" | "1.0"
"""

# =========================================
# AI REQUEST
# =========================================

try:

    response = client.chat.completions.create(

        model="accounts/fireworks/models/qwen3-8b",

        messages=[
            {
                "role": "system",

                "content": """
You are a sentiment analysis system.
Follow the grammar EXACTLY.
"""
            },

            {
                "role": "user",

                "content": """
Analyze this text:

"I love AI tools but they are expensive."
"""
            }
        ],

        response_format={
            "type": "grammar",
            "grammar": grammar
        },

        temperature=0.1,
        max_tokens=50
    )

    # =====================================
    # OUTPUT
    # =====================================

    print("\n==============================")
    print("GRAMMAR MODE OUTPUT")
    print("==============================\n")

    print(response.choices[0].message.content)

except Exception as e:

    print("\nERROR:\n")
    print(e)