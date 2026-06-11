from pinecone import Pinecone
from dotenv import load_dotenv
import os

load_dotenv()

pc = Pinecone(
    api_key=os.getenv("PINECONE_API_KEY")
)

index = pc.Index("rag-docs")

vector = {
    "id": "test_chunk",

    "values": [0.1] * 384,

    "metadata": {
        "text": "This is a test chunk"
    }
}

index.upsert(vectors=[vector])

print("Vector Uploaded")