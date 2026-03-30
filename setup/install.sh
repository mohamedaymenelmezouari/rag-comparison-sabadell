#!/bin/bash
# ─────────────────────────────────────────────────────────────
# RAG Comparison Project — One-Command Setup for macOS
# Run: chmod +x setup/install.sh && ./setup/install.sh
# ─────────────────────────────────────────────────────────────

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║   RAG Comparison — Banc Sabadell Capstone 2026           ║"
echo "║   Traditional RAG vs. Graph RAG — Setup Script           ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ── 1. Check Python ──────────────────────────────────────────
echo -e "${YELLOW}[1/6] Checking Python version...${NC}"
PYTHON=$(python3 --version 2>&1)
echo "  Found: $PYTHON"
if ! python3 -c "import sys; assert sys.version_info >= (3,9)" 2>/dev/null; then
  echo -e "${RED}  ERROR: Python 3.9+ required. Install from python.org${NC}"
  exit 1
fi
echo -e "${GREEN}  Python OK${NC}"

# ── 2. Create virtual environment ────────────────────────────
echo -e "${YELLOW}[2/6] Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
  python3 -m venv venv
  echo -e "${GREEN}  Virtual environment created${NC}"
else
  echo "  Virtual environment already exists, skipping"
fi
source venv/bin/activate

# ── 3. Install Python packages ───────────────────────────────
echo -e "${YELLOW}[3/6] Installing Python packages (this takes 2-3 minutes)...${NC}"
pip install --quiet --upgrade pip
pip install --quiet \
  groq \
  chromadb \
  sentence-transformers \
  langchain \
  langchain-community \
  langchain-groq \
  neo4j \
  pymupdf \
  spacy \
  streamlit \
  plotly \
  pandas \
  python-dotenv \
  ragas \
  datasets \
  tqdm \
  requests \
  rich

echo -e "${GREEN}  All packages installed${NC}"

# ── 4. Download spaCy model ───────────────────────────────────
echo -e "${YELLOW}[4/6] Downloading spaCy English model...${NC}"
python3 -m spacy download en_core_web_sm --quiet
echo -e "${GREEN}  spaCy model ready${NC}"

# ── 5. Copy .env if not exists ───────────────────────────────
echo -e "${YELLOW}[5/6] Setting up environment file...${NC}"
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo -e "${YELLOW}  .env file created — IMPORTANT: open .env and add your GROQ_API_KEY and Neo4j password${NC}"
else
  echo "  .env already exists, skipping"
fi

# ── 6. Download corpus ────────────────────────────────────────
echo -e "${YELLOW}[6/6] Downloading regulatory document corpus...${NC}"
python3 setup/download_corpus.py

echo ""
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║   Setup complete!                                        ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║   Next steps:                                            ║"
echo "║   1. Open .env and add your GROQ_API_KEY                 ║"
echo "║   2. Install Neo4j Desktop from neo4j.com/download       ║"
echo "║   3. Create a database, set password in .env             ║"
echo "║   4. Run: source venv/bin/activate                       ║"
echo "║   5. Run: python3 setup/build_index.py                   ║"
echo "║   6. Run: streamlit run app/demo.py                      ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
