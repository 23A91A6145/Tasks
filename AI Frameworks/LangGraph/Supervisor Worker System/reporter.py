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
        "prompts/reporter.txt",
        "r",
        encoding="utf-8"
    ) as f:

        return f.read()


def run_reporter(
    query,
    research_data="",
    news_data="",
    web_data="",
    analysis_data=""
):

    prompt = f"""
{load_prompt()}

USER QUERY:

{query}

RESEARCH RESULTS:

{research_data}

NEWS RESULTS:

{news_data}

WEB RESULTS:

{web_data}

ANALYSIS RESULTS:

{analysis_data}
"""

    response = llm.invoke(prompt)

    report = response.content

    os.makedirs(
        "outputs/final_reports",
        exist_ok=True
    )

    filename = datetime.now().strftime(
        "%Y%m%d_%H%M%S_final_report.txt"
    )

    filepath = os.path.join(
        "outputs/final_reports",
        filename
    )

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(report)

    return report