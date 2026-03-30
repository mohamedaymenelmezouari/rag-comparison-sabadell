"""
graph_rag.py
Full Graph RAG pipeline using Neo4j knowledge graph.

Architecture:
  Query → Entity disambiguation (spaCy + patterns)
        → Neo4j subgraph traversal (Cypher)
        → Context assembly from graph paths
        → Groq LLM generation (Llama 3.3-70B)
        → Answer with explicit entity citations
"""

import time
import json
from pathlib import Path
from typing import Optional
from rich.console import Console

import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.config import generate, GRAPH_CACHE, NEO4J_URI
from graph.entity_extractor import EntityExtractor, build_graph_cache
from graph.neo4j_builder import Neo4jGraphBuilder

console = Console()

SYSTEM_PROMPT = """You are a regulatory compliance assistant for Banc Sabadell, using a knowledge graph of banking regulations.
You receive context assembled from a knowledge graph showing relationships between regulatory entities.

The context shows:
- Direct entity matches: specific regulations, obligations, thresholds found relevant to the query
- Graph paths: relationships like "Basel III --[SETS_THRESHOLD]--> CET1 4.5%"

Rules:
- Use the graph paths to provide structured, relationship-aware answers
- Explicitly mention the regulatory relationships (e.g., "Under Basel III, which GOVERNS capital requirements, banks MUST maintain...")
- Cite specific entities from the graph (regulation names, article numbers, threshold values)
- Do not fabricate relationships not present in the context
- Your answer should be more structured than a simple text search — use the graph relationships to connect concepts

After your answer, add two lines:
SOURCES: [document names from the graph context]
GRAPH_PATH: [most relevant entity path from the context, e.g., "MiFID_II -> REQUIRES -> Suitability_Assessment -> APPLIES_TO -> Retail_Client"]
"""


