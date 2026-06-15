from langchain_ollama import OllamaLLM

llm = OllamaLLM(
    model="llama3.2:3b"
)

def review_code(prompt):
    return llm.invoke(prompt)