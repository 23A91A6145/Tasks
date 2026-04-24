from openai import OpenAI
# Connect to LM Studio
client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)
# ✅ CHANGE THIS if needed (your model name)
MODEL_NAME = "llama-3.2-3b-instruct"
TONES = {
    "1": ("formal", "Professional and business-like"),
    "2": ("casual", "Friendly and conversational"),
    "3": ("urgent", "Clear urgency, action-oriented"),
    "4": ("apologetic", "Sincere and empathetic")
}
print("📧 AI Email Writer (LM Studio Powered)\n")
print("Tone options:")
for k, (name, desc) in TONES.items():
    print(f" {k}. {name} — {desc}")
tone_choice = input("\nPick tone (1-4): ")
tone_name, tone_desc = TONES.get(tone_choice, ("formal", "Professional"))

recipient = input("To (e.g. 'manager', 'client'): ")
purpose = input("What should the email say? (brief): ")

# 🧠 Prompt
prompt = f"""
Write a complete professional email.

Details:
- Recipient: {recipient}
- Tone: {tone_name} ({tone_desc})
- Purpose: {purpose}

Format:
Subject: <clear subject line>

<email body>

<professional sign-off>
"""

print("\n🤖 Generating email...\n")

# API call
response = client.chat.completions.create(
    model=MODEL_NAME,
    messages=[{"role": "user", "content": prompt}],
    temperature=0.6
)

email_output = response.choices[0].message.content

# Print result
print("="*50)
print(email_output)
print("="*50)

# Save option
save = input("\nSave to file? (y/n): ")

if save.lower() == "y":
    with open("draft_email.txt", "w", encoding="utf-8") as f:
        f.write(email_output)
    print("💾 Saved to draft_email.txt")