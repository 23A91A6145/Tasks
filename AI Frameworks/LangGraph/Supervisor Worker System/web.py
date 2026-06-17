import os
from datetime import datetime

import requests

from bs4 import BeautifulSoup

from langchain_ollama import ChatOllama


MODEL = "llama3.2:3b"

llm = ChatOllama(
    model=MODEL,
    temperature=0.2
)


def load_prompt():

    with open(
        "prompts/web.txt",
        "r",
        encoding="utf-8"
    ) as f:

        return f.read()


def extract_website(url):

    response = requests.get(
        url,
        timeout=20
    )

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    text = soup.get_text(
        separator=" ",
        strip=True
    )

    return text[:12000]


def run_web(url):

    website_text = extract_website(url)

    prompt = f"""
{load_prompt()}

Website:

{url}

Content:

{website_text}
"""

    response = llm.invoke(prompt)

    report = response.content

    os.makedirs(
        "outputs/web",
        exist_ok=True
    )

    filename = datetime.now().strftime(
        "%Y%m%d_%H%M%S_web.txt"
    )

    filepath = os.path.join(
        "outputs/web",
        filename
    )

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(report)

    return report