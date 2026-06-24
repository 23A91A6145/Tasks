from crewai import Task

from agents.writer import writer

from tasks.research_task import research_task
from tasks.seo_task import seo_task

writing_task = Task(
    description="""
    Write a professional blog article.

    Requirements:

    - Engaging title
    - Introduction
    - Headings
    - Subheadings
    - Conclusion
    - CTA

    Minimum 1200 words.
    """,

    expected_output="""
    Complete markdown blog article.
    """,

    agent=writer,

    context=[
        research_task,
        seo_task
    ],

    output_file="outputs/blog.md"
)