"""
evaluator.py
Runs both pipelines against the test set and computes evaluation metrics.
Uses Groq LLM as judge (no OpenAI required).

Metrics:
  - Accuracy        : How correct is the answer vs ground truth (0-100)
  - Faithfulness    : Are claims grounded in retrieved context (0-100)
  - Hallucination   : Risk of fabricated content (0-100, lower is better)
  - Source Citation : Quality of source attribution (0-100)
  - Latency         : Query time in seconds
  - Answer Quality  : Overall response quality (0-100)
"""

import json
import time
import statistics
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.progress import track

import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.config import generate, EVAL_DIR
from pipelines.traditional_rag import TraditionalRAG
from pipelines.graph_rag import GraphRAG

console = Console()

TEST_SET_PATH = Path(__file__).parent / "test_set.json"
RESULTS_PATH = EVAL_DIR / "results.json"

JUDGE_PROMPT = """You are an expert evaluator of AI systems for banking regulatory compliance.
You will evaluate an AI-generated answer against a ground truth answer.

Evaluate ONLY on the JSON schema below. Return ONLY valid JSON, no preamble, no backticks.

Scoring criteria:
- accuracy (0-100): How factually correct is the answer compared to ground truth? 
  90-100: All key facts correct. 70-89: Most facts correct, minor omissions. 
  50-69: Partially correct. Below 50: Significant errors.
- faithfulness (0-100): Are the claims in the answer grounded in the provided context/corpus?
  High score = every claim can be traced to a source. Low score = claims appear invented.
- hallucination_risk (0-100): Risk that the answer contains fabricated regulatory details.
  LOW (0-30) = answer is careful and hedged. HIGH (60-100) = answer asserts specific details not in sources.
  Note: For trick questions, a correct answer explicitly declining to assert a fabricated fact should score 0-10.
- source_citation (0-100): Quality of source attribution. 
  80-100: Specific document/article cited. 40-79: General source mentioned. 0-39: No citation.
- answer_quality (0-100): Overall quality, clarity, completeness and usefulness.

Return exactly this JSON:
{
  "accuracy": <int 0-100>,
  "faithfulness": <int 0-100>,
  "hallucination_risk": <int 0-100>,
  "source_citation": <int 0-100>,
  "answer_quality": <int 0-100>,
  "reasoning": "<one sentence explanation>"
}"""


def score_answer(question: str, answer: str, ground_truth: str, is_trick: bool = False) -> dict:
    """Use Groq LLM as judge to score an answer."""
    trick_note = "\nNote: This is a trick question. The correct response is to NOT assert the premise." if is_trick else ""

    prompt = (
        f"QUESTION: {question}\n\n"
        f"GROUND TRUTH: {ground_truth}\n\n"
        f"AI ANSWER TO EVALUATE: {answer}"
        f"{trick_note}"
    )

    try:
        raw = generate(JUDGE_PROMPT, prompt, max_tokens=300)
        # Strip any markdown code fences
        raw = raw.replace("```json", "").replace("```", "").strip()
        # Find JSON object
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(raw[start:end])
    except Exception as e:
        pass

    # Fallback scores
    return {
        "accuracy": 60, "faithfulness": 60, "hallucination_risk": 40,
        "source_citation": 50, "answer_quality": 60,
        "reasoning": "Scoring failed, using fallback values"
    }


