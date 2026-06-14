import os


def save_quiz(topic, content):

    os.makedirs("quizzes", exist_ok=True)

    filename = f"quizzes/{topic.lower().replace(' ', '_')}_quiz.txt"

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(content)

    return filename