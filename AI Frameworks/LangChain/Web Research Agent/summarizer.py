from langchain_ollama import OllamaLLM
from prompts.research_prompt import RESEARCH_PROMPT


llm = OllamaLLM(
    model="llama3.2:3b"
)


def summarize_research(research_data):

    prompt = RESEARCH_PROMPT.format(
        research_data=research_data
    )

    response = llm.invoke(prompt)

    return response