from crewai import Task

from config.settings import BASE_DIR
from agents.billing import BillingAgent

import yaml

TASKS_CONFIG_PATH = BASE_DIR / "config" / "tasks.yaml"


class BillingTask:
    def __init__(self, query: str):
        with open(TASKS_CONFIG_PATH) as f:
            config = yaml.safe_load(f)["billing_task"]

        agent = BillingAgent().get()

        self.task = Task(
            description=config["description"].format(query=query),
            expected_output=config["expected_output"],
            agent=agent,
        )

    def get(self) -> Task:
        return self.task
