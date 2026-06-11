from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from sentence_transformers import SentenceTransformer

documents = SimpleDirectoryReader("./docs").load_data()

splitter = SentenceSplitter(
    chunk_size=512,
    chunk_overlap=50
)

nodes = splitter.get_nodes_from_documents(
    documents
)

model = SentenceTransformer(
    "BAAI/bge-small-en-v1.5"
)

texts = [node.text for node in nodes]

embeddings = model.encode(texts)

print("Documents:", len(documents))
print("Chunks:", len(nodes))
print("Embeddings:", len(embeddings))
print("Dimension:", len(embeddings[0]))
print("First embedding:", embeddings[0][:5])