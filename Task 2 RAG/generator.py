from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")


def generate_answer(question, retrieved_docs):
    context = "\n\n".join(retrieved_docs)

    prompt = f"""You are a document assistant.
Answer the question using ONLY the context below.
If the answer is not clearly stated in the context, say exactly: "I don't know".
Do not guess. Do not use outside knowledge.

Context:
{context}

Question:
{question}

Answer:"""



    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    outputs = model.generate(**inputs, max_new_tokens=150)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return answer