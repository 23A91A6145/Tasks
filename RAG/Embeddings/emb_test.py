from llama_index.embeddings.huggingface import HuggingFaceEmbedding

embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)

vector = embed_model.get_query_embedding(
    "What is AI?"
)

print(len(vector))  # 384,  # print(vector)