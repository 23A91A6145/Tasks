from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer(
    "intfloat/multilingual-e5-large"
)

telugu = model.encode(
    "తెలంగాణ చరిత్ర"
)

english = model.encode(
    "History of Telangana"  # more accurate
)

score = cosine_similarity(
    [telugu],
    [english]
)

print(score)