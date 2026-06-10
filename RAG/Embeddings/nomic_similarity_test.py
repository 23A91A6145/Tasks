from sentence_transformers.util import cos_sim
from llama_index.embeddings.ollama import OllamaEmbedding

embed = OllamaEmbedding(
    model_name="nomic-embed-text"
)

dog = embed.get_query_embedding("Dog")

puppy = embed.get_query_embedding("Puppy")

tax = embed.get_query_embedding(
    "Income Tax"
)

print(
    cos_sim([dog],[puppy])
)
print( )
print(
    cos_sim([dog],[tax])
)