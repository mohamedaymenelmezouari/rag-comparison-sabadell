"""
demo.py — Professional Streamlit UI for RAG Comparison
Launch: streamlit run app/demo.py
"""

import sys
import time
import json
from pathlib import Path

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))
from config.config import check_config, EVAL_DIR

st.set_page_config(
    page_title="RAG Comparison · Banc Sabadell",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #F8FAFC; }

section[data-testid="stSidebar"] { background: #0A1628 !important; border-right: 1px solid #1E2D45; }
section[data-testid="stSidebar"] * { color: #CBD5E1 !important; }
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 { color: white !important; }
section[data-testid="stSidebar"] .stButton button { background: #0072BC !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; width: 100%; padding: 0.6rem 1rem !important; }

.hero { background: linear-gradient(135deg, #0A1628 0%, #0072BC 100%); border-radius: 16px; padding: 2rem 2.5rem; margin-bottom: 1.5rem; display: flex; align-items: center; justify-content: space-between; }
.hero h1 { color: white; font-size: 1.8rem; font-weight: 700; margin: 0; }
.hero p { color: rgba(255,255,255,0.7); margin: 0.3rem 0 0; font-size: 0.9rem; }
.hero-badge { background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.3); border-radius: 20px; padding: 0.4rem 1rem; color: white !important; font-size: 0.8rem; font-weight: 600; }

.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.5rem; }
.stat-card { background: white; border-radius: 12px; padding: 1.25rem 1.5rem; border: 1px solid #E2E8F0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.stat-label { font-size: 0.72rem; color: #64748B; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.4rem; }
.stat-value { font-size: 1.9rem; font-weight: 700; color: #0F172A; line-height: 1; }
.stat-sub { font-size: 0.72rem; color: #94A3B8; margin-top: 0.3rem; }

.pipeline-card { background: white; border-radius: 16px; border: 1px solid #E2E8F0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); overflow: hidden; margin-bottom: 1rem; }
.pipeline-header { padding: 1rem 1.5rem; display: flex; align-items: center; justify-content: space-between; }
.ph-trad { background: linear-gradient(90deg, #EFF6FF, #DBEAFE); border-bottom: 2px solid #3B82F6; }
.ph-graph { background: linear-gradient(90deg, #F0FDF4, #DCFCE7); border-bottom: 2px solid #10B981; }
.pipeline-title { font-weight: 700; font-size: 1rem; }
.pt-trad { color: #1D4ED8; }
.pt-graph { color: #047857; }
.pipeline-badge { font-size: 0.7rem; padding: 0.2rem 0.7rem; border-radius: 20px; font-weight: 600; }
.pb-trad { background: #DBEAFE; color: #1D4ED8; }
.pb-graph { background: #DCFCE7; color: #047857; }
.pipeline-body { padding: 1.5rem; }
.pipeline-answer { font-size: 0.9rem; line-height: 1.8; color: #334155; }
.source-chip { display: inline-block; background: #F1F5F9; border: 1px solid #E2E8F0; border-radius: 20px; padding: 0.2rem 0.7rem; font-size: 0.72rem; color: #475569; margin: 0.2rem 0.2rem 0 0; }
.graph-path-card { background: #F0FDF4; border: 1px dashed #86EFAC; border-radius: 8px; padding: 0.6rem 0.9rem; font-family: monospace; font-size: 0.78rem; color: #047857; margin-top: 0.5rem; }
.section-hdr { font-size: 1rem; font-weight: 700; color: #0F172A; margin: 1.5rem 0 1rem; display: flex; align-items: center; gap: 0.5rem; }
.section-hdr::before { content:''; display:block; width:4px; height:20px; background:#0072BC; border-radius:2px; }

.stTabs [data-baseweb="tab-list"] { gap:0; background:white; border-radius:12px; padding:0.3rem; border:1px solid #E2E8F0; margin-bottom:1.5rem; }
.stTabs [data-baseweb="tab"] { border-radius:8px; padding:0.5rem 1.2rem; font-weight:500; font-size:0.875rem; color:#64748B; }
.stTabs [aria-selected="true"] { background:#0072BC !important; color:white !important; }

.arch-box { background:white; border-radius:12px; padding:1.5rem; border:1px solid #E2E8F0; margin-bottom:1rem; }
.arch-steps { display:flex; align-items:center; flex-wrap:wrap; gap:0.4rem; margin-top:0.75rem; }
.arch-step { padding:0.35rem 0.8rem; border-radius:20px; font-size:0.78rem; font-weight:600; }
.s-input { background:#F1F5F9; color:#475569; }
.s-trad { background:#DBEAFE; color:#1D4ED8; }
.s-graph { background:#DCFCE7; color:#047857; }
.s-out { background:#FEF9C3; color:#854D0E; }
.arr { color:#94A3B8; font-size:1rem; }
.insight { background:#EFF6FF; border-left:4px solid #3B82F6; border-radius:0 8px 8px 0; padding:0.75rem 1rem; margin-top:0.75rem; font-size:0.82rem; color:#1E40AF; }
.insight-g { background:#F0FDF4; border-left:4px solid #10B981; border-radius:0 8px 8px 0; padding:0.75rem 1rem; margin-top:0.75rem; font-size:0.82rem; color:#065F46; }

.chunk-card { border:1px solid #E2E8F0; border-radius:8px; padding:0.75rem; margin-top:0.5rem; background:#FAFAFA; }

#MainMenu { visibility:hidden; } footer { visibility:hidden; } .stDeployButton { display:none; } header { visibility:hidden; }
.stTextArea textarea { border-radius:10px !important; border:1.5px solid #E2E8F0 !important; font-size:0.9rem !important; }
.stTextArea textarea:focus { border-color:#0072BC !important; }
.stButton > button[kind="primary"] { background:#0072BC !important; color:white !important; border:none !important; border-radius:10px !important; font-weight:600 !important; padding:0.6rem 2rem !important; box-shadow:0 4px 12px rgba(0,114,188,0.3) !important; }
.stButton > button[kind="primary"]:hover { background:#005fa3 !important; transform:translateY(-1px) !important; }
div[data-testid="stProgress"] > div > div { background:#0072BC !important; border-radius:10px !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────
for k, v in [("trad_rag", None), ("graph_rag", None), ("query_history", []), ("pipelines_ready", False), ("last_result", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div style='text-align:center;padding:1rem 0 0.5rem;'><div style='background:#0072BC;border-radius:12px;padding:0.6rem 1.2rem;display:inline-block;margin-bottom:0.5rem;'><span style='color:white;font-weight:800;font-size:1.2rem;letter-spacing:1px;'>B Sabadell</span></div><p style='color:#94A3B8;font-size:0.75rem;margin:0;'>ESADE Capstone 2026</p></div>", unsafe_allow_html=True)
    st.markdown("---")

    status = check_config()
    st.markdown("<p style='color:#94A3B8;font-size:0.72rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.5rem;'>System status</p>", unsafe_allow_html=True)
    for label, ok in [("Groq API key", status["groq_key"]), (f"Corpus ({status['corpus_files']} files)", status["corpus_files"] > 0), ("Vector index (ChromaDB)", status["chroma_exists"]), ("Graph cache (Neo4j)", status["graph_cache_exists"])]:
        icon, color = ("✓", "#10B981") if ok else ("✗", "#EF4444")
        st.markdown(f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:6px;'><span style='color:{color};font-weight:700;'>{icon}</span><span style='font-size:0.82rem;color:#CBD5E1;'>{label}</span></div>", unsafe_allow_html=True)

    if not status["groq_key"]:
        st.error("Add GROQ_API_KEY to .env")
        st.stop()

    st.markdown("---")
    use_neo4j = st.toggle("Use Neo4j", value=True)

    if not st.session_state.pipelines_ready:
        if st.button("🚀 Initialize Pipelines", type="primary", use_container_width=True):
            with st.spinner("Loading..."):
                from pipelines.traditional_rag import TraditionalRAG
                from pipelines.graph_rag import GraphRAG
                trad = TraditionalRAG()
                trad.ingest_corpus()
                st.session_state.trad_rag = trad
                graph = GraphRAG(use_neo4j=use_neo4j)
                graph.connect()
                graph.build_graph()
                st.session_state.graph_rag = graph
                st.session_state.pipelines_ready = True
            st.rerun()
    else:
        st.markdown("<div style='background:#0A2E1A;border:1px solid #10B981;border-radius:8px;padding:0.5rem;text-align:center;'><span style='color:#10B981;font-weight:600;font-size:0.85rem;'>● Pipelines ready</span></div>", unsafe_allow_html=True)
        if st.button("↺ Rebuild", use_container_width=True):
            st.session_state.pipelines_ready = False
            st.session_state.trad_rag = None
            st.session_state.graph_rag = None
            st.rerun()

    st.markdown("---")
    st.markdown("<p style='color:#94A3B8;font-size:0.72rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.5rem;'>Team</p>", unsafe_allow_html=True)
    for name in ["Mohamed Aymen Elmezouari", "Abhay Mathahalli", "Warren Liu"]:
        initials = "".join(w[0] for w in name.split()[:2])
        st.markdown(f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:6px;'><div style='width:26px;height:26px;border-radius:50%;background:#1E3A5F;display:flex;align-items:center;justify-content:center;font-size:0.65rem;font-weight:700;color:#93C5FD;flex-shrink:0;'>{initials}</div><span style='font-size:0.78rem;color:#CBD5E1;'>{name}</span></div>", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────
st.markdown("<div class='hero'><div><h1>🏦 Traditional RAG vs. Graph RAG</h1><p>Banking regulatory document retrieval · Banc Sabadell IT & Operations · ESADE Capstone 2026</p></div><span class='hero-badge'>Mid-Term Prototype</span></div>", unsafe_allow_html=True)

tab_demo, tab_eval, tab_arch, tab_hist = st.tabs(["⚡  Live Demo", "📊  Evaluation", "🏗️  Architecture", "📋  History"])

# ══════════════════════════════════════════════════════════════
# TAB 1 — LIVE DEMO
# ══════════════════════════════════════════════════════════════
with tab_demo:
    if not st.session_state.pipelines_ready:
        st.markdown("<div style='text-align:center;padding:4rem;background:white;border-radius:16px;border:1px solid #E2E8F0;'><div style='font-size:3rem;'>🚀</div><h3 style='color:#0F172A;'>Initialize the pipelines to get started</h3><p style='color:#64748B;'>Click Initialize Pipelines in the sidebar — ~30 seconds on first run.</p></div>", unsafe_allow_html=True)
        st.stop()

    presets = ["— type your own —", "What is the minimum CET1 capital ratio under Basel III?", "What CDD obligations apply to Politically Exposed Persons under AML?", "Which products require both MiFID II suitability and AML enhanced due diligence?", "How should banks handle GDPR data breaches and what are notification deadlines?", "What is the maximum fine for violating Basel III capital requirements?"]
    choice = st.selectbox("Quick preset", presets, label_visibility="collapsed")
    default_q = "" if choice == "— type your own —" else choice
    query = st.text_area("Query", value=default_q, placeholder="Ask anything about banking regulations, compliance, or financial products...", height=90, label_visibility="collapsed")

    c1, c2 = st.columns([4, 1])
    with c1:
        run = st.button("▶  Run Comparison", type="primary", disabled=not query.strip(), use_container_width=True)
    with c2:
        top_k = st.slider("k", 3, 10, 5, label_visibility="collapsed")
        st.caption(f"Top-k: {top_k}")

    if run and query.strip():
        prog = st.progress(0)
        msg = st.empty()
        msg.markdown("*⚡ Traditional RAG — retrieving chunks...*")
        prog.progress(15)
        t_res = st.session_state.trad_rag.query(query, top_k=top_k)
        prog.progress(55)
        msg.markdown("*🔗 Graph RAG — traversing knowledge graph...*")
        g_res = st.session_state.graph_rag.query(query)
        prog.progress(100)
        time.sleep(0.3)
        prog.empty(); msg.empty()
        st.session_state.last_result = {"query": query, "trad": t_res, "graph": g_res}
        st.session_state.query_history.append({"query": query, "trad": t_res, "graph": g_res, "timestamp": time.strftime("%H:%M:%S")})

    if st.session_state.last_result:
        t = st.session_state.last_result["trad"]
        g = st.session_state.last_result["graph"]
        tl, gl = t["latency_total"], g["latency_total"]
        delta = gl - tl
        dc = "#10B981" if delta < 0 else "#EF4444"

        st.markdown(f"""<div class="stat-grid">
            <div class="stat-card"><div class="stat-label">Traditional latency</div><div class="stat-value">{tl:.2f}s</div><div class="stat-sub">vector cosine similarity</div></div>
            <div class="stat-card"><div class="stat-label">Graph RAG latency</div><div class="stat-value">{gl:.2f}s</div><div class="stat-sub" style="color:{dc};font-weight:600;">{delta:+.2f}s vs Traditional</div></div>
            <div class="stat-card"><div class="stat-label">Chunks retrieved</div><div class="stat-value">{len(t.get('chunks', []))}</div><div class="stat-sub">top-{top_k} by similarity</div></div>
            <div class="stat-card"><div class="stat-label">Graph nodes found</div><div class="stat-value">{g.get('entities_found', 0)}</div><div class="stat-sub">entity relationships traversed</div></div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<div class='section-hdr'>Pipeline answers</div>", unsafe_allow_html=True)
        ca, cb = st.columns(2)

        with ca:
            chunks_html = ""
            for i, c in enumerate(t.get("chunks", [])[:3], 1):
                sim = c.get("similarity_score", 0)
                bw = int(sim * 100)
                chunks_html += f"<div class='chunk-card'><div style='display:flex;justify-content:space-between;margin-bottom:4px;'><span style='font-size:0.72rem;font-weight:600;color:#3B82F6;'>Chunk {i} — {c['source'][:30]}</span><span style='font-size:0.72rem;color:#64748B;'>{sim:.3f}</span></div><div style='height:4px;background:#E2E8F0;border-radius:2px;margin-bottom:6px;'><div style='height:100%;width:{bw}%;background:#3B82F6;border-radius:2px;'></div></div><p style='font-size:0.78rem;color:#475569;margin:0;line-height:1.5;'>{c['text'][:200]}...</p></div>"
            srcs = "".join(f'<span class="source-chip">📄 {s}</span>' for s in t["sources"][:4])
            st.markdown(f"""<div class="pipeline-card"><div class="pipeline-header ph-trad"><div><div class="pipeline-title pt-trad">🔵 Traditional RAG</div><div style='font-size:0.72rem;color:#64748B;'>ChromaDB · all-MiniLM-L6-v2 · Top-{top_k} cosine</div></div><span class="pipeline-badge pb-trad">Vector-based</span></div><div class="pipeline-body"><p class="pipeline-answer">{t['answer']}</p><div style='margin-top:1rem;padding-top:1rem;border-top:1px solid #F1F5F9;'><div style='font-size:0.72rem;font-weight:600;color:#64748B;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;'>Sources retrieved</div>{srcs}</div><div style='margin-top:1rem;'><div style='font-size:0.72rem;font-weight:600;color:#64748B;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;'>Top chunks</div>{chunks_html}</div></div></div>""", unsafe_allow_html=True)

        with cb:
            neo_label = "Neo4j" if g.get("neo4j_used") else "In-memory graph"
            paths = g.get("graph_paths", [])
            paths_html = "".join(f'<div class="graph-path-card">→ {p}</div>' for p in paths[:4]) if paths else "<div style='color:#94A3B8;font-size:0.82rem;font-style:italic;'>No graph paths found — entity matching refinement planned</div>"
            srcs_g = "".join(f'<span class="source-chip">📄 {s}</span>' for s in g["sources"][:4])
            st.markdown(f"""<div class="pipeline-card"><div class="pipeline-header ph-graph"><div><div class="pipeline-title pt-graph">🟢 Graph RAG</div><div style='font-size:0.72rem;color:#64748B;'>{neo_label} · Entity traversal · Relationship-aware</div></div><span class="pipeline-badge pb-graph">Knowledge graph</span></div><div class="pipeline-body"><p class="pipeline-answer">{g['answer']}</p><div style='margin-top:1rem;padding-top:1rem;border-top:1px solid #F1F5F9;'><div style='font-size:0.72rem;font-weight:600;color:#64748B;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;'>Graph traversal paths</div>{paths_html}</div><div style='margin-top:1rem;'><div style='font-size:0.72rem;font-weight:600;color:#64748B;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;'>Source documents</div>{srcs_g}</div></div></div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB 2 — EVALUATION
# ══════════════════════════════════════════════════════════════
with tab_eval:
    st.markdown("<div class='section-hdr'>Evaluation Dashboard</div>", unsafe_allow_html=True)

    history = st.session_state.query_history
    if history:
        atl = sum(h["trad"]["latency_total"] for h in history) / len(history)
        agl = sum(h["graph"]["latency_total"] for h in history) / len(history)
        st.markdown(f"""<div class="stat-grid">
            <div class="stat-card"><div class="stat-label">Session queries</div><div class="stat-value">{len(history)}</div><div class="stat-sub">this session</div></div>
            <div class="stat-card"><div class="stat-label">Avg Traditional latency</div><div class="stat-value" style="color:#3B82F6;">{atl:.2f}s</div></div>
            <div class="stat-card"><div class="stat-label">Avg Graph RAG latency</div><div class="stat-value" style="color:#10B981;">{agl:.2f}s</div></div>
            <div class="stat-card"><div class="stat-label">Graph overhead</div><div class="stat-value" style="color:{'#10B981' if agl<atl else '#EF4444'};">{agl-atl:+.2f}s</div></div>
        </div>""", unsafe_allow_html=True)

    rf = EVAL_DIR / "results.json"
    if rf.exists():
        with open(rf) as f:
            ev = json.load(f)
        s = ev["summary"]
        t, g = s["traditional_rag"], s["graph_rag"]

        ca, cb, cc = st.columns(3)
        ca.metric("Graph RAG wins", f"{s['graph_wins_accuracy']}/{s['total_questions']}")
        cb.metric("Traditional wins", f"{s['trad_wins_accuracy']}/{s['total_questions']}")
        cc.metric("Ties", f"{s['ties_accuracy']}/{s['total_questions']}")

        metrics = ["Accuracy", "Faithfulness", "Source Citation", "Answer Quality"]
        tv = [t["avg_accuracy"], t["avg_faithfulness"], t["avg_source_citation"], t["avg_answer_quality"]]
        gv = [g["avg_accuracy"], g["avg_faithfulness"], g["avg_source_citation"], g["avg_answer_quality"]]

        fig = go.Figure(data=[
            go.Bar(name="Traditional RAG", x=metrics, y=tv, marker_color="#3B82F6", text=[f"{v}%" for v in tv], textposition="outside"),
            go.Bar(name="Graph RAG", x=metrics, y=gv, marker_color="#10B981", text=[f"{v}%" for v in gv], textposition="outside"),
        ])
        fig.update_layout(barmode="group", yaxis_range=[0, 115], plot_bgcolor="white", paper_bgcolor="white",
                          font=dict(family="Inter", size=13), legend=dict(orientation="h", yanchor="bottom", y=1.02),
                          margin=dict(t=40, b=20, l=20, r=20), yaxis=dict(showgrid=True, gridcolor="#F1F5F9", ticksuffix="%"), xaxis=dict(showgrid=False))
        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            fig2 = go.Figure(go.Bar(x=["Traditional RAG", "Graph RAG"], y=[t["avg_hallucination_risk"], g["avg_hallucination_risk"]], marker_color=["#3B82F6", "#10B981"], text=[f"{t['avg_hallucination_risk']}%", f"{g['avg_hallucination_risk']}%"], textposition="outside"))
            fig2.update_layout(title="Hallucination risk % (lower = better)", yaxis_range=[0, 100], plot_bgcolor="white", paper_bgcolor="white", font=dict(family="Inter", size=12), margin=dict(t=50, b=20, l=20, r=20), yaxis=dict(showgrid=True, gridcolor="#F1F5F9", ticksuffix="%"))
            st.plotly_chart(fig2, use_container_width=True)
        with c2:
            fig3 = go.Figure(go.Bar(x=["Traditional RAG", "Graph RAG"], y=[t["avg_latency"], g["avg_latency"]], marker_color=["#3B82F6", "#10B981"], text=[f"{t['avg_latency']}s", f"{g['avg_latency']}s"], textposition="outside"))
            fig3.update_layout(title="Average latency in seconds (lower = better)", plot_bgcolor="white", paper_bgcolor="white", font=dict(family="Inter", size=12), margin=dict(t=50, b=20, l=20, r=20), yaxis=dict(showgrid=True, gridcolor="#F1F5F9"))
            st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No full evaluation yet. Run: `python3 evaluation/evaluator.py` in your terminal.")
        if st.session_state.pipelines_ready:
            if st.button("▶ Run Quick Evaluation (5 questions)", type="primary"):
                with st.spinner("Running... ~3 minutes"):
                    from evaluation.evaluator import run_evaluation
                    run_evaluation(max_questions=5)
                st.rerun()

# ══════════════════════════════════════════════════════════════
# TAB 3 — ARCHITECTURE
# ══════════════════════════════════════════════════════════════
with tab_arch:
    st.markdown("<div class='section-hdr'>System Architecture</div>", unsafe_allow_html=True)
    ca, cb = st.columns(2)
    with ca:
        st.markdown("""<div class="arch-box"><div style='font-weight:700;color:#1D4ED8;font-size:0.95rem;'>🔵 Traditional RAG Pipeline</div><div class="arch-steps"><span class="arch-step s-input">PDF/TXT</span><span class="arr">→</span><span class="arch-step s-trad">PyMuPDF</span><span class="arr">→</span><span class="arch-step s-trad">Chunking 500 tok</span><span class="arr">→</span><span class="arch-step s-trad">MiniLM embed</span><span class="arr">→</span><span class="arch-step s-trad">ChromaDB</span><span class="arr">→</span><span class="arch-step s-trad">Top-k cosine</span><span class="arr">→</span><span class="arch-step s-out">Groq Llama 3.3</span></div><div class="insight"><strong>Strengths:</strong> Fast build, low latency, easy updates.<br><strong>Weaknesses:</strong> Loses entity relationships, semantic noise.</div></div>""", unsafe_allow_html=True)
    with cb:
        st.markdown("""<div class="arch-box"><div style='font-weight:700;color:#047857;font-size:0.95rem;'>🟢 Graph RAG Pipeline</div><div class="arch-steps"><span class="arch-step s-input">PDF/TXT</span><span class="arr">→</span><span class="arch-step s-graph">spaCy NER</span><span class="arr">→</span><span class="arch-step s-graph">Entity extract</span><span class="arr">→</span><span class="arch-step s-graph">Neo4j graph</span><span class="arr">→</span><span class="arch-step s-graph">Cypher query</span><span class="arr">→</span><span class="arch-step s-graph">Subgraph ctx</span><span class="arr">→</span><span class="arch-step s-out">Groq Llama 3.3</span></div><div class="insight-g"><strong>Strengths:</strong> Captures relationships, better multi-hop, explicit citations.<br><strong>Weaknesses:</strong> Slower build, higher latency, harder maintenance.</div></div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-hdr'>Technology Stack</div>", unsafe_allow_html=True)
    st.dataframe(pd.DataFrame({"Component": ["LLM", "Embeddings", "Vector store", "Graph DB", "NLP/NER", "Evaluation", "Frontend"], "Technology": ["Llama 3.3-70B via Groq API", "all-MiniLM-L6-v2 (local)", "ChromaDB 0.4.x", "Neo4j Community 5.x + APOC", "spaCy en_core_web_sm", "LLM-as-judge + Ragas", "Streamlit + Plotly"], "Role": ["Generation (both pipelines)", "Document & query embedding", "Vector similarity search", "Knowledge graph storage", "Entity & relationship extraction", "Accuracy, hallucination, faithfulness", "Interactive demo"]}), use_container_width=True, hide_index=True)

    st.markdown("<div class='section-hdr'>Corpus (9 files, ~750 pages)</div>", unsafe_allow_html=True)
    st.dataframe(pd.DataFrame({"Document": ["Basel III BIS Framework", "MiFID II Directive 2014/65/EU", "GDPR Regulation 2016/679/EU", "Sabadell Pillar III 2025", "Sabadell Annual Report 2025", "EBA AML Sample (txt)", "Basel III Sample (txt)", "GDPR Banking Sample (txt)", "MiFID II Sample (txt)"], "Size": ["1.2 MB", "1.8 MB", "959 KB", "33 MB", "38 MB", "2.4 KB", "2.7 KB", "3.1 KB", "2.9 KB"], "Status": ["✅", "✅", "✅", "✅", "✅", "✅", "✅", "✅", "✅"]}), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
# TAB 4 — HISTORY
# ══════════════════════════════════════════════════════════════
with tab_hist:
    st.markdown("<div class='section-hdr'>Query History</div>", unsafe_allow_html=True)
    if not st.session_state.query_history:
        st.markdown("<div style='text-align:center;padding:3rem;background:white;border-radius:16px;border:1px solid #E2E8F0;'><div style='font-size:2.5rem;'>📋</div><p style='color:#64748B;'>No queries yet. Run a comparison in the Live Demo tab.</p></div>", unsafe_allow_html=True)
    else:
        c1, c2 = st.columns([4, 1])
        c1.caption(f"{len(st.session_state.query_history)} queries this session")
        with c2:
            if st.button("🗑 Clear"):
                st.session_state.query_history = []
                st.session_state.last_result = None
                st.rerun()
        for item in reversed(st.session_state.query_history):
            tl, gl = item["trad"]["latency_total"], item["graph"]["latency_total"]
            faster = "Graph RAG" if gl < tl else "Traditional RAG"
            fc = "#047857" if gl < tl else "#1D4ED8"
            with st.expander(f"[{item['timestamp']}]  {item['query'][:80]}"):
                ca, cb = st.columns(2)
                with ca:
                    st.markdown(f"<div style='font-weight:700;color:#1D4ED8;margin-bottom:6px;'>🔵 Traditional RAG <span style='font-size:0.75rem;font-weight:400;color:#64748B;'>({tl:.2f}s)</span></div>", unsafe_allow_html=True)
                    st.write(item["trad"]["answer"])
                    if item["trad"]["sources"]:
                        st.markdown("**Sources:** " + " · ".join(item["trad"]["sources"][:3]))
                with cb:
                    st.markdown(f"<div style='font-weight:700;color:#047857;margin-bottom:6px;'>🟢 Graph RAG <span style='font-size:0.75rem;font-weight:400;color:#64748B;'>({gl:.2f}s)</span></div>", unsafe_allow_html=True)
                    st.write(item["graph"]["answer"])
                    if item["graph"].get("graph_paths"):
                        for p in item["graph"]["graph_paths"][:2]:
                            st.markdown(f"<div class='graph-path-card'>→ {p}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='margin-top:10px;padding-top:10px;border-top:1px solid #F1F5F9;font-size:0.8rem;color:{fc};font-weight:600;'>⚡ Faster pipeline: {faster}</div>", unsafe_allow_html=True)
