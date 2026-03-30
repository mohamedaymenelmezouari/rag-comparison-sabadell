"""
build_index.py
Run this ONCE after setup to build both the vector index and knowledge graph.
Usage: python3 setup/build_index.py
"""

import sys
from pathlib import Path
from rich.console import Console

sys.path.append(str(Path(__file__).parent.parent))

console = Console()

def main():
    console.print("\n[bold blue]" + "="*60 + "[/bold blue]")
    console.print("[bold blue]  Building RAG Indexes[/bold blue]")
    console.print("[bold blue]  Banc Sabadell Capstone 2026[/bold blue]")
    console.print("[bold blue]" + "="*60 + "[/bold blue]\n")

    from config.config import check_config, CORPUS_DIR

    # Check config
    status = check_config()
    console.print("[bold]Configuration check:[/bold]")
    console.print(f"  Groq API key: {'✓' if status['groq_key'] else '✗ Missing — add to .env'}")
    console.print(f"  Neo4j password: {'✓' if status['neo4j_password'] else '✗ Set in .env'}")
    console.print(f"  Corpus files: {status['corpus_files']} files found")

    if not status["groq_key"]:
        console.print("\n[red]ERROR: GROQ_API_KEY missing. Add it to .env and retry.[/red]")
        sys.exit(1)

    if status["corpus_files"] == 0:
        console.print("\n[yellow]No corpus files found. Running download script first...[/yellow]")
        from setup.download_corpus import main as download_main
        download_main()

    # ── Step 1: Build vector index ────────────────────────────
    console.print("\n[bold]Step 1/2: Building Traditional RAG vector index...[/bold]")
    from pipelines.traditional_rag import TraditionalRAG
    trad = TraditionalRAG()
    count = trad.ingest_corpus(force_rebuild=False)
    console.print(f"  ✓ Vector index ready: {count} chunks\n")

    # ── Step 2: Extract entities and build graph ──────────────
    console.print("[bold]Step 2/2: Building Graph RAG knowledge graph...[/bold]")

    from graph.entity_extractor import build_graph_cache
    graph_data = build_graph_cache(force_rebuild=False)

    # Try Neo4j
    from graph.neo4j_builder import Neo4jGraphBuilder
    neo4j_ok = False
    try:
        builder = Neo4jGraphBuilder()
        builder.connect()
        builder.setup_schema()
        builder.build_from_cache(force_rebuild=False)
        stats = builder.get_stats()
        builder.close()
        console.print(f"  ✓ Neo4j graph ready: {stats['nodes']} nodes, {stats['relationships']} relationships")
        neo4j_ok = True
    except Exception as e:
        console.print(f"  [yellow]Neo4j unavailable ({e})[/yellow]")
        console.print(f"  [yellow]Using in-memory graph fallback — demo will still work[/yellow]")
        console.print(f"  [dim]Graph cache: {len(graph_data['entities'])} entities, "
                      f"{len(graph_data['relationships'])} relationships[/dim]")

    # ── Summary ───────────────────────────────────────────────
    console.print("\n[bold green]" + "="*60 + "[/bold green]")
    console.print("[bold green]  All indexes built successfully![/bold green]")
    console.print("[bold green]" + "="*60 + "[/bold green]")
    console.print("\nTo launch the demo:")
    console.print("  [bold]streamlit run app/demo.py[/bold]")
    if not neo4j_ok:
        console.print("\n[yellow]Note: To enable Neo4j graph features:[/yellow]")
        console.print("  1. Download Neo4j Desktop: https://neo4j.com/download/")
        console.print("  2. Create a database and set the password in .env")
        console.print("  3. Re-run this script: python3 setup/build_index.py")

if __name__ == "__main__":
    main()
