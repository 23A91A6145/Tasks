from crewai import Task
from agents.researcher import researcher

research_task = Task(
    description="""
    Research the topic: {topic}

    Find:

    1. Latest trends
    2. Industry statistics
    3. Expert opinions
    4. Market insights
    5. Future opportunities

    Use reliable sources.
    """,

    expected_output="""
    Detailed research report with
    statistics, insights and references.
    """,

    agent=researcher,

    output_file="outputs/research.md"
)