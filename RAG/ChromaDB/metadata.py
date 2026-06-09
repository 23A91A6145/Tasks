import chromadb

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="study_notes"
)

collection.add(
    documents=[
        "Python is a programming language",
        "Django is a Python web framework",
        "RAG means Retrieval Augmented Generation",
        "Chroma is a vector database"
    ],

    ids=[
        "doc1",
        "doc2",
        "doc3",
        "doc4"
    ],

    metadatas=[
        {
            "category":"python",
            "difficulty":"beginner"
        },

        {
            "category":"python",
            "difficulty":"intermediate"
        },

        {
            "category":"ai",
            "difficulty":"beginner"
        },

        {
            "category":"ai",
            "difficulty":"intermediate"
        }
    ]
)

print("Documents stored with metadata")