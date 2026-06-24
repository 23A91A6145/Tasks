from crewai import Agent, LLM

llm = LLM(
    model="ollama/llama3.2:3b",
    base_url="http://localhost:11434"
)

writer = Agent(
    role="Content Writer",
    goal="Write engaging blog articles.",
    backstory="Technology content writer.",
    llm=llm,
    verbose=True,
    allow_delegation=False
)