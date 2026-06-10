from pathlib import Path
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb

PDF_FOLDER = Path("../data")

client = chromadb.PersistentClient(
    path="../chroma_db"
)

collection = client.get_or_create_collection(
    name="study_notes"
)

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

CHUNK_SIZE = 500

for pdf_file in PDF_FOLDER.glob("*.pdf"):

    print(f"Processing {pdf_file.name}")

    reader = PdfReader(pdf_file)

    for page_num, page in enumerate(reader.pages):

        text = page.extract_text()

        if not text:
            continue

        chunks = [
            text[i:i+CHUNK_SIZE]
            for i in range(
                0,
                len(text),
                CHUNK_SIZE
            )
        ]

        for idx, chunk in enumerate(chunks):

            embedding = model.encode(
                chunk
            ).tolist()

            collection.add(
                documents=[chunk],

                embeddings=[embedding],

                metadatas=[
                    {
                        "source": pdf_file.name,
                        "page": page_num + 1
                    }
                ],

                ids=[
                    f"{pdf_file.stem}_{page_num}_{idx}"
                ]
            )

print("Done")