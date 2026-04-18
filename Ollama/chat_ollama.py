import ollama

messages = []

while True:
    user = input("\nYou: ")
    if user.lower() in ['exit', 'quit']:
        break

    messages.append({'role': 'user', 'content': user})

    response = ollama.chat(
        model='qwen2.5:7b',
        messages=messages
    )

    reply = response['message']['content']
    print("AI:", reply)

    messages.append({'role': 'assistant', 'content': reply})