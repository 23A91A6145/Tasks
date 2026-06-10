from llama_index.embeddings.ollama import OllamaEmbedding
embed = OllamaEmbedding(
    model_name="nomic-embed-text"
)
vector = embed.get_query_embedding(
    "What is Artificial Intelligence?"
)
print(len(vector))

print(vector[:10])  # First 10 dimensions.