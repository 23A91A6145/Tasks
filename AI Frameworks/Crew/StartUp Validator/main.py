from crews.validator_crew import create_validator_crew

from reports.report_generator import (
    save_txt_report,
    save_json_report
)


def main():

    startup_idea = input(
        "\nEnter Startup Idea: "
    )

    crew = create_validator_crew(
        startup_idea
    )

    print(
        "\nRunning Startup Validation...\n"
    )

    result = crew.kickoff()

    print("\n")

    print("=" * 80)

    print(
        "STARTUP VALIDATION REPORT"
    )

    print("=" * 80)

    print(result)

    txt_path = save_txt_report(
        result
    )

    json_path = save_json_report(
        result
    )

    print("\n")

    print(
        f"TXT Saved : {txt_path}"
    )

    print(
        f"JSON Saved : {json_path}"
    )


if __name__ == "__main__":
    main()