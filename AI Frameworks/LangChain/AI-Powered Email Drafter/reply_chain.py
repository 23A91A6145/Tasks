from langchain_ollama import ChatOllama

from prompts.reply_prompt import reply_prompt
from models.reply_schema import ReplyOutput


llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0.3
)

structured_llm = llm.with_structured_output(
    ReplyOutput
)

reply_chain = (
    reply_prompt
    | structured_llm
)