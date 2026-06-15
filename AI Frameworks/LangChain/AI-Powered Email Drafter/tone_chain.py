from langchain_ollama import ChatOllama

from prompts.tone_prompt import tone_prompt


llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0
)

tone_chain = tone_prompt | llm