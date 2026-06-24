from crewai import Agent
from llm.local_llm import get_local_llm


def create_financial_analyst():

    return Agent(
        role="Financial Analyst",

        goal="""
        Analyze startup revenue potential,
        pricing strategy,
        profitability and business model.
        """,

        backstory="""
        Experienced startup finance consultant.

        You focus on realistic financial analysis.
        """,

        llm=get_local_llm(),

        verbose=True,

        allow_delegation=False
    )