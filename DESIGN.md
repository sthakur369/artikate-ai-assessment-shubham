# RAG Pipeline Design — Legal Document QA System

## Problem Context

Legal documents are dense, clause-heavy, and use precise language. A question like
"What is the notice period?" needs to retrieve the exact clause, not a semantically
similar paragraph about something else. Hallucinated answers in legal context are
unacceptable — a wrong clause cited with confidence is worse than no answer at all.
Every design decision below is made with this in mind.

---

## Chunking Strategy

Chunk size: 50 words, overlap: 10 words.

Legal documents don't follow uniform paragraph lengths. A governing law clause can be
one sentence. An exceptions clause can be ten. If chunks are too large (300-400 words),
multiple clauses get merged into one chunk and retrieval becomes imprecise — the chunk
matches the query but the actual answer is buried inside it.

I started with 300-word chunks and the governing law clause ("This Agreement shall be
governed by the laws of Germany") was getting merged with the no-license and injunctive
relief sections on the same page. Retrieval was returning that chunk for completely
unrelated questions because it contained too many topics.

Dropping to 50 words meant each clause gets its own chunk. The governing law clause
now sits in its own retrievable unit. The 10-word overlap ensures a clause that spans
a chunk boundary still appears fully in at least one chunk.

The tradeoff is more chunks to store and search, but at this corpus size that's not
a concern.

---

## Embedding Model

Model: BAAI/bge-small-en-v1.5

I picked this from the MTEB leaderboard on HuggingFace, filtering by retrieval tasks.
BGE-small consistently ranks in the top tier for its size class on retrieval benchmarks.

The key reason to choose BGE over the more popular all-MiniLM-L6-v2 is that this is
an asymmetric retrieval task — a short natural language question matched against a long
dense legal clause. MiniLM was trained on symmetric pairs (similar length, similar
style). BGE was trained specifically for passage retrieval where query and document
are different in length and style.

BGE also supports a query prefix — "Represent this sentence for searching relevant
passages:" — which measurably improves retrieval quality on the query side without
changing how documents are stored.

Size is 130MB, runs fine on CPU, no API key needed, no authentication required.

---

## Vector Store

Choice: ChromaDB

ChromaDB stores vectors locally on disk as a persistent client. No server to run,
no Docker setup, no cloud dependency. For a corpus of 5 PDFs with ~200 chunks, it's
more than sufficient.

FAISS would be faster at search but it's in-memory only — you'd have to reload and
re-embed every time the process restarts. ChromaDB persists to disk so ingestion runs
once and retrieval is instant on subsequent runs.

Pinecone is a managed cloud service — requires an API key, internet connection, and
has cost implications at scale. That's unnecessary complexity for this use case.

Weaviate and Qdrant are production-grade stores with HNSW indexing that would make
sense at 50,000+ documents. At our scale they're overkill.

ChromaDB uses cosine similarity by default which is the right metric for normalized
text embeddings. We set hnsw:space to cosine explicitly to make this clear.

---

## Retrieval Strategy

Strategy: Naive top-k (k=3)

Vector similarity search — embed the query, find 3 closest chunks by cosine distance,
return them as context for generation.

At our corpus size (~200 chunks across 5 documents), this works well. Precision@3
across 10 test questions is 0.90, which means retrieval is finding the right chunk
9 out of 10 times. There's no evidence that a more complex strategy would meaningfully
improve this.

Hybrid search (vector + BM25 keyword) would help when documents share a lot of
boilerplate language and exact term matching matters — for example, distinguishing
"indemnification" from "liability" when both appear in similar contexts across many
contracts. We saw a mild version of this problem where multiple NDAs with similar
exception clauses confused retrieval. At 50,000 documents this would become a real
problem.

Re-ranking with a cross-encoder would add a second scoring pass over the top-k results.
More accurate but requires another model download and adds latency. Not justified at
this scale.

---

## Hallucination Mitigation

Two layers:

**Layer 1 — Prompt instruction**
The generation prompt explicitly says: "Answer using ONLY the context below. Do not
guess. Do not use outside knowledge. If the answer is not in the context, say I don't
know." This reduces hallucination at the source before the answer is even generated.

**Layer 2 — Confidence scoring with answer refusal**
After generation, we ask the same model: "Does this answer come directly from the
context? Reply with only yes or no." If the model says no, confidence is set to 0.0
and the answer is replaced with a refusal message instead of being shown to the user.

When asked "Who is the president of the US?" — a question with no relevant chunks —
the pipeline correctly refuses instead of generating an answer from training data.

Limitation: flan-t5-base is a small model and occasionally says "no" even when the
answer is grounded. This causes some correct answers to be refused unnecessarily. A
larger model would improve confidence scoring reliability. The refusal behavior is
still preferable to hallucination in a legal context — a false refusal is recoverable,
a hallucinated legal clause is not.