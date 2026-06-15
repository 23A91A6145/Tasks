import wikipedia


def search_wikipedia(topic):

    try:

        wikipedia.set_lang("en")

        page = wikipedia.page(
            topic,
            auto_suggest=False
        )

        content = page.content[:3000]

        result = (
            f"\n{'='*50}\n"
            f"WIKIPEDIA RESULT\n"
            f"{'='*50}\n"
            f"Title: {page.title}\n"
            f"URL: {page.url}\n\n"
            f"{content}"
        )

        return result

    except wikipedia.exceptions.DisambiguationError as e:

        return (
            "Multiple topics found:\n"
            + ", ".join(e.options[:10])
        )

    except wikipedia.exceptions.PageError:

        return "Wikipedia page not found."

    except Exception as e:

        return f"Wikipedia Error: {str(e)}"