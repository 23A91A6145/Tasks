from agents.supervisor import run_supervisor

from agents.researcher import run_research
from agents.news import run_news
from agents.web import run_web
from agents.analyst import run_analysis
from agents.reporter import run_reporter


def main():

    query = input(
        "\nEnter Query: "
    )

    decision = run_supervisor(query)

    print("\nSupervisor Decision:\n")
    print(decision)

    research_result = ""
    news_result = ""
    web_result = ""
    analysis_result = ""

    print("\n========================")
    print("WORKER EXECUTION")
    print("========================\n")

    if decision["research"]:

        print("\n[Research Worker]\n")

        research_result = run_research(query)

    if decision["news"]:

        print("\n[News Worker]\n")

        news_result = run_news(query)

    if decision["web"]:

        print("\n[Web Worker]\n")

        url = input(
            "\nEnter Website URL: "
        )

        web_result = run_web(url)

    if decision["analyst"]:

        print("\n[Analyst Worker]\n")

        analysis_result = run_analysis(
            query=query,
            research_data=research_result,
            news_data=news_result,
            web_data=web_result
        )

    if decision["reporter"]:

        print("\n[Reporter Worker]\n")

        final_report = run_reporter(
            query=query,
            research_data=research_result,
            news_data=news_result,
            web_data=web_result,
            analysis_data=analysis_result
        )

        print(final_report)


if __name__ == "__main__":
    main()