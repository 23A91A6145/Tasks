from crewai import Agent
from llm.local_llm import get_local_llm


def create_product_critic():

    return Agent(
        role="Product Critic",

        goal="""
        Identify weaknesses,
        risks,
        threats,
        missing features
        and product flaws.
        """,

        backstory="""
        You are a brutally honest product reviewer.

        Your job is to find flaws
        before customers do.
        """,

        llm=get_local_llm(),

        verbose=True,

        allow_delegation=False
    )