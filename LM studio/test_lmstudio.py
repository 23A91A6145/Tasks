from openai import OpenAI

# Connect to LM Studio
client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"  # dummy key
)

# Send request to model
response = client.chat.completions.create(
    model="local-model",  # name doesn't matter
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain Python decorators in simple terms with example."}
    ],
    temperature=0.7,
    max_tokens=300
)

# Print output
print("\n🤖 AI Response:\n")
print(response.choices[0].message.content)

# Print token usage
print("\n📊 Tokens used:", response.usage.total_tokens)