import os
import warnings
warnings.filterwarnings("ignore")

import json
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
    
def load_test_data():
    with open("evaluation_data.json", "r") as f:
        return json.load(f)


def precision_at_k(k=3):
    pages = load_all_pdfs("data")
    chunks = chunk_text(pages)
    client, collection = get_collection()

    if collection.count() == 0:
        print("Storing chunks...")
        store_chunks(collection, chunks)

    test_data = load_test_data()
    correct = 0

    for item in test_data:
        question = item["question"]
        keyword = item["expected_keyword"]

        results = retrieve(collection, question, k)
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
            
    

        # print result in exact format from task doc
        print(f"\nQuestion: {question}")
        print("{")
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

        # check hit or miss
        found = any(keyword.lower() in doc.lower() for doc in docs)
        if found:
            correct += 1
            print(f">> HIT")
        else:
            print(f">> MISS")

    score = correct / len(test_data)
    print(f"\n{'='*50}")
    print(f"Precision@3: {correct}/{len(test_data)} = {score:.2f}")
    print(f"{'='*50}")


if __name__ == "__main__":
    precision_at_k()
