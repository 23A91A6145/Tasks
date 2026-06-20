from datetime import datetime

from graph.workflow import workflow


def main():

    result = workflow.invoke({

        "data": None,

        "validation_report": {},

        "status": "",

        "start_time": datetime.now(),

        "end_time": None,

        "metrics": {},

        "analysis": "",

        "quality_score": 0
    })

    print()
    print("=" * 60)
    print("ETLGUARDIAN-AI EXECUTION REPORT")
    print("=" * 60)

    for key, value in result["metrics"].items():

        print(
            f"{key}: {value}"
        )

    print()
    print("=" * 60)
    print("QUALITY SCORE")
    print("=" * 60)

    print(
        f"{result['quality_score']}%"
    )

    print()
    print("=" * 60)
    print("AI ANALYSIS")
    print("=" * 60)

    print(
        result["analysis"]
    )


if __name__ == "__main__":
    main()