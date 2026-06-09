import chromadb

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_collection(
    "study_notes"
)

results = collection.query(
    query_texts=[
        "What is RAG?"
    ],

    where={
        "category":"ai"
    },

    n_results=2
)

print(results)
