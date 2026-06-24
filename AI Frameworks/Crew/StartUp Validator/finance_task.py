from crewai import Task


def create_finance_task(agent, startup_idea):

    return Task(
        description=f"""
        Analyze the financial viability of:

        {startup_idea}

        Evaluate:

        1. Revenue potential
        2. Pricing strategy
        3. Business model
        4. Costs
        5. Profitability

        Give practical estimates.
        """,

        expected_output="""
        Financial Analysis Report

        Revenue Sources

        Pricing Model

        Startup Costs

        Profit Potential

        Risks

        Recommendation
        """,

        agent=agent
    )