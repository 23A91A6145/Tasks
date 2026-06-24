from crewai import Agent, LLM

llm = LLM(
    model="ollama/llama3.2:3b",
    base_url="http://localhost:11434"
)

twitter_agent = Agent(
    role="X Thread Creator",
    goal="Create engaging X threads.",
    backstory="Expert social media thread creator.",
    llm=llm,
    verbose=True,
    allow_delegation=False
)   