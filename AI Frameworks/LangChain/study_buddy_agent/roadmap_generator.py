import os


def save_roadmap(topic, content):

    os.makedirs(
        "roadmaps",
        exist_ok=True
    )

    filename = (
        f"roadmaps/"
        f"{topic.lower().replace(' ', '_')}_roadmap.txt"
    )

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(content)

    return filename