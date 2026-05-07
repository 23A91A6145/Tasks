import requests

BASE_URL = "http://localhost:3001"
API_KEY = "4MAVN8E-9T7MWMN-HRX4ZRM-HR06Z7Q"
WORKSPACE = "study-ai"

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

def ask_ai(question):
    response = requests.post(
        f"{BASE_URL}/api/v1/workspace/{WORKSPACE}/chat",
        headers=headers,
        json={"message": question, "mode": "chat"}
    )

    data = response.json()

    print("FULL RESPONSE:", data)

    return data.get("textResponse") or data.get("response") or "No response"

print(ask_ai("Explain normalization"))