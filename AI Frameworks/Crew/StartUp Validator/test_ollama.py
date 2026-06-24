from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3.2:3b"
)

response = llm.invoke("Hello")

print(response.content)