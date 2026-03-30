"""
traditional_rag.py
Full Traditional (Vector-based) RAG pipeline.

Architecture:
  PDF/TXT → Chunks (500 tokens, 50 overlap)
           → Embeddings (all-MiniLM-L6-v2, local)
           → ChromaDB (persistent vector store)
           → Top-5 cosine similarity retrieval
           → Groq LLM generation (Llama 3.3-70B)
"""

import time
import hashlib
from pathlib import Path
from typing import Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import fitz  # PyMuPDF
from rich.console import Console
from rich.progress import track

import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.config import (
    CORPUS_DIR, CHROMA_DIR, EMBEDDING_MODEL,
    CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_RETRIEVAL, generate
)

console = Console()

SYSTEM_PROMPT = """You are a regulatory compliance assistant for Banc Sabadell, a Spanish banking institution.
You answer questions about banking regulations, financial policies, and product guidelines strictly based on the provided document excerpts.

Rules:
- Answer ONLY based on the provided context. Do not use outside knowledge.
- Be precise and factual. Use specific terms from the documents.
- If the context does not contain enough information, say so explicitly.
- Always cite the source document and section when possible.
- Do not speculate or hallucinate regulatory details.
- Keep answers concise but complete (3-5 sentences for simple queries, more for complex ones).

After your answer, add a line formatted exactly as:
SOURCES: [list the document names and sections you used]
"""


