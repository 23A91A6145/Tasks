from openai import OpenAI

# Connect to LOCAL Ollama server
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama'   # dummy key
)

# Send request
response = client.chat.completions.create(
    model='qwen2.5:7b',
    messages=[
        {'role': 'user', 'content': 'Explain Python in 3 lines'}
    ]
)

# Print response
print(response.choices[0].message.content)