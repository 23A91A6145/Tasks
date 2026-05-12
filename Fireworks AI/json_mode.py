from fireworks.client import Fireworks
import os
import json
from dotenv import load_dotenv

# Load API key
load_dotenv()

# Initialize client
client = Fireworks(
    api_key=os.getenv("FIREWORKS_API_KEY")
)

# Prompt
response = client.chat.completions.create(
    model="accounts/fireworks/models/qwen3-8b",
    messages=[
        {
            "role": "system",
            "content": "You ONLY return valid JSON. No explanations. No thinking. No markdown."
        },
        {
            "role": "user",
            "content": """
Generate a student profile in JSON format with:
- name
- age
- skills (list)
- city
"""
        }
    ],
    max_tokens=200,
    temperature=0.3
)

# Raw output
raw_text = response.choices[0].message.content

print("\nRAW AI RESPONSE:\n")
print(raw_text)

# Convert JSON string → Python dictionary
try:
    data = json.loads(raw_text)

    print("\nPARSED JSON:\n")

    print("Name:", data["name"])
    print("Age:", data["age"])
    print("Skills:", data["skills"])
    print("City:", data["city"])

except json.JSONDecodeError as e:
    print("\nJSON ERROR:")
    print(e)