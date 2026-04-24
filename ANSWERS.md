# Task 1 — Diagnose a Failing LLM Pipeline

---

## Problem 1 — Bot gives wrong pricing answers

**What I investigated first:**
Pricing errors that appear after launch with no prompt changes point to a knowledge
problem, not a logic problem. First thing to check is whether the pricing information
was ever in the prompt or if the model was expected to "know" it.

**What I ruled out:**
Temperature — high temperature causes creative/random answers, not confidently wrong
specific numbers. A model hallucinating "$49.99" with confidence is not a temperature
problem.

Prompt structure — if the prompt hasn't changed and it worked in testing, the prompt
format itself is not the issue.

**Root cause:**
Knowledge cutoff combined with no retrieval. GPT-4o's training data has a cutoff —
it doesn't know your current product prices. In testing this probably worked because
the test prices matched what the model had seen, or testers didn't catch wrong numbers.
In production, real users asked about real prices and the model either hallucinated
numbers or returned outdated ones confidently.

**Fix:**
Add a retrieval step before generation. Before the model responds to any pricing
question, fetch the current price from your database or pricing API and inject it
into the prompt as context. Instruct the model to only use provided pricing data
and say "I don't have that information" if no price is provided. Never rely on the
model's parametric memory for facts that change.

---

## Problem 2 — Bot responds in English to Hindi/Arabic users

**Mechanism:**
In a system prompt + user message architecture, the model pays strong attention to
the language of the system prompt. If your system prompt is written in English, the
model treats English as the "operating language" of the assistant. When a user writes
in Hindi or Arabic, the model sees a conflict — English instructions vs non-English
input — and often defaults to the instruction language, especially for longer or more
complex responses.

**Root cause:**
The system prompt has no explicit instruction about response language. The model is
making its own decision and choosing English because that's what the instructions are
written in.

**Fix — add this specific line to your system prompt:**
Always respond in the same language the user writes in.
If the user writes in Hindi, respond in Hindi.
If the user writes in Arabic, respond in Arabic.
Never switch languages unless the user switches first.

This is explicit, testable, and language-agnostic — it works for any language without
listing them all. You can test it by sending the same question in 5 different languages

and verifying the response language matches each time.

---

## Problem 3 — Response time degraded from 1.2s to 8-12s

**Three distinct causes:**

**1. Growing conversation history (most likely — investigate first)**
If the chatbot maintains conversation history per session and appends every message
to the context, the prompt gets longer with every turn. A longer prompt means more
tokens for the model to process, which directly increases latency. Over two weeks
with a growing user base, average session length probably increased. This is the
first thing to check because it requires no infrastructure access — just log the
average token count per request two weeks ago vs now.

**2. No caching on repeated questions**
Customer support bots receive the same questions repeatedly — "what are your hours",
"how do I return an item". Without a cache layer, every request goes to GPT-4o even
if it was answered 500 times already. As user volume grows, API call volume grows
linearly. Add semantic caching — store recent question-answer pairs and return cached
responses for similar questions without hitting the model.

**3. Infrastructure not scaling with load**
If the application server, database, or API gateway is not auto-scaling, increased
concurrent users cause queuing. Requests wait for available resources before even
reaching GPT-4o. Check server CPU/memory metrics and API gateway queue depth over
the same two week period.

**Why investigate context length first:**
It requires no infrastructure access, takes 10 minutes to check by looking at request
logs, and is the most common cause of gradual latency increase in LLM apps with no
code changes. Infrastructure issues tend to cause sudden spikes, not gradual
degradation over two weeks.

---

## Post-mortem Summary

Over the past two weeks, three issues emerged in our customer support chatbot.

On pricing accuracy — the bot was giving users wrong prices because it was relying
on its own internal knowledge rather than our live pricing data. The model was trained
at a fixed point in time and has no awareness of price changes after that. We are
fixing this by connecting the bot directly to our pricing database so it always pulls
current prices before responding.

On language — users writing in Hindi and Arabic were receiving English responses. This
happened because our setup instructions were written in English and the bot was
defaulting to that language. A one-line change to the instructions telling the bot to
always match the user's language has resolved this.

On speed — response times increased from around 1 second to 8-12 seconds as our user
base grew. The primary cause was the bot accumulating long conversation histories,
making each request progressively slower to process. We are implementing a limit on
conversation history length and adding a cache for common repeated questions, which
will bring response times back to acceptable levels.

None of these required changes to the core AI model — they are all fixable through
better prompt design, data integration, and infrastructure configuration.

-------------

# Task 2 - RAG

## Scaling to 50,000 Documents

At 50,000 documents averaging 40 pages each, the current pipeline breaks in three
specific places:

**1. Ingestion and embedding**

Right now we embed all chunks at startup in a single batch on CPU. At this scale
we're looking at tens of millions of chunks. Embedding that on CPU is not feasible.

Fix: move embedding to GPU batch processing, potentially distributed across multiple
workers for parallel ingestion. Run ingestion as an offline async pipeline — new
documents go into a queue, get embedded in batches, and are added to the vector
store incrementally. Ingestion and querying become separate processes.

**2. Vector store**

ChromaDB is a local persistent store. It works well up to a few hundred thousand
vectors but is not designed for tens of millions. Search latency will degrade and
it has no support for distributed deployment.

