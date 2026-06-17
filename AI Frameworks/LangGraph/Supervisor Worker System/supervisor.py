import json
from langchain_ollama import ChatOllama


MODEL = "llama3.2:3b"

llm = ChatOllama(
    model=MODEL,
    temperature=0
)


def load_prompt():
    with open(
        "prompts/supervisor.txt",
        "r",
        encoding="utf-8"
    ) as f:
        return f.read()


def get_default_decision():
    return {
        "research": False,
        "news": False,
        "web": False,
        "analyst": False,
        "reporter": False
    }


def clean_json_response(raw_text):
    """
    Extract JSON from LLM response safely.
    """

    start = raw_text.find("{")
    end = raw_text.rfind("}") + 1

    if start == -1 or end == 0:
        raise ValueError("No JSON object found")

    return raw_text[start:end]


def run_supervisor(query):

    prompt = f"""
{load_prompt()}

USER QUERY:
{query}

IMPORTANT RULES:

1. Return ONLY JSON.
2. No explanation.
3. No markdown.
4. No ```json blocks.
5. Every field must exist.

Required Format:

{{
    "research": true,
    "news": false,
    "web": false,
    "analyst": false,
    "reporter": false
}}
"""

    try:

        response = llm.invoke(prompt)

        raw = response.content.strip()

        json_text = clean_json_response(raw)

        data = json.loads(json_text)

        default = get_default_decision()

        for key in default:

            if key not in data:
                data[key] = False

        return data

    except Exception as e:

        print("\n====================")
        print("SUPERVISOR ERROR")
        print("====================")
        print(e)

        try:
            print("\nRAW RESPONSE:")
            print(raw)
        except:
            pass

        return get_default_decision()


if __name__ == "__main__":

    while True:

        query = input("\nEnter Query (q to quit): ")

        if query.lower() == "q":
            break

        decision = run_supervisor(query)

        print("\nSupervisor Decision:")
        print(json.dumps(decision, indent=4))