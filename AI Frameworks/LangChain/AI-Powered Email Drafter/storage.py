import json
import os
from datetime import datetime

FILE_PATH = "data/email_history.json"


def load_history():

    if not os.path.exists(FILE_PATH):
        return []

    try:
        with open(FILE_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return []


def save_email(recipient, tone, subject, body):

    history = load_history()

    history.append(
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "recipient": recipient,
            "tone": tone,
            "subject": subject,
            "body": body
        }
    )

    with open(FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=4)


def clear_history():

    with open(FILE_PATH, "w", encoding="utf-8") as file:
        json.dump([], file)