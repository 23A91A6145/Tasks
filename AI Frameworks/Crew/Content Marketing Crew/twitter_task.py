from crewai import Task

from agents.twitter import twitter_agent

from tasks.editing_task import editing_task

twitter_task = Task(
    description="""
    Convert article into
    an X thread.

    Include:

    - Hook
    - Thread
    - CTA
    """,

    expected_output="""
    X Thread.
    """,

    agent=twitter_agent,

    context=[
        editing_task
    ],

    output_file="outputs/twitter.txt"
)