import os
from datetime import datetime

from langchain_ollama import ChatOllama


MODEL = "llama3.2:3b"

llm = ChatOllama(
    model=MODEL,
    temperature=0.3
)


def load_prompt():

    with open(
        "prompts/research.txt",
        "r",
        encoding="utf-8"
    ) as f:

        return f.read()


def run_research(query):

    prompt = f"""
{load_prompt()}

Topic:

{query}
"""

    response = llm.invoke(prompt)

    report = response.content

    os.makedirs(
        "outputs/reports",
        exist_ok=True
    )

    filename = datetime.now().strftime(
        "%Y%m%d_%H%M%S.txt"
    )

    filepath = os.path.join(
        "outputs/reports",
        filename
    )

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(report)

    return report