from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)
vector = model.encode("What is AI?")
print(len(vector)) 
print(vector)