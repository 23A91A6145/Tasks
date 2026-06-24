from crewai import Task

from agents.linkedin import linkedin_agent

from tasks.editing_task import editing_task

linkedin_task = Task(
    description="""
    Convert article into a
    professional LinkedIn post.

    Include:

    - Hook
    - Insights
    - CTA
    """,

    expected_output="""
    LinkedIn post.
    """,

    agent=linkedin_agent,

    context=[
        editing_task
    ],

    output_file="outputs/linkedin.txt"
)