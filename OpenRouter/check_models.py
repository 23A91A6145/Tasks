import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API key
api_key = os.getenv("OPENROUTER_API_KEY")

# Request models
response = requests.get(
    "https://openrouter.ai/api/v1/models",
    headers={
        "Authorization": f"Bearer {api_key}"
    }
)

# Convert response to JSON
models = response.json()["data"]

# Filter free models
free_models = []

for model in models:
    try:
        if model["pricing"]["prompt"] == "0":
            free_models.append(model["id"])
    except:
        pass

# Print results
print(f"\n✅ Total Free Models: {len(free_models)}\n")

for model in free_models:
    print(model)