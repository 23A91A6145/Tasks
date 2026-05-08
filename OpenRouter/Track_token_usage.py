import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)
messages = [
    {"role": "user", "content": "Explain AI in simple terms"}
]
response = client.chat.completions.create(
    model="openrouter/auto",
    messages=messages
)
# Response text
print("\n🤖 Response:")
print(response.choices[0].message.content)
# Token usage
usage = response.usage
print("\n📊 Token Usage:")
print(f"Input tokens:  {usage.prompt_tokens}")
print(f"Output tokens: {usage.completion_tokens}")
print(f"Total tokens:  {usage.total_tokens}")