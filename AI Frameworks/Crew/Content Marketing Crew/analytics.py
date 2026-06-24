from pathlib import Path


def file_word_count(path):

    file_path = Path(path)

    if not file_path.exists():
        return 0

    text = file_path.read_text(
        encoding="utf-8"
    )

    return len(text.split())