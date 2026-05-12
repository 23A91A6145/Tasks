import json
import re
import os

from typing import List, Optional, Literal

from dotenv import load_dotenv
from fireworks.client import Fireworks

from pydantic import (
    BaseModel,
    Field,
    ValidationError
)

# =========================================
# LOAD ENVIRONMENT VARIABLES
# =========================================

load_dotenv()

# =========================================
# INITIALIZE FIREWORKS CLIENT
# =========================================

client = Fireworks(
    api_key=os.getenv("FIREWORKS_API_KEY")
)

# =========================================
# PYDANTIC SCHEMA
# =========================================
class SentimentAnalysis(BaseModel):
    sentiment: Literal[
        "positive",
        "negative",
        "neutral",
        "mixed"
    ]
    score: float = Field(
        ge=-1.0,
        le=1.0
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0
    )

    key_emotions: List[str]

    reasoning: str

    actionable_insight: Optional[str] = None

# =========================================
# ANALYZE SENTIMENT FUNCTION
# =========================================

def analyze_sentiment(text: str):

    try:

        response = client.chat.completions.create(

            model="accounts/fireworks/models/qwen3-8b",

            messages=[

                {
                    "role": "system",

                    "content": """
You are a professional sentiment analysis AI.

STRICT RULES:
- Return ONLY valid JSON
- No markdown
- No explanations
- No thinking tags
"""
                },

                {
                    "role": "user",

                    "content": f"""
Analyze sentiment for this text:

{text}

Return JSON with:
- sentiment
- score
- confidence
- key_emotions
- reasoning
- actionable_insight
"""
                }
            ],

            response_format={
                "type": "json_object"
            },

            temperature=0.1,
            max_tokens=800
        )

        # =========================================
        # RAW RESPONSE
        # =========================================

        raw_text = response.choices[0].message.content

        print("\n==============================")
        print("RAW AI RESPONSE")
        print("==============================\n")

        print(raw_text)

        # =========================================
        # EXTRACT JSON SAFELY
        # =========================================

        match = re.search(
            r'\{.*\}',
            raw_text,
            re.DOTALL
        )

        if not match:
            raise ValueError(
                "No valid JSON found."
            )

        clean_json = match.group()

        # =========================================
        # PARSE JSON
        # =========================================

        parsed_data = json.loads(clean_json)

        # =========================================
        # PYDANTIC VALIDATION
        # =========================================

        validated = SentimentAnalysis(
            **parsed_data
        )

        return validated

    except ValidationError as ve:

        print("\nPYDANTIC VALIDATION ERROR:\n")
        print(ve)

    except json.JSONDecodeError as je:

        print("\nJSON ERROR:\n")
        print(je)

    except Exception as e:

        print("\nGENERAL ERROR:\n")
        print(e)

# =========================================
# TEST INPUT
# =========================================

sample_text = """
I love the new AI tools,
but they are too expensive
for students.
"""

# =========================================
# RUN ANALYSIS
# =========================================

result = analyze_sentiment(sample_text)

# =========================================
# DISPLAY RESULTS
# =========================================

if result:

    print("\n==============================")
    print("VALIDATED OUTPUT")
    print("==============================\n")

    print("Sentiment:", result.sentiment)

    print("Score:", result.score)

    print("Confidence:", result.confidence)

    print("Emotions:", result.key_emotions)

    print("Reasoning:", result.reasoning)

    print(
        "Actionable Insight:",
        result.actionable_insight
    )

    # =====================================
    # SAVE OUTPUT
    # =====================================

    os.makedirs(
        "outputs",
        exist_ok=True
    )

    with open(
        "outputs/sentiment_analysis.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result.model_dump(),
            file,
            indent=2
        )

    print("\nSaved successfully:")
    print(
        "outputs/sentiment_analysis.json"
    )