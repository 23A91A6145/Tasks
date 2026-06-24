from crewai import Task


def create_critic_task(agent, startup_idea):

    return Task(
        description=f"""
        Critically evaluate:

        {startup_idea}

        Identify:

        1. Risks
        2. Weaknesses
        3. Challenges
        4. Threats
        5. Missing Features

        Be brutally honest.
        """,

        expected_output="""
        Product Critique Report

        Risks

        Weaknesses

        Missing Features

        Threat Analysis

        Improvement Suggestions
        """,

        agent=agent
    )