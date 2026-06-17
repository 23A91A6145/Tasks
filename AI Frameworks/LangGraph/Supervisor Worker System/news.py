from duckduckgo_search import DDGS
from langchain_ollama import ChatOllama

import os
from datetime import datetime


MODEL = "llama3.2:3b"

llm = ChatOllama(
    model=MODEL,
    temperature=0.2
)


def load_prompt():

    with open(
        "prompts/news.txt",
        "r",
        encoding="utf-8"
    ) as f:

        return f.read()


def search_news(query):

    results = []

    with DDGS() as ddgs:

        search_results = ddgs.text(
            query,
            max_results=5
        )

        for item in search_results:

            results.append(
                f"""
Title:
{item.get('title','')}

Body:
{item.get('body','')}

Link:
{item.get('href','')}
"""
            )

    return "\n".join(results)


def run_news(query):

    news_data = search_news(query)

    prompt = f"""
{load_prompt()}

Topic:

{query}

News Results:

{news_data}
"""

    response = llm.invoke(prompt)

    report = response.content

    os.makedirs(
        "outputs/news",
        exist_ok=True
    )

    filename = datetime.now().strftime(
        "%Y%m%d_%H%M%S_news.txt"
    )

    filepath = os.path.join(
        "outputs/news",
        filename
    )

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(report)

    return report