from crewai import Task

from agents.seo import seo_agent
from tasks.research_task import research_task

seo_task = Task(
    description="""
    Analyze the research report.

    Create:

    - Primary Keywords
    - Secondary Keywords
    - Long Tail Keywords
    - Search Intent
    - SEO Strategy
    """,

    expected_output="""
    Complete SEO report.
    """,

    agent=seo_agent,

    context=[
        research_task
    ],

    output_file="outputs/seo.md"
)