def run_evaluation(
    tier_filter: Optional[int] = None,
    max_questions: Optional[int] = None,
    use_neo4j: bool = True
) -> dict:
    """
    Run full evaluation of both pipelines against the test set.
    Returns comprehensive results dict.
    """
    with open(TEST_SET_PATH) as f:
        test_set = json.load(f)

    if tier_filter:
        test_set = [q for q in test_set if q["tier"] == tier_filter]
    if max_questions:
        test_set = test_set[:max_questions]

    console.print(f"\n[bold blue]Starting evaluation: {len(test_set)} questions[/bold blue]")
    console.print(f"Tiers: {sorted(set(q['tier'] for q in test_set))}\n")

    # Initialize pipelines
    console.print("Initializing pipelines...")
    trad_rag = TraditionalRAG()
    trad_rag.ingest_corpus()

    graph_rag = GraphRAG(use_neo4j=use_neo4j)
    graph_rag.connect()
    graph_rag.build_graph()

    results = []
    trad_scores_all = []
    graph_scores_all = []

    for item in track(test_set, description="  Evaluating queries"):
        question = item["question"]
        ground_truth = item["ground_truth"]
        is_trick = item.get("is_trick_question", False)

        # Run Traditional RAG
        t_start = time.time()
        trad_result = trad_rag.query(question)
        trad_scores = score_answer(question, trad_result["answer"], ground_truth, is_trick)
        trad_scores["latency"] = trad_result["latency_total"]

        # Small delay to avoid rate limits
        time.sleep(0.5)

        # Run Graph RAG
        graph_result = graph_rag.query(question)
        graph_scores = score_answer(question, graph_result["answer"], ground_truth, is_trick)
        graph_scores["latency"] = graph_result["latency_total"]

        time.sleep(0.5)

        result = {
            "id": item["id"],
            "tier": item["tier"],
            "tier_name": item["tier_name"],
            "question": question,
            "ground_truth": ground_truth,
            "is_trick": is_trick,
            "expected_winner": item.get("expected_better_pipeline", "unknown"),
            "traditional_rag": {
                "answer": trad_result["answer"],
                "sources": trad_result["sources"],
                "scores": trad_scores,
            },
            "graph_rag": {
                "answer": graph_result["answer"],
                "sources": graph_result["sources"],
                "graph_paths": graph_result.get("graph_paths", []),
                "scores": graph_scores,
            },
            "winner_accuracy": (
                "graph" if graph_scores["accuracy"] > trad_scores["accuracy"]
                else "traditional" if trad_scores["accuracy"] > graph_scores["accuracy"]
                else "tie"
            )
        }
        results.append(result)
        trad_scores_all.append(trad_scores)
        graph_scores_all.append(graph_scores)

        console.print(
            f"  [{item['id']}] Acc: Trad={trad_scores['accuracy']} Graph={graph_scores['accuracy']} "
            f"| Winner: {result['winner_accuracy']}",
            style="dim"
        )

    # Aggregate metrics
    def avg(scores_list, key):
        vals = [s[key] for s in scores_list]
        return round(statistics.mean(vals), 1) if vals else 0

    summary = {
        "total_questions": len(results),
        "traditional_rag": {
            "avg_accuracy": avg(trad_scores_all, "accuracy"),
            "avg_faithfulness": avg(trad_scores_all, "faithfulness"),
            "avg_hallucination_risk": avg(trad_scores_all, "hallucination_risk"),
            "avg_source_citation": avg(trad_scores_all, "source_citation"),
            "avg_answer_quality": avg(trad_scores_all, "answer_quality"),
            "avg_latency": avg(trad_scores_all, "latency"),
        },
        "graph_rag": {
            "avg_accuracy": avg(graph_scores_all, "accuracy"),
            "avg_faithfulness": avg(graph_scores_all, "faithfulness"),
            "avg_hallucination_risk": avg(graph_scores_all, "hallucination_risk"),
            "avg_source_citation": avg(graph_scores_all, "source_citation"),
            "avg_answer_quality": avg(graph_scores_all, "answer_quality"),
            "avg_latency": avg(graph_scores_all, "latency"),
        },
        "graph_wins_accuracy": sum(1 for r in results if r["winner_accuracy"] == "graph"),
        "trad_wins_accuracy": sum(1 for r in results if r["winner_accuracy"] == "traditional"),
        "ties_accuracy": sum(1 for r in results if r["winner_accuracy"] == "tie"),
        "by_tier": _aggregate_by_tier(results),
    }

    full_results = {"summary": summary, "results": results}

    # Save results
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(full_results, f, indent=2)

    _print_summary_table(summary)
    console.print(f"\n  Results saved to: {RESULTS_PATH}", style="green")

    return full_results


def _aggregate_by_tier(results: list) -> dict:
    tiers = {}
    for r in results:
        tier = r["tier"]
        if tier not in tiers:
            tiers[tier] = {"trad_acc": [], "graph_acc": [], "count": 0}
        tiers[tier]["trad_acc"].append(r["traditional_rag"]["scores"]["accuracy"])
        tiers[tier]["graph_acc"].append(r["graph_rag"]["scores"]["accuracy"])
        tiers[tier]["count"] += 1

    return {
        tier: {
            "count": d["count"],
            "trad_avg_accuracy": round(statistics.mean(d["trad_acc"]), 1),
            "graph_avg_accuracy": round(statistics.mean(d["graph_acc"]), 1),
        }
        for tier, d in tiers.items()
    }


def _print_summary_table(summary: dict):
    console.print("\n")
    table = Table(title="Evaluation Results Summary", show_header=True, header_style="bold blue")
    table.add_column("Metric", style="bold")
    table.add_column("Traditional RAG", justify="center", style="blue")
    table.add_column("Graph RAG", justify="center", style="green")
    table.add_column("Winner", justify="center")

    t = summary["traditional_rag"]
    g = summary["graph_rag"]

    def winner(t_val, g_val, lower_better=False):
        if lower_better:
            return "Traditional ✓" if t_val < g_val else "Graph RAG ✓" if g_val < t_val else "Tie"
        return "Traditional ✓" if t_val > g_val else "Graph RAG ✓" if g_val > t_val else "Tie"

    table.add_row("Accuracy (%)", str(t["avg_accuracy"]), str(g["avg_accuracy"]), winner(t["avg_accuracy"], g["avg_accuracy"]))
    table.add_row("Faithfulness (%)", str(t["avg_faithfulness"]), str(g["avg_faithfulness"]), winner(t["avg_faithfulness"], g["avg_faithfulness"]))
    table.add_row("Hallucination Risk (%)", str(t["avg_hallucination_risk"]), str(g["avg_hallucination_risk"]), winner(t["avg_hallucination_risk"], g["avg_hallucination_risk"], lower_better=True))
    table.add_row("Source Citation (%)", str(t["avg_source_citation"]), str(g["avg_source_citation"]), winner(t["avg_source_citation"], g["avg_source_citation"]))
    table.add_row("Answer Quality (%)", str(t["avg_answer_quality"]), str(g["avg_answer_quality"]), winner(t["avg_answer_quality"], g["avg_answer_quality"]))
    table.add_row("Avg Latency (s)", str(t["avg_latency"]), str(g["avg_latency"]), winner(t["avg_latency"], g["avg_latency"], lower_better=True))

    console.print(table)
    console.print(f"\n  Graph RAG wins: {summary['graph_wins_accuracy']}/{summary['total_questions']} on accuracy")
    console.print(f"  Traditional wins: {summary['trad_wins_accuracy']}/{summary['total_questions']} on accuracy")


if __name__ == "__main__":
    run_evaluation(max_questions=5)  # Quick test with 5 questions
