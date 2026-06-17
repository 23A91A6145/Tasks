import os
from datetime import datetime

from langchain_ollama import ChatOllama


MODEL = "llama3.2:3b"

llm = ChatOllama(
    model=MODEL,
    temperature=0.2
)


def load_prompt():

    with open(
        "prompts/analyst.txt",
        "r",
        encoding="utf-8"
    ) as f:

        return f.read()


def run_analysis(
    query,
    research_data="",
    news_data="",
    web_data=""
):

    prompt = f"""
{load_prompt()}

USER QUERY:

{query}

RESEARCH FINDINGS:

{research_data}

NEWS FINDINGS:

{news_data}

WEB FINDINGS:

{web_data}
"""

    response = llm.invoke(prompt)

    report = response.content

    os.makedirs(
        "outputs/analysis",
        exist_ok=True
    )

    filename = datetime.now().strftime(
        "%Y%m%d_%H%M%S_analysis.txt"
    )

    filepath = os.path.join(
        "outputs/analysis",
        filename
    )

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(report)

    return report