from ddgs import DDGS


def search_web(query, max_results=5):
    """
    Search DuckDuckGo
    """

    try:
        results = DDGS().text(
            query,
            max_results=max_results
        )

        formatted_results = ""

        for idx, result in enumerate(results, start=1):

            formatted_results += (
                f"\n{'='*50}\n"
                f"Result {idx}\n"
                f"{'='*50}\n"
                f"Title: {result.get('title', 'N/A')}\n"
                f"URL: {result.get('href', 'N/A')}\n"
                f"Snippet: {result.get('body', 'N/A')}\n"
            )

        return formatted_results

    except Exception as e:
        return f"Search Error: {str(e)}"