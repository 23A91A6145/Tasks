from agents.market_researcher import create_market_researcher

from tasks.market_task import create_market_task


agent = create_market_researcher()

task = create_market_task(
    agent,
    "AI Interview Coach for Freshers"
)

print(task)