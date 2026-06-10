import chromadb

client = chromadb.PersistentClient(
    path="../chroma_db"
)

collection = client.get_collection(
    "study_notes"
)

print("\nCollection Name:")
print(collection.name)

print("\nTotal Chunks:")
print(collection.count())