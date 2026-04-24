import fitz

import fitz
import os

def load_all_pdfs(folder_path):
    all_pages = []

    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            file_path = os.path.join(folder_path, file)
            doc = fitz.open(file_path)

            for i, page in enumerate(doc):
                text = page.get_text()

                all_pages.append({
                    "document": file,
                    "page": i + 1,
                    "text": text
                })

    return all_pages
    
    

def chunk_text(pages, chunk_size=50, overlap=10):
    chunks = []

    for page in pages:
        words = page["text"].split()

        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            
            chunks.append({
    "document": page["document"],
    "page": page["page"],
    "text": chunk
})

    return chunks