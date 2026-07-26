import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

executor = ChatOllama(
    model=os.getenv("OLLAMA_MODEL"),
    base_url=os.getenv("OLLAMA_URL"),
    temperature=0
)

EXECUTOR_PROMPT = """
You are an AI Executor.

Complete ONLY the given execution step.

Do not create a new plan.

Return a concise, useful result.
"""

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def execute_step(step: str):

    messages = [
        ("system", EXECUTOR_PROMPT),
        ("human", step)
    ]

    response = executor.invoke(messages)

    return response.content
