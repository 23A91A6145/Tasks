from crewai import Agent
from llm.local_llm import get_local_llm


def create_market_researcher():

    return Agent(
        role="Market Researcher",

        goal="""
        Analyze startup ideas and identify:

        - Market demand
        - Target customers
        - Competitors
        - Industry trends
        - Opportunities
        """,

        backstory="""
        You are a senior market researcher with
        15 years of startup validation experience.

        You identify market opportunities,
        customer pain points,
        and business demand.
        """,

        llm=get_local_llm(),

        verbose=True,

        allow_delegation=False
    )