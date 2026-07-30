from crewai import Task

from config.settings import BASE_DIR
from agents.validator import ValidatorAgent

import yaml

TASKS_CONFIG_PATH = BASE_DIR / "config" / "tasks.yaml"


class ValidationTask:
    def __init__(self, query: str, response: str):
        with open(TASKS_CONFIG_PATH) as f:
            config = yaml.safe_load(f)["validation_task"]

        agent = ValidatorAgent().get()

        self.task = Task(
            description=config["description"].format(query=query, response=response),
            expected_output=config["expected_output"],
            agent=agent,
        )

    def get(self) -> Task:
        return self.task
