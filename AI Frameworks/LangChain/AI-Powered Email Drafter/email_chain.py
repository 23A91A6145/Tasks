from langchain_ollama import ChatOllama

from prompts.email_prompt import email_prompt
from models.email_schema import EmailOutput

llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0.3
)

structured_llm = llm.with_structured_output(
    EmailOutput
)

email_chain = (
    email_prompt
    | structured_llm
)