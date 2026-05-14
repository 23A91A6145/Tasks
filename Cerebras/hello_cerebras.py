import os
from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create client
client = Cerebras(
    api_key=os.environ.get("CEREBRAS_API_KEY")
)

# Send request
response = client.chat.completions.create(
    model="llama3.1-8b",
    messages=[
        {
            "role": "user",
            "content": "Explain AI in simple words."
        }
    ],
    max_tokens=200
)

# Print result
print(response.choices[0].message.content)