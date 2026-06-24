from crewai import Agent, LLM

llm = LLM(
    model="ollama/llama3.2:3b",
    base_url="http://localhost:11434"
)

seo_agent = Agent(
    role="SEO Specialist",
    goal="Create SEO strategies and keyword plans.",
    backstory="Expert SEO strategist.",
    llm=llm,
    verbose=True,
    allow_delegation=False
)