import requests

url = "http://localhost:11434/api/chat"

messages = []

while True:
    user = input("\nYou: ")
    if user.lower() in ['exit', 'quit']:
        break

    messages.append({"role": "user", "content": user})

    data = {
        "model": "qwen2.5:7b",
        "messages": messages,
        "stream": False
    }

    response = requests.post(url, json=data)
    result = response.json()

    reply = result['message']['content']
    print("AI:", reply)

    messages.append({"role": "assistant", "content": reply})