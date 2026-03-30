# RAG Comparison — Banc Sabadell Capstone 2026
## Traditional RAG vs. Graph RAG for Banking Regulatory Documents

**Team:** Mohamed Aymen Elmezouari · Abhay Mathahalli · Warren Liu  
**Partner:** Banc Sabadell — IT & Operations  
**Programme:** ESADE Capstone 2026

---

## Quick Start (5 steps)

```bash
# 1. Clone / unzip the project
cd rag_comparison

# 2. Run the setup script (installs everything)
chmod +x setup/install.sh
./setup/install.sh

# 3. Add your Groq API key to .env
#    Get a FREE key at: https://console.groq.com
echo "GROQ_API_KEY=gsk_your_key_here" >> .env

# 4. Build both indexes (one-time, ~5 minutes)
source venv/bin/activate
python3 setup/build_index.py

# 5. Launch the demo
streamlit run app/demo.py
```

The demo opens at **http://localhost:8501**

---

## Neo4j Setup (for full Graph RAG)

The Graph RAG pipeline works without Neo4j using an in-memory fallback,  
but for full performance install Neo4j Desktop:

1. Download: https://neo4j.com/download/
2. Install and open Neo4j Desktop
3. Click **New** → **Create a local database**
4. Set a password (e.g., `sabadell2026`)
5. Click **Start** on the database
6. Add to your `.env`:
   ```
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=sabadell2026
   ```
7. Re-run: `python3 setup/build_index.py`

---

## Manual Document Downloads

Most corpus documents are downloaded automatically. Two require manual download:

### Banc Sabadell Pillar III 2024
1. Go to: https://www.grupbancsabadell.com/corp/en/shareholders-and-investors/financial-information/annual-accounts-and-reports.html
2. Download the **Pillar 3 2024** PDF
3. Save as: `data/corpus/Sabadell_Pillar3_2024.pdf`

### Basel III BIS Framework
1. Go to: https://www.bis.org/bcbs/publ/d424.pdf
2. Download and save as: `data/corpus/Basel3_BIS_Framework.pdf`

> **Note:** The pipeline works immediately with the sample text files created automatically.
> The PDFs add more depth but are not required to run the demo.

---

## Project Structure

```
rag_comparison/
├── setup/
│   ├── install.sh              # One-command Mac setup
│   ├── download_corpus.py      # Downloads public regulatory documents
│   └── build_index.py          # Builds vector index + knowledge graph
│
├── data/
│   ├── corpus/                 # Your PDF/TXT documents go here
│   │   └── samples/            # Auto-generated sample regulatory texts
│   ├── chroma_db/              # Vector store (auto-created)
│   └── graph_cache.json        # Entity/relationship cache (auto-created)
│
├── config/
│   └── config.py               # Shared config, Groq client, paths
│
├── pipelines/
│   ├── traditional_rag.py      # Full vector RAG pipeline
│   └── graph_rag.py            # Full Graph RAG pipeline
│
├── graph/
│   ├── entity_extractor.py     # NER + relationship extraction
│   └── neo4j_builder.py        # Neo4j graph construction + querying
│
├── evaluation/
│   ├── test_set.json           # 20 annotated Q&A pairs (4 tiers)
│   ├── evaluator.py            # Runs Ragas-style evaluation
│   └── results.json            # Evaluation results (auto-generated)
│
├── app/
│   └── demo.py                 # Streamlit web demo
│
├── .env.example                # Environment variables template
└── README.md                   # This file
```

---

## Running Individual Components

```bash
# Test Traditional RAG only
python3 pipelines/traditional_rag.py

# Test Graph RAG only  
python3 pipelines/graph_rag.py

# Build entity graph (standalone)
python3 graph/entity_extractor.py

# Run evaluation (quick, 5 questions)
python3 evaluation/evaluator.py

# Run full evaluation (all 20 questions, ~15 min)
python3 -c "from evaluation.evaluator import run_evaluation; run_evaluation()"
```

---

## Evaluation Query Tiers

| Tier | Name | Description | Expected winner |
|------|------|-------------|-----------------|
| 1 | Simple Factual | Single document lookup | Tie |
| 2 | Single-hop Relational | Two entities linked | Graph RAG slight advantage |
| 3 | Multi-hop Relational | Multi-entity traversal | Graph RAG significant advantage |
| 4 | Adversarial | Tests hallucination resistance | Graph RAG advantage |

---

## Corpus Documents

| File | Description | Auto-downloaded? |
|------|-------------|-----------------|
| EBA_AML_Guidelines_2021.pdf | AML/CFT guidance | Yes (attempt) |
| MiFID2_Directive_2014_65_EU.pdf | MiFID II directive | Yes |
| GDPR_Regulation_2016_679_EU.pdf | GDPR regulation | Yes |
| Basel3_BIS_Framework.pdf | Basel III framework | Manual (see above) |
| Sabadell_Pillar3_2024.pdf | Sabadell risk disclosures | Manual (see above) |
| data/corpus/samples/*.txt | Rich sample texts | Auto-created |

---

## Requirements

- Python 3.9+
- macOS (tested), Linux (compatible), Windows (WSL recommended)
- Neo4j Desktop (optional but recommended)
- Groq API key (free at console.groq.com)
- ~2GB disk space for models and indexes

---

## Troubleshooting

**"GROQ_API_KEY not set"**  
→ Open `.env` and add your key: `GROQ_API_KEY=gsk_...`

**"No documents found in corpus"**  
→ Run: `python3 setup/download_corpus.py`

**"spaCy model not found"**  
→ Run: `python3 -m spacy download en_core_web_sm`

**Neo4j connection refused**  
→ Make sure Neo4j Desktop is open and the database is started (green dot)

**Streamlit ImportError**  
→ Make sure venv is activated: `source venv/bin/activate`
