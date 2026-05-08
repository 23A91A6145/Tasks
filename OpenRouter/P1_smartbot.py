import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# Available models
models = {
    1: "openrouter/auto",
    2: "google/gemma-2-9b-it",
    3: "openai/gpt-4o-mini",
    4: "deepseek/deepseek-r1",
    5: "openrouter/auto"
}

print("\n🤖 SMART Q&A BOT\n")

while True:

    # Show model menu
    print("\nChoose a model:\n")

    for num, model in models.items():
        print(f"{num}. {model}")

    # User chooses model
    try:
        choice = int(input("\nEnter model number: "))

        if choice not in models:
            print("❌ Invalid choice")
            continue

        selected_model = models[choice]

    except:
        print("❌ Please enter a valid number")
        continue

    # User question
    question = input("\n❓ Ask your question: ")

    try:

        # API request
        response = client.chat.completions.create(
            model=selected_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant."
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            temperature=0.7
        )

        # AI response
        answer = response.choices[0].message.content

        print("\n🤖 AI Response:\n")
        print(answer)

        # Token usage
        usage = response.usage

        print("\n📊 Token Usage:")
        print(f"Input Tokens:  {usage.prompt_tokens}")
        print(f"Output Tokens: {usage.completion_tokens}")
        print(f"Total Tokens:  {usage.total_tokens}")

        # Save to file
        with open("chat_history.txt", "a", encoding="utf-8") as file:
            file.write(f"\nMODEL: {selected_model}\n")
            file.write(f"QUESTION: {question}\n")
            file.write(f"ANSWER: {answer}\n")
            file.write("-" * 50 + "\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")

    # Continue?
    again = input("\nAsk another question? (y/n): ")

    if again.lower() != "y":
        print("\n👋 Goodbye!")
        break