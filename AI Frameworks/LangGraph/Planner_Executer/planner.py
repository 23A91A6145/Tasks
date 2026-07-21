import os

from dotenv import load_dotenv

from langchain_groq import ChatGroq

from planner.prompts import PLANNER_SYSTEM_PROMPT

load_dotenv()

planner = ChatGroq(
    model=os.getenv("GROQ_MODEL"),
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

def create_plan(task: str):

    messages = [
        ("system", PLANNER_SYSTEM_PROMPT),
        ("human", task)
    ]

    response = planner.invoke(messages)

    return response.content