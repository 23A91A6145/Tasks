from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper


search_tool = DuckDuckGoSearchRun()

wiki_tool = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(
        top_k_results=2,
        doc_content_chars_max=1000
    )
)


def safe_search(query):

    try:
        return search_tool.run(query)

    except Exception as e:

        return f"Search Error: {str(e)}"


def safe_wiki(query):

    try:
        return wiki_tool.run(query)

    except Exception:

        return "Wikipedia information unavailable."