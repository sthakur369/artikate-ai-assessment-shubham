from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-small-en-v1.5")

def embed_text(text):
    return model.encode(text).tolist()

def store_chunks(collection, chunks):
    documents = []
    embeddings = []
    ids = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        documents.append(chunk["text"])
        embeddings.append(embed_text(chunk["text"]))
        ids.append(str(i))
        metadatas.append({
            "document": chunk["document"],
            "page": chunk["page"]
        })

    collection.add(
        documents=documents,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )

def retrieve(collection, query, k=3):
    prefixed = f"Represent this sentence for searching relevant passages: {query}"
    query_embedding = embed_text(prefixed)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )

    return results
