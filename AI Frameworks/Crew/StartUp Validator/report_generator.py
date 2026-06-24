import json
from pathlib import Path


OUTPUT_DIR = Path("outputs")

OUTPUT_DIR.mkdir(exist_ok=True)


def save_txt_report(content):

    report_file = OUTPUT_DIR / "startup_report.txt"

    with open(
        report_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(str(content))

    return report_file


def save_json_report(content):

    report_file = OUTPUT_DIR / "startup_report.json"

    data = {
        "report": str(content)
    }

    with open(
        report_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )

    return report_file