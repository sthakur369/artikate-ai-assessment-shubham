# Artikate AI Assessment

This repository contains solutions for all sections of the Artikate AI assessment.

---

## 📌 Overview

The project is divided into the following tasks:

- **Task 1** — Debugging an AI Chatbot  
- **Task 2** — Legal Document RAG System  
- **Task 3** — Support Ticket Classifier  
- **Task 4** — Systems Design Review (Written)  
- **Task 5** — Loom Video  

https://www.loom.com/share/ddc47343219b4e9a8ef07b4eb1c12e88

---

## 🧠 Task 1 — Debugging an AI Chatbot

Details and solutions are documented in:

```
ANSWERS.md
```

---

## 📚 Task 2 — RAG Pipeline

### ✨ Features

- PDF ingestion  
- Paragraph-based chunking  
- BGE embeddings  
- ChromaDB vector store  
- Top-k retrieval  
- Grounded answer generation  
- Source citation  
- Safe refusal (prevents hallucination)  

### ▶️ How to Run

```bash
cd task2_rag
python main.py
```

### 📊 Evaluation

```bash
python evaluation.py
```

---

## 🎯 Task 3 — Ticket Classifier

### 🏷️ Labels

- billing  
- technical_issue  
- feature_request  
- complaint  
- other  

### 🤖 Model

- Fine-tuned DistilBERT  
- CPU inference (<500ms)  

### ▶️ Training

```bash
cd task3_classifier
python train.py
```

### 📊 Evaluation

```bash
python evaluate.py
```

### ⚡ Latency Test

```bash
python test_latency.py
```

---

## 🏗️ Task 4 — Systems Design Review

You can find it here

```
ANSWERS.md
```

---


## ⚙️ Requirements

Install dependencies using:

```bash
pip install -r requirements.txt
```

---

## 📂 Project Structure

```
.
├── task2_rag/
├── task3_classifier/
├── DESIGN.md
├── ANSWERS.md
└── README.md
```

---
