from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path("outputs")

OUTPUT_DIR.mkdir(exist_ok=True)


def save_file(filename, content):

    filepath = OUTPUT_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(str(content))

    return filepath


def save_log(topic):

    log_file = OUTPUT_DIR / "run_log.txt"

    with open(log_file, "a", encoding="utf-8") as f:

        f.write(
            f"\n{datetime.now()} - {topic}\n"
        )