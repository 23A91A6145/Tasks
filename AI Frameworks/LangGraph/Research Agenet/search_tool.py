from ddgs import DDGS


def search_web(query: str, max_results: int = 5):

    results_text = []

    with DDGS() as ddgs:

        results = ddgs.text(
            query,
            max_results=max_results
        )

        for result in results:

            results_text.append(
                f"""
Title: {result.get('title', '')}

URL: {result.get('href', '')}

Body: {result.get('body', '')}
"""
            )

    return "\n\n".join(results_text)