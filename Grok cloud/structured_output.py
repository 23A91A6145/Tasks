import os
import json

from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Model Router
def pick_model(task_type):

    routing = {

        "quick": "llama-3.1-8b-instant",

        "quality": "llama-3.3-70b-versatile",

        "math": "deepseek-r1-distill-llama-70b",

        "multilang": "mixtral-8x7b-32768"
    }

    return routing.get(
        task_type,
        "llama-3.1-8b-instant"
    )

# Structured extraction function
def extract_structured(text):

    prompt = f"""
    Extract information from this text.

    Return ONLY valid JSON.

    {{
      "name": "",
      "email": "",
      "phone": "",
      "company": "",
      "sentiment": "",
      "summary": ""
    }}

    Text:
    {text}
    """

    response = client.chat.completions.create(

        model=pick_model("quality"),

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.1,
        max_tokens=300
    )

    raw = response.choices[0].message.content.strip()

    try:

        data = json.loads(raw)

        return data

    except json.JSONDecodeError:

        return {
            "error": "Invalid JSON",
            "raw_output": raw
        }

# Sample input
sample = """
Hi, I'm Priya Sharma from Hyderabad.

Email:
priya@startup.in

Phone:
9876543210

Interested in AI consulting.
"""

# Run extraction
result = extract_structured(sample)

# Pretty print result
print("\n📊 STRUCTURED OUTPUT\n")

print(
    json.dumps(
        result,
        indent=4
    )
)