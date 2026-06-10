from sentence_transformers import SentenceTransformer
model = SentenceTransformer(
    "BAAI/bge-large-en-v1.5"
)
vector = model.encode(
    "What is Artificial Intelligence?"
)
print(len(vector))