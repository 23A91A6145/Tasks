from openai import OpenAI
import datetime
# Connect to LM Studio
client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)
PROMPT_TEMPLATE = """
You are a study assistant.
Create exactly 10 flashcards about: {topic}
Format EXACTLY like this (no extra text):
Q1: [Question]
A1: [Answer]
Q2: [Question]
A2: [Answer]
...
Q10: [Question]
A10: [Answer]
Make questions test understanding, not just memory.
Vary difficulty: 3 easy, 4 medium, 3 hard.
"""
print("📚 LM Studio Study Assistant")
print("="*40)

topic = input("Enter study topic: ")
level = input("Your level (beginner/intermediate/expert): ")

prompt = PROMPT_TEMPLATE.format(topic=f"{topic} for {level} level")

print(f"\n🤖 Generating flashcards for '{topic}'...\n")

# ✅ FIXED MODEL NAME HERE
response = client.chat.completions.create(
    model="llama-3.2-3b-instruct",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.3,
    max_tokens=1000
)

flashcards = response.choices[0].message.content

print(flashcards)

filename = f"flashcards_{topic.replace(' ','_')}_{datetime.date.today()}.txt"

with open(filename, "w", encoding="utf-8") as f:
    f.write(f"Topic: {topic}\nLevel: {level}\n\n{flashcards}")

print(f"\n💾 Saved to: {filename}")
print("🎓 Happy studying!")