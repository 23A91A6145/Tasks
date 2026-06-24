from crewai import Agent, LLM
from crewai_tools import SerperDevTool

llm = LLM(
    model="ollama/llama3.2:3b",
    base_url="http://localhost:11434"
)

search_tool = SerperDevTool()

researcher = Agent(
    role="Senior Research Analyst",
    goal="""
    Find accurate information,
    statistics, trends and sources.
    """,
    backstory="""
    Experienced researcher specializing
    in AI, technology and business.
    """,
    tools=[search_tool],
    llm=llm,
    verbose=True,
    allow_delegation=False,
    max_iter=5
)