from graph.workflow import app


result = app.invoke(
    {
        "topic": "AI Agents",

        "draft": "",

        "review_notes": "",

        "reviewed": False,

        "human_feedback": "",

        "human_approved": False,

        "revision_count": 0,

        "published": False
    }
)

print("\n")
print("=" * 50)
print("FINAL STATE")
print("=" * 50)

print(result)