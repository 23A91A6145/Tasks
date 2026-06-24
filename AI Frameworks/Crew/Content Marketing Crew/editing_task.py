from crewai import Task

from agents.editor import editor

from tasks.writing_task import writing_task

editing_task = Task(
    description="""
    Edit the blog.

    Improve:

    - Grammar
    - Clarity
    - Readability
    - Structure
    - SEO
    """,

    expected_output="""
    Publication ready article.
    """,

    agent=editor,

    context=[
        writing_task
    ]
)