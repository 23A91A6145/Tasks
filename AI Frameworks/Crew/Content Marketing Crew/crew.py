from crewai import Crew, Process

from agents.researcher import researcher
from agents.seo import seo_agent
from agents.writer import writer
from agents.editor import editor
from agents.linkedin import linkedin_agent
from agents.twitter import twitter_agent

from tasks.research_task import research_task
from tasks.seo_task import seo_task
from tasks.writing_task import writing_task
from tasks.editing_task import editing_task
from tasks.linkedin_task import linkedin_task
from tasks.twitter_task import twitter_task


content_marketing_crew = Crew(
    agents=[
        researcher,
        seo_agent,
        writer,
        editor,
        linkedin_agent,
        twitter_agent
    ],

    tasks=[
        research_task,
        seo_task,
        writing_task,
        editing_task,
        linkedin_task,
        twitter_task
    ],

    process=Process.sequential,

    verbose=True
)