# ANSWERS

---

# Task 1 — Diagnose a Failing LLM Pipeline

## Problem 1 — Wrong pricing answers

**What I will investigate first:**
Pricing errors after launch with no prompt changes point to a knowledge problem.
First check was pricing ever explicitly provided in the prompt, or the model need to search it from somewhere?

**What I ruled out:**
Temperature — that causes random variation, not confidently wrong specific numbers.

Prompt structure — it hadn't changed and worked in testing, so this is not the issue.

**Root cause:**
GPT-4o doesn't know your current prices. In testing this
probably passed because testers used prices the model had seen, or didn't catch
wrong numbers. Real users in production asked about real prices and got hallucinated
or outdated ones stated confidently.

**Fix:**
Add a retrieval step. Before responding to any pricing question, fetch the current
price from your database and inject it into the prompt. Tell the model to only use
provided data and say "I don't have that information" if none is provided.

---

## Problem 2 — Responding in English to Hindi/Arabic users

**Mechanism:**
The model pays strong attention to the language of the system prompt. If instructions
are in English, it treats English as the operating language. When the user writes in
Hindi or Arabic, there's a conflict — and the model defaults to the instruction
language, especially for longer responses.

**Root cause:**
No explicit language instruction in the system prompt. In testing maybe tester did not use another language so it did not come under testing time.

**Fix — add this to your system prompt:**

Always respond in the same language the user writes in.
If the user writes in Hindi, respond in Hindi.
If the user writes in Arabic, respond in Arabic.
Never switch languages unless the user switches first.

Explicit, testable, works for any language without listing them all.

---

## Problem 3 — Latency went from 1.2s to 8-12s

**Three causes:**

**1. Growing conversation history — investigate this first**
If the bot appends every message to context, prompts get longer each turn. More
tokens = slower response. Over two weeks with more users, average session length
grew. Check this first — just compare average token count per request two weeks
ago vs now.

**2. No caching on repeated questions**
Support bots get the same questions constantly. Without caching, every request
hits GPT-4o. Add semantic caching — store recent answers and return them for
similar questions without calling the model.

**3. Infrastructure not scaling**
If the server isn't auto-scaling, more concurrent users cause queuing. Check
CPU/memory metrics and API gateway queue depth over the same period.

Infrastructure issues cause sudden spikes. Gradual degradation over two weeks
points to context length first.

---

## Post-mortem

Three issues emerged in the chatbot over two weeks.

Pricing — the bot was giving wrong prices because it relied on its own training
data instead of live pricing. We're fixing this by fetching current prices from
our database before every response.

Language — Hindi and Arabic users were getting English replies because the bot's
instructions were in English and it defaulted to that. One added line in the
instructions telling it to match the user's language fixes this.

Speed — response times grew from 1 second to 8-12 seconds as usage increased.
The main cause was conversation history growing with each session, making every
request slower to process. We're capping history length and adding a cache for
common questions.

None of these needed model changes — prompt design, data integration, and
caching fix all three.

---

# Task 2 — RAG Pipeline

## Precision@3 Result

**9/10 = 0.90**

Tested across 5 legal NDAs. Questions cover governing law, confidentiality duration,
assignment clauses, remedies, and exceptions. The one miss was two NDAs with nearly
identical exception clause language — expected behavior for naive top-k on similar
content.

## Scaling to 50,000 Documents

**1. Ingestion and embedding**
Currently embeds all chunks on CPU at startup. At this scale that's tens of millions
of chunks — not feasible on CPU.

Fix: GPU batch embedding distributed across multiple workers. Run ingestion as an
async offline pipeline so new documents are processed incrementally, separate from
query serving.

**2. Vector store**
ChromaDB works fine up to a few hundred thousand vectors but isn't built for tens
of millions and has no distributed support.

Fix: replace ChromaDB with Qdrant or Weaviate. Both use HNSW indexing for fast search at scale and support
horizontal scaling. Qdrant has good filtered search which is useful for querying
within specific contracts or date ranges.

**3. Retrieval**
At 50,000 NDAs, many documents share identical boilerplate. Pure vector search
can't distinguish the same clause appearing across hundreds of similar contracts.

Fix: move to hybrid search — combine vector similarity with BM25 keyword search.

**4. Generation**
flan-t5-base has a 512 token limit. With dense legal chunks that's already tight.
Complex questions at scale may need more context than fits.

Fix: a larger context model so more retrieved chunks can be passed per call. This
also improves instruction following, which fixes the confidence scoring issue we
saw where flan-t5-base refused grounded answers.

---

# Task 3 — Classifier

## Model Choice Justification

Chose fine-tuned DistilBERT over LLM prompting. Reason is latency and cost:

- If we use prompt then we will have to inject thousands of example for every call. It will increase the cost and latency. If examples were just 10-20 then prompt method was sufficient
- At 2880 tickets per day, cost and latency will be too much on prompt method so fine tunnig will work better here.

## Evaluation Results

Accuracy: 0.93

Per-class F1:
- billing: 0.85
- technical_issue: 0.95
- feature_request: 0.96
- complaint: 0.92
- other: 0.94

## Most Confused Classes

**complaint vs billing**
A ticket like "I was charged twice and this is completely unacceptable" has
both a billing signal and an emotional complaint tone. The model has to pick
one. 

**billing vs technical_issue**
"My payment failed" could be a billing problem or a system bug. Without more
context the model guesses. 

for both cases more examples of edge cases in training data would
improve separation.

## Data Note

Training data was synthetically generated with small variations per template.
Evaluation set was manually written to keep it realistic. Synthetic training
works at this scale but may not capture the full range of how real users phrase
things.

## Latency Test

Ran on 20 tickets. All predictions valid labels, all under 500ms, most under
150ms. Test passed.

---

# Task 4

## Question B — Evaluating a Summarisation System

**Automated metrics**
ROUGE measures word overlap with a reference summary. BERTScore measures semantic
similarity. Both have limits — ROUGE misses meaning, BERTScore can miss factual
errors.

**Ground truth dataset**
100-200 real internal reports with human-written reference summaries. Include
variety — short, long, technical, non-technical.

**Confidence Score**
Keep a fixed evaluation set. Run it after every reponse. If scores drop, flag
it before it reaches users.


No single metric captures true quality. Automated scores plus human review together
are the real solution

---

## Question A and C — On-Premise LLM Deployment

im not aware of Question A fully and calculation i dont think i can do just on assumption on Question C
