# RAG Intelligence Platform — Banc Sabadell Capstone 2026
## Traditional RAG vs. Graph RAG for Banking Regulatory Document Retrieval

**Team:** Mohamed Aymen Elmezouari · Abhay Mathahalli · Warren Liu  
**Partner:** Banc Sabadell — IT & Operations  
**Programme:** ESADE Business School · Capstone 2026  
**Status:** Final Submission · June 2026

---

## What This Project Does

This project delivers a rigorous, empirically grounded comparison of two AI retrieval architectures — **Traditional RAG** (vector-based) and **Graph RAG** (knowledge graph) — for querying banking regulatory documents in a GDPR-compliant environment.

The interactive prototype allows side-by-side comparison of both pipelines answering the same query in real time, with live metrics, source citations, and graph traversal paths.

**Key finding:** Graph RAG achieves +21 pp accuracy on multi-hop regulatory queries and reduces hallucination risk by 57%, at a 0.8s latency cost over Traditional RAG. A hybrid query-routing architecture is recommended for Banc Sabadell.

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/mohamedaymenelmezouari/rag-comparison-sabadell.git
cd rag-comparison-sabadell

# 2. Install dependencies
chmod +x setup/install.sh
./setup/install.sh

# 3. Add your Groq API key (.env file)
#    Free key at: https://console.groq.com
echo "GROQ_API_KEY=gsk_your_key_here" > .env

# 4. Build the indexes (one-time, ~5 minutes)
source venv/bin/activate
python3 setup/build_index.py

# 5. Launch the final prototype
streamlit run app/demo_final.py
```

Opens at **http://localhost:8501**

> The **Evaluation**, **Findings & Recommendation**, and **Architecture** tabs display final benchmark results and work immediately without any API key. Only the **Live Demo** tab requires a Groq key and initialized pipelines.

---

## Neo4j Setup (for full Graph RAG)

Graph RAG works with an in-memory fallback, but Neo4j gives full performance:

1. Download [Neo4j Desktop](https://neo4j.com/download/)
2. Create a new local database and start it
3. Set a password (e.g. `sabadell2026`)
4. Add to `.env`:

```env
GROQ_API_KEY=gsk_your_key_here
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=sabadell2026
```

---

## Manual Document Downloads

Two large PDFs require manual download (others are fetched automatically):

**Banc Sabadell Pillar III 2025**
→ Download from [grupbancsabadell.com](https://www.grupbancsabadell.com/corp/en/shareholders-and-investors/financial-information/annual-accounts-and-reports.html) and save as `data/corpus/Sabadell_Pillar3_2025.pdf`

**Basel III BIS Framework**
→ Download from [bis.org/bcbs/publ/d424.pdf](https://www.bis.org/bcbs/publ/d424.pdf) and save as `data/corpus/Basel3_BIS_Framework.pdf`

The pipeline works immediately with auto-generated sample texts. PDFs add depth but are not required to run the demo.

---

## Project Structure

```
rag-comparison-sabadell/
│
├── app/
│   ├── demo_final.py           # ★ Final prototype (use this for submission)
│   └── demo.py                 # Mid-term prototype (reference only)
│
├── pipelines/
│   ├── traditional_rag.py      # Vector RAG — ChromaDB + all-MiniLM-L6-v2 + Groq
│   └── graph_rag.py            # Graph RAG — Neo4j + spaCy NER + Cypher + Groq
│
├── graph/
│   ├── entity_extractor.py     # spaCy NER + LLM-assisted relationship extraction
│   └── neo4j_builder.py        # Neo4j graph construction and Cypher querying
│
├── evaluation/
│   ├── test_set.json           # 75 annotated Q&A pairs (4 tiers)
│   ├── evaluator.py            # Automated evaluation (Ragas + GPT-4o judge)
│   └── results.json            # Benchmark results (auto-generated)
│
├── data/
│   ├── corpus/                 # PDF and TXT regulatory documents
│   │   └── samples/            # Auto-generated sample texts
│   ├── chroma_db/              # ChromaDB vector store (auto-created)
│   └── graph_cache.json        # Entity/relationship cache (auto-created)
│
├── config/
│   └── config.py               # Shared config, paths, Groq client
│
├── setup/
│   ├── install.sh              # One-command macOS/Linux setup
│   ├── download_corpus.py      # Downloads public regulatory PDFs
│   └── build_index.py          # Builds vector index + knowledge graph
│
├── generate_final_report.py    # Generates Capstone_Report_Final.docx (Python only)
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
└── README.md                   # This file
```

---

## Architecture

### Traditional RAG Pipeline
```
PDF / TXT → PyMuPDF → Chunking (500 tok, 50 overlap) → all-MiniLM-L6-v2 embed
→ ChromaDB (local) → Top-k cosine retrieval → Groq Llama 3.3-70B → Answer
```

### Graph RAG Pipeline
```
PDF / TXT → spaCy NER → Entity extraction (8 types) → Neo4j graph
→ Cypher subgraph traversal (6 relationship types) → Context assembly
→ Groq Llama 3.3-70B → Answer + traversal path
```

**Entity types (8):** Regulation · Article · Product · Obligation · Role · Risk_Category · Threshold · Date

**Relationship types (6):** GOVERNS · REQUIRES · APPLIES_TO · REFERENCES · SUPERSEDES · EXEMPTS

---

## Technology Stack

| Component | Technology | Notes |
|-----------|------------|-------|
| Language | Python 3.11 | Python-only stack (Banc Sabadell standard) |
| LLM | Llama 3.3-70B via Groq | Sub-2s latency; Mistral 7B (Ollama) fallback |
| Embeddings | all-MiniLM-L6-v2 (local) | No API cost; GDPR-compliant data locality |
| Vector store | ChromaDB 0.4.x | Persistent local instance |
| Graph DB | Neo4j Community 5.x + APOC | 5,235 entities · 847 relationships |
| NLP / NER | spaCy en_core_web_sm + rules | Custom financial entity rules |
| Evaluation | Ragas 0.1.x + GPT-4o judge | Independent judge model (no circularity bias) |
| Frontend | Streamlit + Plotly | Python-only; no JavaScript dependencies |
| Orchestration | LangChain 0.2.x | Document processing, prompt management |

---

## Corpus — 9 Documents · ~750 Pages

| Document | Pages | Auto-downloaded |
|----------|-------|-----------------|
| EBA AML/CFT Guidelines 2021 (EBA/GL/2021/02) | 87 | Yes |
| BIS Basel III Framework | 63 | Manual |
| MiFID II Directive 2014/65/EU | 90 | Yes |
| GDPR Regulation 2016/679/EU | 54 | Yes |
| Banc Sabadell Pillar III Report 2025 | 210 | Manual |
| Banc Sabadell Annual Report 2025 | ~350 | Manual |
| EBA AML Guidelines (sample text) | 15 | Auto-created |
| Basel III (sample text) | 12 | Auto-created |
| GDPR Banking (sample text) | 14 | Auto-created |

---

## Final Benchmark Results (June 2026 · n=75)

Evaluated on 75 annotated Q&A pairs stratified across 4 query complexity tiers.  
Scored by GPT-4o as independent judge model.

| Metric | Traditional RAG | Graph RAG | Δ |
|--------|----------------|-----------|---|
| Accuracy | 79% | **87%** | +8 pp |
| Faithfulness | 82% | **91%** | +9 pp |
| Source Citation Quality | 74% | **88%** | +14 pp |
| Answer Quality | 81% | **89%** | +8 pp |
| Hallucination Risk | 21% | **9%** | −57% |
| Average Latency | **2.3s** | 3.1s | +0.8s |

### Accuracy by Complexity Tier

| Tier | Traditional RAG | Graph RAG | Winner |
|------|----------------|-----------|--------|
| Tier 1 · Simple Factual (n=20) | **91%** | 89% | Traditional RAG |
| Tier 2 · Single-hop (n=20) | 84% | **90%** | Graph RAG (+6 pp) |
| Tier 3 · Multi-hop Relational (n=20) | 68% | **89%** | Graph RAG (+21 pp) |
| Tier 4 · Adversarial (n=15) | 71% | **80%** | Graph RAG (+9 pp) |

**Graph RAG wins: 52/75 · Traditional RAG wins: 18/75 · Ties: 5/75**

---

## Running Individual Components

```bash
# Test Traditional RAG pipeline
python3 pipelines/traditional_rag.py

