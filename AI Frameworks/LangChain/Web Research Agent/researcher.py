from tools.search_tool import search_web
from tools.wiki_tool import search_wikipedia

from tools.github_tool import search_github
from tools.arxiv_tool import search_arxiv

from chains.summarizer import (
    summarize_research
)


def run_agent(query):

    search_results = search_web(query)

    wiki_results = search_wikipedia(query)

    github_results = search_github(query)

    arxiv_results = search_arxiv(query)

    combined_research = (

        "WEB SEARCH\n"
        + search_results

        + "\n\n"

        + "WIKIPEDIA\n"
        + wiki_results

        + "\n\n"

        + "GITHUB\n"
        + github_results

        + "\n\n"

        + "ARXIV\n"
        + arxiv_results
    )

    summary = summarize_research(
        combined_research
    )

    return summary