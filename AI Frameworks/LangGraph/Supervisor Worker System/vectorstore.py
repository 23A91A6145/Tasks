import chromadb

from chromadb.utils import embedding_functions

DB_PATH = "chroma_db"

client = chromadb.PersistentClient(
    path=DB_PATH
)

embedding_function = (
    embedding_functions.DefaultEmbeddingFunction()
)

collection = client.get_or_create_collection(
    name="research_memory",
    embedding_function=embedding_function
)


def save_memory(
    document_text,
    document_id
):

    collection.add(
        documents=[document_text],
        ids=[document_id]
    )


def search_memory(
    query,
    n_results=3
):

    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    return results