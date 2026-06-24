from crewai import Task


def create_market_task(agent, startup_idea):

    return Task(
        description=f"""
        Analyze the startup idea:

        {startup_idea}

        Research:

        1. Target customers
        2. Market demand
        3. Customer pain points
        4. Existing competitors
        5. Market opportunities

        Provide realistic findings.
        """,

        expected_output="""
        Market Research Report

        Target Audience

        Market Demand

        Competitors

        Customer Problems

        Opportunities

        Final Summary
        """,

        agent=agent
    )