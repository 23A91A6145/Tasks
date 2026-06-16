from pathlib import Path

from langchain_ollama import ChatOllama


llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0
)

PROMPT_PATH = Path(
    "prompts/review.txt"
)


def reviewer_agent(report: str):

    prompt_template = PROMPT_PATH.read_text(
        encoding="utf-8"
    )

    prompt = prompt_template.format(
        report=report
    )

    response = llm.invoke(prompt)

    return response.content