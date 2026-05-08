import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)
prompt = """
Classify the sentiment:

Text: "I love this!"
Sentiment: POSITIVE

Text: "This is terrible"
Sentiment: NEGATIVE

Text: "It was okay I guess"
Sentiment:
"""
response = client.chat.completions.create(
    model="openrouter/auto",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0.1
)

print(response.choices[0].message.content)