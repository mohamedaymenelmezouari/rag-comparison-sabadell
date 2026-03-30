"""
neo4j_builder.py
Builds and queries the Neo4j knowledge graph for Graph RAG.

Requires Neo4j Desktop running locally with credentials in .env
Download Neo4j Desktop: https://neo4j.com/download/
"""

import json
from pathlib import Path
from typing import Optional
from rich.console import Console

import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, GRAPH_CACHE

console = Console()


class Neo4jGraphBuilder:
    """
    Builds a Neo4j knowledge graph from extracted banking entities and relationships.
    Also handles querying the graph for Graph RAG retrieval.
    """

    def __init__(self):
        self._driver = None

    def connect(self):
        """Connect to Neo4j. Call this explicitly before using the graph."""
        try:
            from neo4j import GraphDatabase
            self._driver = GraphDatabase.driver(
                NEO4J_URI,
                auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
            )
            self._driver.verify_connectivity()
            console.print("  ✓ Connected to Neo4j", style="green")
        except Exception as e:
            console.print(f"  ✗ Neo4j connection failed: {e}", style="red")
            console.print(
                "  Make sure Neo4j Desktop is running and credentials in .env are correct.\n"
                "  Download: https://neo4j.com/download/",
                style="yellow"
            )
            raise

    def close(self):
        if self._driver:
            self._driver.close()

    # ── Schema setup ──────────────────────────────────────────

    def setup_schema(self):
        """Create indexes and constraints for performance."""
        constraints = [
            "CREATE CONSTRAINT regulation_name IF NOT EXISTS FOR (r:Regulation) REQUIRE r.name IS UNIQUE",
            "CREATE CONSTRAINT obligation_name IF NOT EXISTS FOR (o:Obligation) REQUIRE o.name IS UNIQUE",
            "CREATE CONSTRAINT product_name IF NOT EXISTS FOR (p:Product) REQUIRE p.name IS UNIQUE",
            "CREATE CONSTRAINT threshold_name IF NOT EXISTS FOR (t:Threshold) REQUIRE t.name IS UNIQUE",
        ]
        indexes = [
            "CREATE INDEX regulation_source IF NOT EXISTS FOR (r:Regulation) ON (r.source)",
            "CREATE INDEX obligation_source IF NOT EXISTS FOR (o:Obligation) ON (o.source)",
            "CREATE FULLTEXT INDEX entity_search IF NOT EXISTS FOR (n:Regulation|Obligation|Product|Threshold|Role) ON EACH [n.name, n.context]",
        ]
        with self._driver.session() as session:
            for q in constraints + indexes:
                try:
                    session.run(q)
                except Exception:
                    pass  # Constraint may already exist
        console.print("  ✓ Schema and indexes ready", style="green")

    # ── Graph construction ────────────────────────────────────

    def build_from_cache(self, force_rebuild: bool = False):
        """Load graph data from JSON cache and populate Neo4j."""
        if not GRAPH_CACHE.exists():
            raise FileNotFoundError(
                f"Graph cache not found at {GRAPH_CACHE}.\n"
                "Run: python3 graph/entity_extractor.py first."
            )

        # Check if graph already has data
        with self._driver.session() as session:
            count = session.run("MATCH (n) RETURN count(n) as c").single()["c"]
            if count > 0 and not force_rebuild:
                console.print(f"  Graph already contains {count} nodes. Skipping rebuild.", style="dim")
                console.print("  Use force_rebuild=True to rebuild.", style="dim")
                return

            if force_rebuild:
                session.run("MATCH (n) DETACH DELETE n")
                console.print("  Cleared existing graph.", style="yellow")

        with open(GRAPH_CACHE) as f:
            graph_data = json.load(f)

        console.print(f"\n  Loading {len(graph_data['entities'])} entities into Neo4j...", style="bold")

        # Batch insert entities
        with self._driver.session() as session:
            batch_size = 200
            entities = graph_data["entities"]
            for i in range(0, len(entities), batch_size):
                batch = entities[i:i+batch_size]
                session.run("""
                    UNWIND $batch AS entity
                    CALL apoc.merge.node(
                        [entity.type],
                        {name: entity.name},
                        {source: entity.source, context: entity.context}
                    ) YIELD node
                    RETURN count(node)
                """, batch=batch)

        # Fallback without APOC
        with self._driver.session() as session:
            for entity in graph_data["entities"]:
                label = _sanitize_label(entity["type"])
                session.run(
                    f"MERGE (n:{label} {{name: $name}}) "
                    f"SET n.source = $source, n.context = $context",
                    name=entity["name"],
                    source=entity.get("source", ""),
                    context=entity.get("context", "")[:500]
                )

        console.print(f"  Loading {len(graph_data['relationships'])} relationships...", style="bold")

        with self._driver.session() as session:
            for rel in graph_data["relationships"]:
                src_label = _sanitize_label(rel["source_type"])
                tgt_label = _sanitize_label(rel["target_type"])
                rel_type = _sanitize_label(rel["relationship"])
                try:
                    session.run(
                        f"MATCH (a:{src_label} {{name: $src_name}}) "
                        f"MATCH (b:{tgt_label} {{name: $tgt_name}}) "
                        f"MERGE (a)-[r:{rel_type}]->(b) "
                        f"SET r.evidence = $evidence, r.source_doc = $source_doc",
                        src_name=rel["source_entity"],
                        tgt_name=rel["target_entity"],
                        evidence=rel.get("evidence", "")[:300],
                        source_doc=rel.get("source_doc", "")
                    )
                except Exception:
                    pass

        final_count = self._get_node_count()
        console.print(f"  ✓ Graph built: {final_count} nodes", style="green")

    # ── Graph retrieval ───────────────────────────────────────

    def retrieve_subgraph(self, query: str, max_nodes: int = 15) -> list[dict]:
        """
        Find the most relevant subgraph for a query.
        Strategy:
          1. Find entities whose names appear in the query
          2. Expand to their 1-hop and 2-hop neighbours
          3. Return context assembled from the subgraph
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())

        # Step 1: Find seed entities matching the query
        seed_results = []
        with self._driver.session() as session:
            # Try full-text search first
            try:
                results = session.run(
                    "CALL db.index.fulltext.queryNodes('entity_search', $query) "
                    "YIELD node, score "
                    "RETURN labels(node)[0] AS type, node.name AS name, "
                    "node.context AS context, node.source AS source, score "
                    "LIMIT 10",
                    query=query
                )
                seed_results = [dict(r) for r in results]
            except Exception:
                pass

            # Fallback: keyword matching
            if not seed_results:
                results = session.run(
                    "MATCH (n) WHERE toLower(n.name) CONTAINS $kw "
                    "RETURN labels(n)[0] AS type, n.name AS name, "
                    "n.context AS context, n.source AS source "
                    "LIMIT 10",
                    kw=list(query_words)[0] if query_words else ""
                )
                seed_results = [dict(r) for r in results]

        if not seed_results:
            return []

        # Step 2: Expand to neighbourhood
        context_nodes = []
        with self._driver.session() as session:
            for seed in seed_results[:5]:
                results = session.run(
                    "MATCH (n {name: $name})-[r*1..2]-(neighbour) "
                    "RETURN labels(n)[0] AS src_type, n.name AS src_name, "
                    "type(r[0]) AS rel_type, "
                    "labels(neighbour)[0] AS tgt_type, neighbour.name AS tgt_name, "
                    "neighbour.context AS tgt_context, neighbour.source AS tgt_source "
                    "LIMIT $limit",
                    name=seed["name"],
                    limit=max_nodes
                )
                for row in results:
                    context_nodes.append({
                        "path": f"{seed['name']} --[{row['rel_type']}]--> {row['tgt_name']}",
                        "src_name": seed["name"],
                        "src_type": seed["type"],
                        "rel_type": row["rel_type"],
                        "tgt_name": row["tgt_name"],
                        "tgt_type": row["tgt_type"],
                        "context": row.get("tgt_context", ""),
                        "source": row.get("tgt_source", ""),
                    })

        # Also add the seed nodes' own context
        for seed in seed_results:
            context_nodes.insert(0, {
                "path": f"[{seed['type']}] {seed['name']}",
                "src_name": seed["name"],
                "src_type": seed["type"],
                "rel_type": "DIRECT_MATCH",
                "tgt_name": seed["name"],
                "tgt_type": seed["type"],
                "context": seed.get("context", ""),
                "source": seed.get("source", ""),
            })

        return context_nodes[:max_nodes]

    def _get_node_count(self) -> int:
        with self._driver.session() as session:
            return session.run("MATCH (n) RETURN count(n) as c").single()["c"]

    def get_stats(self) -> dict:
        """Return statistics about the knowledge graph."""
        with self._driver.session() as session:
            nodes = session.run("MATCH (n) RETURN count(n) as c").single()["c"]
            rels = session.run("MATCH ()-[r]->() RETURN count(r) as c").single()["c"]
            labels = session.run(
                "MATCH (n) RETURN labels(n)[0] as label, count(n) as count "
                "ORDER BY count DESC"
            )
            label_counts = {r["label"]: r["count"] for r in labels}
        return {"nodes": nodes, "relationships": rels, "by_label": label_counts}


def _sanitize_label(label: str) -> str:
    """Convert label to valid Neo4j identifier."""
    return re.sub(r"[^a-zA-Z0-9_]", "_", label) if label else "Unknown"


import re  # needed by _sanitize_label
