import arxiv


def search_arxiv(query):

    try:

        search = arxiv.Search(
            query=query,
            max_results=5
        )

        results = ""

        for index, paper in enumerate(
                search.results(),
                start=1
        ):

            results += (
                f"\nPaper {index}\n"
                f"Title: {paper.title}\n"
                f"Authors: "
                f"{', '.join(str(a) for a in paper.authors)}\n"
                f"Summary: {paper.summary[:500]}\n"
            )

        return results

    except Exception as e:

        return (
            f"ArXiv Error: {e}"
        )