# Test Graph RAG pipeline
python3 pipelines/graph_rag.py

# Run entity extraction standalone
python3 graph/entity_extractor.py

# Run quick evaluation (5 questions, ~3 min)
python3 evaluation/evaluator.py

# Run full evaluation (75 questions)
python3 -c "from evaluation.evaluator import run_evaluation; run_evaluation()"

# Regenerate the final Word report
python3 generate_final_report.py
```

---

## Query Presets (Demo)

| Tier | Example Query |
|------|--------------|
| Tier 1 — Simple | "What is the minimum CET1 capital ratio under Basel III?" |
| Tier 2 — Single-hop | "What CDD obligations apply to Politically Exposed Persons under AML?" |
| Tier 3 — Multi-hop | "Which products require both MiFID II suitability and AML enhanced due diligence?" |
| Tier 4 — Adversarial | "What does Article 47 of GDPR say about banking?" |

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `GROQ_API_KEY not set` | Add your key to `.env`: `GROQ_API_KEY=gsk_...` |
| `No documents found in corpus` | Run `python3 setup/download_corpus.py` |
| `spaCy model not found` | Run `python3 -m spacy download en_core_web_sm` |
| Neo4j connection refused | Open Neo4j Desktop and start the database (green dot) |
| Streamlit ImportError | Activate venv: `source venv/bin/activate` |
| `chromadb` version conflict | Run `pip install chromadb==0.4.24` |

---

## Requirements

- Python 3.9+ (Python 3.11 recommended)
- macOS or Linux (Windows: use WSL)
- Neo4j Desktop — optional, in-memory fallback available
- Groq API key — free at [console.groq.com](https://console.groq.com)
- ~2 GB disk space for models and indexes

---

## References

1. Lewis et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.* NeurIPS 33.
2. Edge et al. (2024). *From Local to Global: A Graph RAG Approach to Query-Focused Summarization.* Microsoft Research. arXiv:2404.16130.
3. Pan et al. (2024). *Unifying Large Language Models and Knowledge Graphs: A Roadmap.* IEEE TKDE. arXiv:2306.08302.
4. Es et al. (2023). *RAGAS: Automated Evaluation of Retrieval Augmented Generation.* arXiv:2309.15217.
5. Reimers & Gurevych (2019). *Sentence-BERT.* EMNLP 2019.

---

*ESADE Business School · Banc Sabadell Capstone Project 2026*  
*This project was developed using a Python-only stack in alignment with Banc Sabadell's engineering standards.*
