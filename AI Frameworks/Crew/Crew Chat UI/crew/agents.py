import os

from crewai import Agent
from crew.config import settings

_agents: dict[str, Agent] = {}


def _build_llm():
    if settings.provider == "ollama":
        os.environ["OLLAMA_API_BASE"] = settings.OLLAMA_BASE_URL
        return f"ollama/{settings.OLLAMA_MODEL_NAME}"
    return None


_llm = _build_llm()


def create_researcher() -> Agent:
    if "researcher" not in _agents:
        _agents["researcher"] = Agent(
            role="Research Specialist",
            goal="Gather relevant, accurate, and up-to-date information to answer the user's query",
            backstory=(
                "You are a senior research analyst with expertise across multiple domains. "
                "You excel at finding relevant information, verifying facts, and organizing "
                "data into a clear, structured format. You provide comprehensive context "
                "so downstream agents can produce the best possible response."
            ),
            llm=_llm,
            verbose=settings.CREW_VERBOSE,
            allow_delegation=False,
        )
    return _agents["researcher"]


def create_analyst() -> Agent:
    if "analyst" not in _agents:
        _agents["analyst"] = Agent(
            role="Analysis Expert",
            goal="Analyze gathered information and extract key insights relevant to the user's question",
            backstory=(
                "You are a sharp analytical thinker who breaks down complex information "
                "into clear, logical patterns. You identify trends, connections, and "
                "implications that might not be obvious at first glance. Your analysis "
                "bridges raw data and actionable answers."
            ),
            llm=_llm,
            verbose=settings.CREW_VERBOSE,
            allow_delegation=False,
        )
    return _agents["analyst"]


def create_writer() -> Agent:
    if "writer" not in _agents:
        _agents["writer"] = Agent(
            role="Response Writer",
            goal="Synthesize research and analysis into a clear, helpful, and well-structured final response",
            backstory=(
                "You are an expert communicator who transforms complex information into "
                "engaging, accessible content. You structure responses with clarity, "
                "use appropriate formatting (headings, bullet points, code blocks), "
                "and tailor your tone to the user's needs. You ensure every response "
                "is complete, accurate, and directly answers the user's question."
            ),
            llm=_llm,
            verbose=settings.CREW_VERBOSE,
            allow_delegation=False,
        )
    return _agents["writer"]


def get_all_agents() -> list[Agent]:
    return [create_researcher(), create_analyst(), create_writer()]


def reset_agents() -> None:
    _agents.clear()