class TraditionalRAG:
    """
    Vector-based RAG pipeline using local sentence embeddings and ChromaDB.
    """

    def __init__(self, collection_name: str = "banking_docs"):
        self.collection_name = collection_name
        self._embedding_model = None
        self._chroma_client = None
        self._collection = None

    @property
    def embedding_model(self) -> SentenceTransformer:
        if self._embedding_model is None:
            console.print(f"  Loading embedding model: {EMBEDDING_MODEL}...", style="dim")
            self._embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        return self._embedding_model

    @property
    def collection(self):
        if self._collection is None:
            CHROMA_DIR.mkdir(parents=True, exist_ok=True)
            self._chroma_client = chromadb.PersistentClient(
                path=str(CHROMA_DIR),
                settings=Settings(anonymized_telemetry=False)
            )
            self._collection = self._chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        return self._collection

    # ── Document ingestion ────────────────────────────────────

    def ingest_corpus(self, force_rebuild: bool = False) -> int:
        """
        Load all documents from corpus directory, chunk them, embed, and store.
        Returns number of chunks indexed.
        """
        existing_count = self.collection.count()
        if existing_count > 0 and not force_rebuild:
            console.print(f"  Vector index already contains {existing_count} chunks. Skipping rebuild.", style="dim")
            console.print("  Use force_rebuild=True to re-index.", style="dim")
            return existing_count

        if force_rebuild and existing_count > 0:
            console.print("  Force rebuilding index...", style="yellow")
            self._chroma_client.delete_collection(self.collection_name)
            self._collection = self._chroma_client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )

        all_files = list(CORPUS_DIR.rglob("*.pdf")) + list(CORPUS_DIR.rglob("*.txt"))
        if not all_files:
            raise FileNotFoundError(
                f"No documents found in {CORPUS_DIR}.\n"
                "Run: python3 setup/download_corpus.py"
            )

        console.print(f"\n  Indexing {len(all_files)} documents...", style="bold")
        total_chunks = 0

        for file_path in track(all_files, description="  Indexing documents"):
            chunks, metadatas = self._load_and_chunk(file_path)
            if not chunks:
                continue

            embeddings = self.embedding_model.encode(chunks, show_progress_bar=False).tolist()
            ids = [
                hashlib.md5(f"{file_path.name}:{i}:{chunk[:50]}".encode()).hexdigest()
                for i, chunk in enumerate(chunks)
            ]

            # Batch insert (ChromaDB recommends batches of ≤5000)
            batch_size = 500
            for i in range(0, len(chunks), batch_size):
                self.collection.add(
                    documents=chunks[i:i+batch_size],
                    embeddings=embeddings[i:i+batch_size],
                    metadatas=metadatas[i:i+batch_size],
                    ids=ids[i:i+batch_size]
                )
            total_chunks += len(chunks)

        console.print(f"  ✓ Indexed {total_chunks} chunks from {len(all_files)} documents", style="green")
        return total_chunks

    def _load_and_chunk(self, file_path: Path) -> tuple[list[str], list[dict]]:
        """Load a PDF or TXT file and split into overlapping chunks."""
        text = ""
        if file_path.suffix.lower() == ".pdf":
            try:
                doc = fitz.open(str(file_path))
                text = "\n".join(page.get_text() for page in doc)
                doc.close()
            except Exception as e:
                console.print(f"  Warning: Could not read PDF {file_path.name}: {e}", style="yellow")
                return [], []
        else:
            text = file_path.read_text(encoding="utf-8", errors="ignore")

        text = " ".join(text.split())  # normalise whitespace
        if len(text) < 100:
            return [], []

        # Simple word-based chunking with overlap
        words = text.split()
        chunks, metadatas = [], []
        i = 0
        chunk_idx = 0
        while i < len(words):
            chunk_words = words[i:i + CHUNK_SIZE]
            chunk_text = " ".join(chunk_words)
            chunks.append(chunk_text)
            metadatas.append({
                "source": file_path.name,
                "source_path": str(file_path),
                "chunk_index": chunk_idx,
                "doc_type": "pdf" if file_path.suffix.lower() == ".pdf" else "txt",
                "char_start": len(" ".join(words[:i])),
            })
            i += CHUNK_SIZE - CHUNK_OVERLAP
            chunk_idx += 1

        return chunks, metadatas

    # ── Retrieval ─────────────────────────────────────────────

    def retrieve(self, query: str, top_k: int = TOP_K_RETRIEVAL) -> list[dict]:
        """
        Retrieve the top-k most relevant chunks for a query using cosine similarity.
        Returns list of dicts with 'text', 'source', 'score'.
        """
        query_embedding = self.embedding_model.encode([query]).tolist()
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=min(top_k, self.collection.count()),
            include=["documents", "metadatas", "distances"]
        )

        chunks = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            chunks.append({
                "text": doc,
                "source": meta.get("source", "unknown"),
                "chunk_index": meta.get("chunk_index", 0),
                "similarity_score": round(1 - dist, 4),  # convert distance to similarity
            })
        return chunks

    # ── Full pipeline query ───────────────────────────────────

    def query(self, question: str, top_k: int = TOP_K_RETRIEVAL) -> dict:
        """
        Full RAG query: retrieve → build context → generate answer.
        Returns dict with answer, sources, latency, and retrieved chunks.
        """
        t_start = time.time()

        # Retrieve relevant chunks
        t_retrieve_start = time.time()
        chunks = self.retrieve(question, top_k=top_k)
        t_retrieve = time.time() - t_retrieve_start

        if not chunks:
            return {
                "answer": "No relevant documents found in the corpus for this query.",
                "sources": [],
                "chunks": [],
                "latency_total": time.time() - t_start,
                "latency_retrieval": t_retrieve,
                "latency_generation": 0,
                "pipeline": "Traditional RAG",
                "method": "vector_cosine_similarity",
            }

        # Build context from retrieved chunks
        context_parts = []
        for i, chunk in enumerate(chunks):
            context_parts.append(
                f"[Document {i+1}: {chunk['source']} | Similarity: {chunk['similarity_score']}]\n"
                f"{chunk['text']}"
            )
        context = "\n\n---\n\n".join(context_parts)

        prompt_with_context = (
            f"Based on the following regulatory document excerpts, answer the question.\n\n"
            f"CONTEXT:\n{context}\n\n"
            f"QUESTION: {question}"
        )

        # Generate answer
        t_gen_start = time.time()
        raw_answer = generate(SYSTEM_PROMPT, prompt_with_context)
        t_gen = time.time() - t_gen_start

        # Parse sources from answer
        answer_text, sources = _parse_sources(raw_answer)

        return {
            "answer": answer_text,
            "sources": sources if sources else [c["source"] for c in chunks[:3]],
            "chunks": chunks,
            "latency_total": round(time.time() - t_start, 3),
            "latency_retrieval": round(t_retrieve, 3),
            "latency_generation": round(t_gen, 3),
            "pipeline": "Traditional RAG",
            "method": "vector_cosine_similarity",
            "top_k": top_k,
            "num_chunks_indexed": self.collection.count(),
        }


def _parse_sources(raw_answer: str) -> tuple[str, list[str]]:
    """Extract SOURCES line from raw answer."""
    lines = raw_answer.strip().split("\n")
    sources = []
    answer_lines = []
    for line in lines:
        if line.strip().upper().startswith("SOURCES:"):
            src_text = line.split(":", 1)[1].strip()
            sources = [s.strip() for s in src_text.replace("[", "").replace("]", "").split(",") if s.strip()]
        else:
            answer_lines.append(line)
    return "\n".join(answer_lines).strip(), sources


# ── Standalone usage ──────────────────────────────────────────

if __name__ == "__main__":
    console.print("\n[bold blue]Traditional RAG Pipeline — Test Run[/bold blue]\n")

    rag = TraditionalRAG()

    console.print("Building vector index...")
    rag.ingest_corpus()

    test_query = "What are the customer due diligence requirements under AML regulations?"
    console.print(f"\n[bold]Query:[/bold] {test_query}\n")

    result = rag.query(test_query)

    console.print(f"[bold green]Answer:[/bold green]\n{result['answer']}\n")
    console.print(f"[bold]Sources:[/bold] {', '.join(result['sources'])}")
    console.print(f"[bold]Latency:[/bold] {result['latency_total']}s total "
                  f"({result['latency_retrieval']}s retrieval + {result['latency_generation']}s generation)")
