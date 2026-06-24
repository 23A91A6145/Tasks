from crewai import LLM


def get_local_llm():
    return LLM(
        model="ollama/llama3.2:3b",
        base_url="http://localhost:11434"
    )