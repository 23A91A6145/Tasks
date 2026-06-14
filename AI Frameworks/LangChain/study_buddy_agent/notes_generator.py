import os


def save_notes(topic, content):

    os.makedirs("notes", exist_ok=True)

    filename = f"notes/{topic.lower().replace(' ', '_')}_notes.txt"

    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)

    return filename