import time
from sentence_transformers import SentenceTransformer
model = SentenceTransformer(
    "BAAI/bge-large-en-v1.5"
)
start = time.time()
vector = model.encode(
    "What is AI?"
)
end = time.time()

print(end-start)