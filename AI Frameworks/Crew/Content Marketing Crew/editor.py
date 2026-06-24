from crewai import Agent, LLM

llm = LLM(
    model="ollama/llama3.2:3b",
    base_url="http://localhost:11434"
)

editor = Agent(
    role="Senior Editor",
    goal="Improve grammar, clarity and readability.",
    backstory="Professional editor.",
    llm=llm,
    verbose=True,
    allow_delegation=False
)