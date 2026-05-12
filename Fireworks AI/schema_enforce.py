from fireworks.client import Fireworks
import os
import json
import re
from dotenv import load_dotenv

# Load API key
load_dotenv()

# Initialize client
client = Fireworks(
    api_key=os.getenv("FIREWORKS_API_KEY")
)

# Generate response
response = client.chat.completions.create(
    model="accounts/fireworks/models/qwen3-8b",
    messages=[
        {
            "role": "system",
            "content": """
Return ONLY valid JSON.
No explanations.
No markdown.
No thinking tags.
"""
        },
        {
            "role": "user",
            "content": """
Generate a product JSON with:
- product_name
- price
- category
- in_stock
- rating
"""
        }
    ],
    max_tokens=200,
    temperature=0.2
)

# Raw response
raw_text = response.choices[0].message.content

print("\nRAW AI RESPONSE:\n")
print(raw_text)

# -------------------------------
# Extract ONLY JSON object
# -------------------------------

match = re.search(r'\{.*\}', raw_text, re.DOTALL)

if match:
    clean_json = match.group(0)

    try:
        data = json.loads(clean_json)

        print("\nPARSED JSON:\n")

        print("Product:", data["product_name"])
        print("Price:", data["price"])
        print("Category:", data["category"])
        print("In Stock:", data["in_stock"])
        print("Rating:", data["rating"])

    except json.JSONDecodeError as e:
        print("\nJSON PARSE ERROR:")
        print(e)

else:
    print("\nNo valid JSON found.")