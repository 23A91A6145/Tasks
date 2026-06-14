import json

MEMORY_FILE = "memory.json"


def load_memory():
    with open(MEMORY_FILE, "r") as file:
        return json.load(file)


def save_memory(memory):
    with open(MEMORY_FILE, "w") as file:
        json.dump(memory, file, indent=4)


def update_name(name):
    memory = load_memory()

    memory["name"] = name

    save_memory(memory)


def update_goal(goal):
    memory = load_memory()

    memory["goal"] = goal

    save_memory(memory)