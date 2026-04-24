import os
import warnings
warnings.filterwarnings("ignore")

from ingestion import load_all_pdfs, chunk_text
from chroma_setup import get_collection
from retrieval import store_chunks, retrieve
from generator import generate_answer


def compute_confidence(answer, docs, question):
    context = "\n\n".join(docs)
    
    prompt = f"""Rate how well this answer is supported by the context on a scale of 0.0 to 1.0.
Return ONLY a number between 0.0 and 1.0. Nothing else.

Context:
{context}

Question: {question}
Answer: {answer}

Score:"""

    response = generate_answer(prompt, docs)
    
    try:
        score = float(response.strip())
        return round(min(max(score, 0.0), 1.0), 2)
    except:
        # if LLM returns something unparseable, fall back to 0.5
        return 0.5


def run_pipeline():
    pages = load_all_pdfs("data")
    chunks = chunk_text(pages)
    client, collection = get_collection()

    if collection.count() == 0:
        print("Storing chunks...")
        store_chunks(collection, chunks)

    while True:
        question = input("\nAsk a question: ")

        results = retrieve(collection, question)
        docs = results["documents"][0]
        metas = results["metadatas"][0]

        answer = generate_answer(question, docs)
        confidence = compute_confidence(answer, docs, question)

        # hallucination mitigation — if answer is not grounded in retrieved chunks, refuse
        if confidence < 0.3:
            answer = "I cannot confidently answer this from the provided documents. Please verify manually."

        
        sources = []

        for i in range(len(docs)):
            source = {
                "document": metas[i]["document"],
                "page": metas[i]["page"],
                "chunk": docs[i]
            }
            sources.append(source)
            
        # print in exact format from task doc
        print("\n{")
        print(f"  'answer': '{answer}',")
        print(f"  'sources': [")
        for s in sources:
            print(f"    {{")
            print(f"      'document': '{s['document']}',")
            print(f"      'page': {s['page']},")
            print(f"      'chunk': '{s['chunk'][:200]}...'")
            print(f"    }},")
        print(f"  ],")
        print(f"  'confidence': {confidence}")
        print("}")


if __name__ == "__main__":
    run_pipeline()