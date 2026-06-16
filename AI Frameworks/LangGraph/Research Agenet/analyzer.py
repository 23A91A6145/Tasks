from pathlib import Path

from langchain_ollama import ChatOllama


llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0
)

PROMPT_PATH = Path(
    "prompts/analyze.txt"
)


def analyzer_agent(research_notes: str):

    prompt_template = PROMPT_PATH.read_text(
        encoding="utf-8"
    )

    prompt = prompt_template.format(
        research_notes=research_notes
    )

    response = llm.invoke(prompt)

    return response.content