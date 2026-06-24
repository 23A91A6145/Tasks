from crewai import Agent, LLM

llm = LLM(
    model="ollama/llama3.2:3b",
    base_url="http://localhost:11434"
)

linkedin_agent = Agent(
    role="LinkedIn Content Creator",
    goal="Create engaging LinkedIn posts.",
    backstory="Expert LinkedIn creator.",
    llm=llm,
    verbose=True,
    allow_delegation=False
)