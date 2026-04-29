from openai import OpenAI
import datetime

# Connect to Jan API
client = OpenAI(
    base_url="http://localhost:1337/v1",
    api_key="jan"
)

# Prompt template
PLANNER_PROMPT = """
You are a productivity coach.

Analyze these tasks and return:

## TASK ANALYSIS
Total Tasks: [count]
Estimated Total Time: [hours]

## HIGH PRIORITY
- Important tasks

## MEDIUM PRIORITY
- Other tasks

## PRODUCTIVITY TIPS
- 3 tips

## SCHEDULE
- Simple plan

TASKS:
{tasks}
"""

print(f"\n📅 AI Daily Planner — {datetime.date.today()}")
print("=" * 40)

print("\nEnter tasks (press ENTER twice to stop):\n")

tasks = []

# Take input
while True:
    t = input(f"Task {len(tasks)+1}: ")
    if not t.strip():
        break
    tasks.append(f"- {t}")

if not tasks:
    print("No tasks entered!")
    exit()

task_str = "\n".join(tasks)
prompt = PLANNER_PROMPT.format(tasks=task_str)

print(f"\n🤖 Analyzing {len(tasks)} tasks...\n")

# Call Jan API
try:
    for chunk in client.chat.completions.create(
        model="local-model",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        stream=True
    ):
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)

    print("\n")

except Exception as e:
    print("\n❌ ERROR:", e)
    print("👉 Fix: Open Jan → Load model → Type 'hello'")