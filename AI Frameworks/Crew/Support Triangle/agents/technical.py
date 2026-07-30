from typing import Optional, List

from crewai import Agent
from crewai.tools import BaseTool

from config.settings import get_llm, BASE_DIR

import yaml

AGENTS_CONFIG_PATH = BASE_DIR / "config" / "agents.yaml"


class TechnicalAgent:
    def __init__(self, tools: Optional[List[BaseTool]] = None):
        with open(AGENTS_CONFIG_PATH) as f:
            config = yaml.safe_load(f)["technical_agent"]

        self.agent = Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            verbose=config["verbose"],
            allow_delegation=config["allow_delegation"],
            llm=get_llm(),
            tools=tools or [],
        )

    def get(self) -> Agent:
        return self.agent
