import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

replanner = ChatGroq(
    model=os.getenv("GROQ_MODEL"),
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

SYSTEM_PROMPT = """
You are an AI Replanner.

Given:
- Original plan
- Failed step
- Failure reason

Generate a new execution plan.

Do not repeat completed work.

Return only the updated numbered plan.
"""

def replan(original_plan, failed_step, error):

    prompt = f"""
Original Plan:

{original_plan}

Failed Step:

{failed_step}

Failure:

{error}
"""

    response = replanner.invoke([
        ("system", SYSTEM_PROMPT),
        ("human", prompt)
    ])

    return response.content