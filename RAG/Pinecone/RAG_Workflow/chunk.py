from pypdf import PdfReader

reader = PdfReader("./docs/introductiontodjango.pdf")

print("Pages:", len(reader.pages))

for i in range(3):
    print(f"\nPAGE {i+1}")
    print("-"*50)

    text = reader.pages[i].extract_text()

    print(text[:1000] if text else "NO TEXT")