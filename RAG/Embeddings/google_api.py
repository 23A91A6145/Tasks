import google.generativeai as genai

genai.configure(
    api_key="YOUR_KEY"
)

result = genai.embed_content(
    model="models/text-embedding-004",
    content="What is AI?"
)

print(len(result["embedding"]))