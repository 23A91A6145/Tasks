from crewai import Crew, Process

from agents.market_researcher import create_market_researcher
from agents.financial_analyst import create_financial_analyst
from agents.product_critic import create_product_critic

from tasks.market_task import create_market_task
from tasks.finance_task import create_finance_task
from tasks.critic_task import create_critic_task


def create_validator_crew(startup_idea):

    market_agent = create_market_researcher()

    finance_agent = create_financial_analyst()

    critic_agent = create_product_critic()

    market_task = create_market_task(
        market_agent,
        startup_idea
    )

    finance_task = create_finance_task(
        finance_agent,
        startup_idea
    )

    critic_task = create_critic_task(
        critic_agent,
        startup_idea
    )

    return Crew(
        agents=[
            market_agent,
            finance_agent,
            critic_agent
        ],
        tasks=[
            market_task,
            finance_task,
            critic_task
        ],
        process=Process.sequential,
        verbose=True
    )