Fix: replace ChromaDB with Qdrant or Weaviate. Both use HNSW indexing which keeps
search latency low even at very large scale. Both support distributed deployment
and horizontal scaling. Qdrant specifically has good support for filtered search —
useful for searching within a specific contract or date range.

**3. Retrieval strategy**

At 50,000 NDAs and contracts, many documents will share nearly identical boilerplate
language. Pure vector search will struggle to distinguish the same clause appearing
across hundreds of similar contracts.

Fix: move to hybrid search — combine vector similarity with BM25 keyword search.
Vector search finds semantically relevant chunks, BM25 finds exact term matches.
Merge results using Reciprocal Rank Fusion. Add a cross-encoder re-ranker on top
to score the merged top-20 and return the best 3.

**4. Generation**

flan-t5-base has a 512 token input limit. With 3 chunks of dense legal text that
is already tight. At scale, complex questions may need more retrieved chunks as
context to answer correctly.

Fix: replace with a larger context model so more retrieved chunks can be passed
in a single generation call without truncation. This also improves instruction
following, which directly fixes the confidence scoring reliability issue we saw
with flan-t5-base refusing grounded answers.

---------------

# Task 3 — Classifier

## Model Choice

I used a fine-tuned DistilBERT model instead of an LLM.

Reason: latency.

- My model runs in ~40–130ms per request on CPU
- Requirement is <500ms → satisfied

If I used an LLM API:
- Network latency alone is ~300–800ms
- Not reliable for strict timing

So a local model is faster, more stable, and simpler.

---

## Latency & Throughput

- Avg time per ticket: ~50–100ms
- Max observed: ~130ms

System load:
- 2880 tickets/day (~1 every 30 sec)

Total compute:
2880 × 0.05s ≈ 144 seconds/day

Very low load → easily handled by one CPU server.

---

## Evaluation Results

- Accuracy: 0.93

Per-class F1:
- billing: 0.85
- technical_issue: 0.95
- feature_request: 0.96
- complaint: 0.92
- other: 0.94

---

## Confusion Analysis

### Most confused:
**complaint ↔ billing**

Example:
"I was charged twice and this is unacceptable"

- billing → "charged twice"
- complaint → emotional tone

Model has to pick one → ambiguity.

---

### Second confusion:
**billing ↔ technical_issue**

Example:
"Payment failed"

Could be:
- billing problem
- system issue

---

## Improvements

- Use multi-label classification (some tickets belong to multiple classes)
- Add sentiment signal (helps detect complaints)
- Use real data instead of only synthetic
- Add more mixed/ambiguous examples in training

---

## Data Note

Training data was synthetically generated with small variations.

This helps scale data, but:
- may not fully reflect real user behavior

Evaluation data was manually written to keep it realistic.

---

## Latency Test

Tested on 20 tickets:
- All predictions valid
- All under 500ms (mostly <150ms)

Test passed.

----

# Task 4 — Written Systems Design Review

## Question B — Evaluating LLM Output Quality

To evaluate a summarisation system, I would use a mix of automated metrics and human review.

**1. Metrics**
- ROUGE (measures overlap with reference summary)
- BERTScore (captures semantic similarity)

Limitations:
- ROUGE focuses on wording, not meaning
- BERTScore may miss factual errors or hallucinations

---

**2. Ground truth dataset**
- Collect ~100–200 real internal reports
- Write high-quality human summaries for each
- Include different types of reports (short, long, technical)

---

**3. Human evaluation**
- Rate summaries on:
  - correctness (is it factually right?)
  - completeness (are key points covered?)
  - clarity (is it readable?)
- Use a simple 1–5 scale

---

**4. Regression detection**
- Keep a fixed evaluation dataset
- Run evaluation after every model update
- Track metrics over time
- If scores drop → flag regression

---

**5. Communicating results**
Instead of raw metrics, explain like:
- “~90% of summaries are correct and complete”
- Show before/after examples
- Highlight common failure cases

---

**Limitation**
No single metric captures true quality. A combination of automated scores + human review is needed.

---

## Question C — On-Premise LLM Deployment

We need to run everything offline on a server with 2× A100 80GB GPUs and respond within 3 seconds.

---

**1. Model selection**

I would evaluate:
- LLaMA 3 (8B or 70B)
- Mistral 7B / Mixtral 8x7B

Given latency constraints, I would start with:
- **Mistral 7B or LLaMA 3 8B**

These are fast and fit comfortably on GPU.

---

**2. VRAM estimation**

Rough rule:
- 1 parameter ≈ 2 bytes (FP16)

So:
- 7B model → ~14GB  
- 8B model → ~16GB  

With KV cache + overhead → ~20–25GB total

👉 Easily fits in one A100 (80GB)

---

**3. Quantisation**

To improve speed and reduce memory:
- Use 4-bit or 8-bit quantisation (bitsandbytes or AWQ)

This reduces memory usage and increases throughput.

---

**4. Serving**

I would use:
- **vLLM** (best for throughput and batching)

Why:
- Efficient KV cache management
- Continuous batching → handles multiple requests well

Alternatives:
- TensorRT-LLM (high performance but more setup)
- llama.cpp (good for CPU, less relevant here)

---

**5. Expected performance**

- Latency: ~1–2 seconds for 500-token input  
- Throughput: multiple requests/sec with batching  

This satisfies the 3-second requirement.

---

**Limitations**

- Larger models (70B) may increase latency  
- Quantisation can slightly reduce quality  
- Requires careful GPU memory management  

So model size vs latency must be balanced.