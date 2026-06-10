import chromadb

client = chromadb.PersistentClient(
    path="../chroma_db"
)

collection = client.get_collection(
    "study_notes"
)

question = input(
    "Ask Question: "
)

results = collection.query(
    query_texts=[question],
    n_results=3
)

print("\nRESULTS\n")

for doc in results["documents"][0]:
    print(doc)
    print("="*50)