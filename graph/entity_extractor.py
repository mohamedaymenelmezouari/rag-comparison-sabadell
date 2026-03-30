"""
entity_extractor.py
Extracts entities and relationships from banking regulatory documents
to build the knowledge graph for Graph RAG.

Entity types:
  - Regulation     : Legal regulations (GDPR, MiFID II, Basel III, AML Directive)
  - Article        : Specific articles within regulations
  - Obligation     : Specific compliance obligations (CDD, EDD, SAR)
  - Product        : Financial products (mortgage, loan, UCITS, structured product)
  - Role           : Actor roles (PEP, beneficial owner, DPO, institution)
  - Risk_Category  : Risk classifications (high-risk, low-risk, ML/TF risk)
  - Threshold      : Numerical thresholds (CET1 4.5%, 25% beneficial ownership)
  - Process        : Compliance processes (transaction monitoring, risk assessment)

Relationship types:
  - GOVERNS        : Regulation GOVERNS Obligation
  - REQUIRES       : Obligation REQUIRES Process
  - APPLIES_TO     : Regulation APPLIES_TO Product / Role
  - REFERENCES     : Article REFERENCES Article
  - TRIGGERS       : Risk_Category TRIGGERS Obligation
  - EXEMPTS        : Regulation EXEMPTS Product from Obligation
"""

import re
import json
import time
from pathlib import Path
from typing import Optional
import spacy
from rich.console import Console
from rich.progress import track

import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.config import generate, CORPUS_DIR, GRAPH_CACHE

console = Console()

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    console.print("spaCy model not found. Run: python3 -m spacy download en_core_web_sm", style="red")
    nlp = None


# ── Banking-specific entity patterns ─────────────────────────

REGULATION_PATTERNS = [
    r"\bGDPR\b", r"\bMiFID\s*II?\b", r"\bBasel\s*III?\b", r"\bAML\b",
    r"\bCRD\s*IV?\b", r"\bPSD\s*2?\b", r"\bAMLD\s*[456]?\b",
    r"\bEBA/GL/\d{4}/\d{2}\b", r"Directive\s+\d{4}/\d+/EU",
    r"Regulation\s+\(EU\)\s+\d{4}/\d+", r"\bFRTB\b", r"\bNSFR\b", r"\bLCR\b"
]

OBLIGATION_PATTERNS = [
    r"\bCustomer Due Diligence\b", r"\bCDD\b", r"\bEnhanced Due Diligence\b",
    r"\bEDD\b", r"\bSimplified Due Diligence\b", r"\bSDD\b",
    r"\bSuspicious\s+(?:Activity|Transaction)\s+Report(?:ing)?\b", r"\bSAR\b", r"\bSTR\b",
    r"\btransaction monitoring\b", r"\bbeneficial ownership\b", r"\brisk assessment\b",
    r"\bsuitability (?:test|assessment)\b", r"\bappropriateness test\b",
    r"\bbest execution\b", r"\bdata breach notification\b",
    r"\bPrivacy by Design\b", r"\bDPIA\b"
]

THRESHOLD_PATTERNS = [
    r"\b4\.5\s*%\s*(?:CET1|capital)\b", r"\b6\s*%\s*Tier\s*1\b", r"\b8\s*%\s*(?:total\s+)?capital\b",
    r"\b25\s*%\s*(?:of\s+)?(?:shares|voting rights|ownership)\b",
    r"\b72\s*(?:-|\s+)?hour(?:s)?\b", r"\b30\s*(?:calendar\s+)?days?\b",
    r"\b100\s*%\s*(?:LCR|NSFR|leverage)\b", r"\b3\s*%\s*(?:leverage|Tier\s*1)\b",
    r"\b2\.5\s*%\s*(?:buffer|conservation)\b"
]

PRODUCT_PATTERNS = [
    r"\bmortgage\b", r"\bresidential\s+(?:mortgage|property)\b",
    r"\bUCITS\b", r"\bPRIIPs?\b", r"\bstructured\s+(?:product|note|deposit)\b",
    r"\bderivative[s]?\b", r"\bcredit\s+(?:facility|line|card)\b",
    r"\bsavings\s+account\b", r"\bcurrent\s+account\b", r"\bpension\s+fund\b",
    r"\bETF\b", r"\bbond[s]?\b", r"\bequit(?:y|ies)\b",
    r"\bcorrespondent\s+banking\b"
]


