from pathlib import Path

from langchain_ollama import ChatOllama

from tools.search_tool import search_web


llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0
)

PROMPT_PATH = Path("prompts/research.txt")


def research_agent(query: str):

    print("\nSearching Web...\n")

    search_results = search_web(query)

    prompt_template = PROMPT_PATH.read_text(
        encoding="utf-8"
    )

    prompt = prompt_template.format(
        query=query,
        search_results=search_results
    )

    print("Analyzing Results...\n")

    response = llm.invoke(prompt)

    return response.content