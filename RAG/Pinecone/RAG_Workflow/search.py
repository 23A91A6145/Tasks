from pinecone import Pinecone
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import os

# Load environment variables
load_dotenv()

# Embedding model
model = SentenceTransformer(
    "BAAI/bge-small-en-v1.5"
)

# Connect Pinecone
pc = Pinecone(
    api_key=os.getenv("PINECONE_API_KEY")
)

# Connect Index
index = pc.Index("rag-docs")

# Question
query = "What is Django?"

# Generate query embedding
query_embedding = model.encode(
    query
).tolist()

# Search
results = index.query(
    vector=query_embedding,
    top_k=3,
    include_metadata=True
)

# Display results nicely
for match in results["matches"]:

    print(f"\nScore: {match['score']:.2f}")

    print("\nText:")

    print(match["metadata"]["text"])

    print("-" * 50)