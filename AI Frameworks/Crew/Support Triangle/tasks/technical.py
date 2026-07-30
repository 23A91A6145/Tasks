from crewai import Task

from config.settings import BASE_DIR
from agents.technical import TechnicalAgent

import yaml

TASKS_CONFIG_PATH = BASE_DIR / "config" / "tasks.yaml"


class TechnicalTask:
    def __init__(self, query: str):
        with open(TASKS_CONFIG_PATH) as f:
            config = yaml.safe_load(f)["technical_task"]

        agent = TechnicalAgent().get()

        self.task = Task(
            description=config["description"].format(query=query),
            expected_output=config["expected_output"],
            agent=agent,
        )

    def get(self) -> Task:
        return self.task
