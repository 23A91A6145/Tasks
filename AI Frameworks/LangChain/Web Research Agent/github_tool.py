import requests


def search_github(query):

    try:

        url = (
            f"https://api.github.com/search/repositories"
            f"?q={query}"
        )

        response = requests.get(url)

        data = response.json()

        results = ""

        repos = data.get(
            "items",
            []
        )[:5]

        for index, repo in enumerate(
                repos,
                start=1
        ):

            results += (
                f"\nRepository {index}\n"
                f"Name: {repo['name']}\n"
                f"URL: {repo['html_url']}\n"
                f"Description: {repo['description']}\n"
            )

        return results

    except Exception as e:

        return (
            f"GitHub Error: {e}"
        )