# Artikate AI Assessment --- Shubham Thakur

This repository contains solutions for all sections of the Artikate AI
assessment.

------------------------------------------------------------------------

## Overview

The project is divided into the following tasks:

-   Task 1 --- Debugging an AI Chatbot\
-   Task 2 --- Legal Document RAG System\
-   Task 3 --- Support Ticket Classifier\
-   Task 4 --- Systems Design Review (written)\
-   Task 5 (Optional) --- RAG Demo Video

------------------------------------------------------------------------

## Task 1 --- Debugging an AI Chatbot

Covered in ANSWERS.md: - Root cause analysis\
- Failure explanation\
- Fixes and improvements

------------------------------------------------------------------------

## Task 2 --- RAG Pipeline

Features: - PDF ingestion\
- Paragraph-based chunking\
- BGE embeddings\
- ChromaDB vector store\
- Top-k retrieval\
- Grounded answer generation\
- Source citation\
- Safe refusal (no hallucination)

Run: cd task2_rag\
python main.py

Evaluation: python evaluation.py

------------------------------------------------------------------------

## Task 3 --- Ticket Classifier

Labels: - billing\
- technical_issue\
- feature_request\
- complaint\
- other

Model: - Fine-tuned DistilBERT\
- CPU inference (\<500ms)

Train: cd task3_classifier\
python train.py

Evaluate: python evaluate.py

Latency test: python test_latency.py

------------------------------------------------------------------------

## Task 4 --- Systems Design Review

Includes: - Evaluation framework\
- On-prem LLM deployment

------------------------------------------------------------------------

## Task 5 --- Optional Demo

Shows: - RAG pipeline\
- Evaluation\
- Safe refusal

------------------------------------------------------------------------

## Requirements

pip install -r requirements.txt

------------------------------------------------------------------------

## Structure

. ├── task2_rag/ ├── task3_classifier/ ├── DESIGN.md ├── ANSWERS.md ├──
README.md

------------------------------------------------------------------------

## Author

Shubham Thakur