class GraphRAG:
    """
    Graph RAG pipeline: retrieves context via knowledge graph traversal
    rather than vector similarity.
    """

    def __init__(self, use_neo4j: bool = True):
        self.use_neo4j = use_neo4j
        self._neo4j = None
        self._fallback_graph = None
        self._extractor = EntityExtractor()

    def connect(self):
        """Connect to Neo4j if available, otherwise use in-memory graph."""
        if self.use_neo4j:
            try:
                self._neo4j = Neo4jGraphBuilder()
                self._neo4j.connect()
                return True
            except Exception as e:
                console.print(f"  Neo4j unavailable ({e}), falling back to in-memory graph.", style="yellow")
                self.use_neo4j = False

        # Fallback: load from JSON cache
        self._load_fallback_graph()
        return False

    def _load_fallback_graph(self):
        """Load graph from JSON cache for in-memory traversal."""
        if GRAPH_CACHE.exists():
            with open(GRAPH_CACHE) as f:
                self._fallback_graph = json.load(f)
            console.print(f"  Loaded fallback graph: {len(self._fallback_graph['entities'])} entities", style="dim")
        else:
            console.print("  No graph cache found. Run setup/build_index.py first.", style="yellow")
            self._fallback_graph = {"entities": [], "relationships": []}

    def build_graph(self, force_rebuild: bool = False):
        """Build or rebuild the knowledge graph from corpus."""
        # Step 1: Extract entities to cache
        build_graph_cache(force_rebuild=force_rebuild)

        # Step 2: Load into Neo4j if available
        if self.use_neo4j and self._neo4j:
            self._neo4j.setup_schema()
            self._neo4j.build_from_cache(force_rebuild=force_rebuild)
        else:
            self._load_fallback_graph()

    # ── Retrieval ─────────────────────────────────────────────

    def retrieve(self, query: str) -> list[dict]:
        """
        Retrieve relevant subgraph context for the query.
        Uses Neo4j if available, otherwise in-memory traversal.
        """
        if self.use_neo4j and self._neo4j:
            return self._neo4j.retrieve_subgraph(query)
        else:
            return self._fallback_retrieve(query)

    def _fallback_retrieve(self, query: str, max_results: int = 20) -> list[dict]:
        """In-memory graph traversal fallback (no Neo4j required)."""
        if not self._fallback_graph:
            return []

        query_lower = query.lower()
        query_words = set(w for w in query_lower.split() if len(w) > 2)

        # Find matching entities
        matched_entities = []
        for entity in self._fallback_graph.get("entities", []):
            name_lower = entity["name"].lower()
            if any(word in name_lower for word in query_words):
                matched_entities.append(entity)

        matched_names = {e["name"].lower() for e in matched_entities}

        # Find relationships involving matched entities
        context_nodes = []
        for entity in matched_entities[:5]:
            context_nodes.append({
                "path": f"[{entity['type']}] {entity['name']}",
                "src_name": entity["name"],
                "src_type": entity["type"],
                "rel_type": "DIRECT_MATCH",
                "tgt_name": entity["name"],
                "tgt_type": entity["type"],
                "context": entity.get("context", ""),
                "source": entity.get("source", ""),
            })

        for rel in self._fallback_graph.get("relationships", []):
            src_match = rel["source_entity"].lower() in matched_names
            tgt_match = rel["target_entity"].lower() in matched_names
            if src_match or tgt_match:
                context_nodes.append({
                    "path": f"{rel['source_entity']} --[{rel['relationship']}]--> {rel['target_entity']}",
                    "src_name": rel["source_entity"],
                    "src_type": rel.get("source_type", ""),
                    "rel_type": rel["relationship"],
                    "tgt_name": rel["target_entity"],
                    "tgt_type": rel.get("target_type", ""),
                    "context": rel.get("evidence", ""),
                    "source": rel.get("source_doc", ""),
                })

        # Sort: direct matches first, then by relevance
        context_nodes.sort(key=lambda x: (0 if x["rel_type"] == "DIRECT_MATCH" else 1))
        return context_nodes[:max_results]

    # ── Full pipeline query ───────────────────────────────────

    def query(self, question: str) -> dict:
        """
        Full Graph RAG query: graph traversal → context assembly → generation.
        """
        t_start = time.time()

        # Retrieve relevant subgraph
        t_retrieve_start = time.time()
        graph_context = self.retrieve(question)
        t_retrieve = time.time() - t_retrieve_start

        if not graph_context:
            return {
                "answer": "No relevant entities found in the knowledge graph for this query.",
                "sources": [],
                "graph_paths": [],
                "latency_total": time.time() - t_start,
                "latency_retrieval": t_retrieve,
                "latency_generation": 0,
                "pipeline": "Graph RAG",
                "method": "knowledge_graph_traversal",
            }

        # Build context from graph
        context_parts = []
        graph_paths = []
        seen_paths = set()

        for node in graph_context:
            path = node["path"]
            if path not in seen_paths:
                seen_paths.add(path)
                graph_paths.append(path)
                if node.get("context"):
                    context_parts.append(
                        f"Graph path: {path}\n"
                        f"Context: {node['context'][:300]}\n"
                        f"Source: {node.get('source', 'unknown')}"
                    )

        context = "\n\n---\n\n".join(context_parts[:15])

        # Add graph structure summary at top
        graph_summary = "KNOWLEDGE GRAPH CONTEXT:\n"
        graph_summary += "Entity relationships found:\n"
        for path in graph_paths[:10]:
            graph_summary += f"  • {path}\n"

        full_context = graph_summary + "\n\nDETAILED CONTEXT:\n" + context

        prompt_with_context = (
            f"Based on the following knowledge graph context about banking regulations, "
            f"answer the question using the entity relationships provided.\n\n"
            f"{full_context}\n\n"
            f"QUESTION: {question}"
        )

        # Generate answer
        t_gen_start = time.time()
        raw_answer = generate(SYSTEM_PROMPT, prompt_with_context)
        t_gen = time.time() - t_gen_start

        # Parse sources and graph path from answer
        answer_text, sources, final_graph_path = _parse_graph_answer(raw_answer)

        return {
            "answer": answer_text,
            "sources": sources if sources else list({n.get("source", "") for n in graph_context if n.get("source")}),
            "graph_paths": graph_paths[:8],
            "graph_path_cited": final_graph_path,
            "latency_total": round(time.time() - t_start, 3),
            "latency_retrieval": round(t_retrieve, 3),
            "latency_generation": round(t_gen, 3),
            "pipeline": "Graph RAG",
            "method": "knowledge_graph_traversal",
            "neo4j_used": self.use_neo4j,
            "entities_found": len(graph_context),
        }

    def get_graph_stats(self) -> dict:
        if self.use_neo4j and self._neo4j:
            return self._neo4j.get_stats()
        elif self._fallback_graph:
            return {
                "nodes": len(self._fallback_graph.get("entities", [])),
                "relationships": len(self._fallback_graph.get("relationships", [])),
                "source_docs": len(self._fallback_graph.get("source_docs", [])),
            }
        return {}


def _parse_graph_answer(raw_answer: str) -> tuple[str, list[str], str]:
    """Extract SOURCES and GRAPH_PATH from raw answer."""
    lines = raw_answer.strip().split("\n")
    sources = []
    graph_path = ""
    answer_lines = []

    for line in lines:
        if line.strip().upper().startswith("SOURCES:"):
            src_text = line.split(":", 1)[1].strip()
            sources = [s.strip() for s in src_text.replace("[", "").replace("]", "").split(",") if s.strip()]
        elif line.strip().upper().startswith("GRAPH_PATH:"):
            graph_path = line.split(":", 1)[1].strip().replace("[", "").replace("]", "")
        else:
            answer_lines.append(line)

    return "\n".join(answer_lines).strip(), sources, graph_path


# ── Standalone usage ──────────────────────────────────────────

if __name__ == "__main__":
    console.print("\n[bold green]Graph RAG Pipeline — Test Run[/bold green]\n")

    graph_rag = GraphRAG(use_neo4j=True)
    graph_rag.connect()
    graph_rag.build_graph()

    test_query = "What capital ratio must banks maintain under Basel III and how is it calculated?"
    console.print(f"\n[bold]Query:[/bold] {test_query}\n")

    result = graph_rag.query(test_query)

    console.print(f"[bold green]Answer:[/bold green]\n{result['answer']}\n")
    console.print(f"[bold]Graph paths used:[/bold]")
    for path in result["graph_paths"]:
        console.print(f"  • {path}", style="dim")
    console.print(f"\n[bold]Latency:[/bold] {result['latency_total']}s total")
