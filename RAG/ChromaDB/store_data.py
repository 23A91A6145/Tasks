import chromadb

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="study_notes"
)

results = collection.query(
    query_texts=[
        "What is Django?"
    ],
    n_results=2
)

print(results)