class EntityExtractor:
    """
    Extracts banking entities and relationships from text using:
    1. Rule-based patterns (fast, deterministic)
    2. spaCy NER (for generic named entities)
    3. LLM-assisted extraction (for complex relationships)
    """

    def extract_from_text(self, text: str, source_doc: str) -> dict:
        """
        Extract all entities and relationships from a text passage.
        Returns dict with 'entities' and 'relationships' lists.
        """
        entities = []
        relationships = []

        # 1. Pattern-based extraction
        entities.extend(self._extract_patterns(text, source_doc))

        # 2. spaCy extraction
        if nlp:
            entities.extend(self._extract_spacy(text, source_doc))

        # Deduplicate entities
        seen = set()
        unique_entities = []
        for e in entities:
            key = (e["type"], e["name"].lower())
            if key not in seen:
                seen.add(key)
                unique_entities.append(e)

        # 3. Extract relationships between found entities
        relationships = self._extract_relationships(text, unique_entities, source_doc)

        return {"entities": unique_entities, "relationships": relationships}

    def _extract_patterns(self, text: str, source_doc: str) -> list[dict]:
        entities = []

        for pattern in REGULATION_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append({
                    "type": "Regulation",
                    "name": match.group().strip(),
                    "source": source_doc,
                    "context": text[max(0, match.start()-50):match.end()+50].strip()
                })

        for pattern in OBLIGATION_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append({
                    "type": "Obligation",
                    "name": match.group().strip(),
                    "source": source_doc,
                    "context": text[max(0, match.start()-50):match.end()+50].strip()
                })

        for pattern in THRESHOLD_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append({
                    "type": "Threshold",
                    "name": match.group().strip(),
                    "source": source_doc,
                    "context": text[max(0, match.start()-80):match.end()+80].strip()
                })

        for pattern in PRODUCT_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append({
                    "type": "Product",
                    "name": match.group().strip(),
                    "source": source_doc,
                    "context": text[max(0, match.start()-50):match.end()+50].strip()
                })

        return entities

    def _extract_spacy(self, text: str, source_doc: str) -> list[dict]:
        entities = []
        # Process in chunks to avoid spaCy token limit
        chunk_size = 100000
        for i in range(0, len(text), chunk_size):
            doc = nlp(text[i:i+chunk_size])
            for ent in doc.ents:
                if ent.label_ in ("ORG", "LAW", "GPE") and len(ent.text) > 2:
                    entities.append({
                        "type": "Organization" if ent.label_ == "ORG" else "Regulation",
                        "name": ent.text.strip(),
                        "source": source_doc,
                        "context": text[max(0, ent.start_char-50):ent.end_char+50].strip()
                    })
        return entities

    def _extract_relationships(self, text: str, entities: list, source_doc: str) -> list[dict]:
        """Extract relationships between co-occurring entities in the same sentence."""
        relationships = []
        sentences = text.split(".")

        for sentence in sentences:
            sentence_entities = [
                e for e in entities
                if e["name"].lower() in sentence.lower()
            ]

            if len(sentence_entities) < 2:
                continue

            for i, e1 in enumerate(sentence_entities):
                for e2 in sentence_entities[i+1:]:
                    rel_type = _infer_relationship(e1, e2, sentence)
                    if rel_type:
                        relationships.append({
                            "source_entity": e1["name"],
                            "source_type": e1["type"],
                            "relationship": rel_type,
                            "target_entity": e2["name"],
                            "target_type": e2["type"],
                            "evidence": sentence.strip()[:200],
                            "source_doc": source_doc
                        })

        return relationships


def _infer_relationship(e1: dict, e2: dict, sentence: str) -> Optional[str]:
    """Infer relationship type based on entity types and sentence content."""
    s = sentence.lower()

    if e1["type"] == "Regulation" and e2["type"] == "Obligation":
        if any(kw in s for kw in ["require", "mandate", "shall", "must", "oblig"]):
            return "REQUIRES"
        return "GOVERNS"

    if e1["type"] == "Regulation" and e2["type"] == "Product":
        if any(kw in s for kw in ["apply", "applies", "exempt", "scope"]):
            return "APPLIES_TO"

    if e1["type"] == "Obligation" and e2["type"] == "Threshold":
        return "HAS_THRESHOLD"

    if e1["type"] == "Regulation" and e2["type"] == "Threshold":
        return "SETS_THRESHOLD"

    if e1["type"] == "Obligation" and e2["type"] == "Product":
        if any(kw in s for kw in ["apply", "require", "assess", "test"]):
            return "APPLIES_TO"

    return None


def build_graph_cache(force_rebuild: bool = False) -> dict:
    """
    Process all corpus documents, extract entities and relationships,
    and save to a JSON cache file.
    """
    if GRAPH_CACHE.exists() and not force_rebuild:
        console.print("  Graph cache already exists. Loading...", style="dim")
        with open(GRAPH_CACHE) as f:
            return json.load(f)

    extractor = EntityExtractor()
    all_files = list(CORPUS_DIR.rglob("*.pdf")) + list(CORPUS_DIR.rglob("*.txt"))

    if not all_files:
        raise FileNotFoundError(f"No documents found in {CORPUS_DIR}")

    console.print(f"\n  Extracting entities from {len(all_files)} documents...", style="bold")

    graph_data = {"entities": [], "relationships": [], "source_docs": []}

    for file_path in track(all_files, description="  Processing documents"):
        if file_path.suffix.lower() == ".pdf":
            try:
                import fitz
                doc = fitz.open(str(file_path))
                text = "\n".join(page.get_text() for page in doc)
                doc.close()
            except Exception:
                continue
        else:
            text = file_path.read_text(encoding="utf-8", errors="ignore")

        result = extractor.extract_from_text(text, file_path.name)
        graph_data["entities"].extend(result["entities"])
        graph_data["relationships"].extend(result["relationships"])
        graph_data["source_docs"].append(file_path.name)

    # Deduplicate
    seen_entities = set()
    unique_entities = []
    for e in graph_data["entities"]:
        key = (e["type"], e["name"].lower())
        if key not in seen_entities:
            seen_entities.add(key)
            unique_entities.append(e)
    graph_data["entities"] = unique_entities

    GRAPH_CACHE.parent.mkdir(parents=True, exist_ok=True)
    with open(GRAPH_CACHE, "w") as f:
        json.dump(graph_data, f, indent=2)

    console.print(f"  ✓ Extracted {len(unique_entities)} entities and "
                  f"{len(graph_data['relationships'])} relationships", style="green")
    console.print(f"  ✓ Graph cache saved to {GRAPH_CACHE}", style="green")

    return graph_data
