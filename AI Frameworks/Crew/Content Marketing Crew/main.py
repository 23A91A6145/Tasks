from crew import content_marketing_crew
from utils.file_manager import save_file, save_log


def run():

    topic = input(
        "\nEnter Blog Topic: "
    )

    result = content_marketing_crew.kickoff(
        inputs={
            "topic": topic
        }
    )

    save_file(
        "final_result.md",
        str(result)
    )

    save_log(topic)

    print("\n")
    print("=" * 60)
    print("RESULT SAVED")
    print("=" * 60)
    print("\nSaved To:")
    print("outputs/final_result.md")


if __name__ == "__main__":
    run()   