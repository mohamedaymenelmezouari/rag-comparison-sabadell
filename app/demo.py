"""
demo.py — Professional Dark-Theme Streamlit UI for RAG Comparison
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

# ── Banc Sabadell SVG logo (inline, no external assets needed) ──────────────
LOGO_SIDEBAR = """
<svg width="160" height="52" viewBox="0 0 160 52" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="44" height="44" x="0" y="4" rx="10" fill="#E31837"/>
  <text x="8" y="22" font-family="Georgia,serif" font-size="16" font-weight="900" fill="white">B</text>
  <text x="8" y="40" font-family="Georgia,serif" font-size="16" font-weight="900" fill="white">S</text>
  <text x="52" y="24" font-family="Inter,Arial,sans-serif" font-size="13" font-weight="700" fill="white">Banc</text>
  <text x="52" y="40" font-family="Inter,Arial,sans-serif" font-size="13" font-weight="700" fill="white">Sabadell</text>
  <rect x="52" y="44" width="72" height="2" rx="1" fill="#E31837"/>
</svg>
"""

LOGO_HERO = """
<svg width="140" height="48" viewBox="0 0 140 48" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="40" height="40" x="0" y="4" rx="8" fill="#E31837"/>
  <text x="7" y="20" font-family="Georgia,serif" font-size="14" font-weight="900" fill="white">B</text>
  <text x="7" y="37" font-family="Georgia,serif" font-size="14" font-weight="900" fill="white">S</text>
  <text x="48" y="22" font-family="Inter,Arial,sans-serif" font-size="12" font-weight="700" fill="white">Banc</text>
  <text x="48" y="37" font-family="Inter,Arial,sans-serif" font-size="12" font-weight="700" fill="white">Sabadell</text>
  <rect x="48" y="41" width="64" height="2" rx="1" fill="#E31837"/>
</svg>
"""

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Base dark background ── */
.stApp { background: #070D1A !important; }
[data-testid="stAppViewContainer"] { background: #070D1A !important; }
[data-testid="stMain"] { background: #070D1A !important; }
.main .block-container { background: transparent !important; padding-top: 1rem !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #040810 !important;
    border-right: 1px solid #1A2745 !important;
}
section[data-testid="stSidebar"] * { color: #94A3B8 !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #F1F5F9 !important; }
section[data-testid="stSidebar"] .stButton button {
    background: #E31837 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    width: 100%;
    padding: 0.6rem 1rem !important;
    letter-spacing: 0.02em !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: #c0132d !important;
    transform: translateY(-1px) !important;
}
section[data-testid="stSidebar"] hr { border-color: #1A2745 !important; }
section[data-testid="stSidebar"] [data-testid="stToggle"] { filter: hue-rotate(200deg); }

/* ── Hero banner ── */
.hero {
    background: linear-gradient(135deg, #040810 0%, #0D1B3E 50%, #1a1040 100%);
    border: 1px solid #1A2745;
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 4px 32px rgba(0,0,0,0.5);
}
.hero-text h1 { color: #F1F5F9; font-size: 1.65rem; font-weight: 800; margin: 0; letter-spacing: -0.02em; }
.hero-text p  { color: #64748B; margin: 0.35rem 0 0; font-size: 0.875rem; }
.hero-right   { display: flex; flex-direction: column; align-items: flex-end; gap: 0.5rem; }
.hero-badge   {
    background: rgba(227,24,55,0.15);
    border: 1px solid rgba(227,24,55,0.4);
    border-radius: 20px;
    padding: 0.35rem 1rem;
    color: #FC8FA0 !important;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

/* ── Stat cards ── */
.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.5rem; }
.stat-card {
    background: #0D1728;
    border: 1px solid #1A2745;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}
.stat-label { font-size: 0.7rem; color: #475569; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.4rem; }
.stat-value { font-size: 1.85rem; font-weight: 800; color: #F1F5F9; line-height: 1; }
.stat-sub   { font-size: 0.7rem; color: #334155; margin-top: 0.3rem; }

/* ── Pipeline cards ── */
.pipeline-card {
    background: #0D1728;
    border: 1px solid #1A2745;
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 1rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.4);
}
.pipeline-header { padding: 1rem 1.5rem; display: flex; align-items: center; justify-content: space-between; }
.ph-trad  { background: linear-gradient(90deg, #0D1B3E, #0F2154); border-bottom: 2px solid #2563EB; }
.ph-graph { background: linear-gradient(90deg, #0B1F17, #0F2D1A); border-bottom: 2px solid #059669; }
.pipeline-title { font-weight: 800; font-size: 1rem; }
.pt-trad  { color: #93C5FD; }
.pt-graph { color: #6EE7B7; }
.pipeline-badge { font-size: 0.68rem; padding: 0.2rem 0.7rem; border-radius: 20px; font-weight: 700; letter-spacing: 0.04em; }
.pb-trad  { background: rgba(37,99,235,0.2); color: #93C5FD; border: 1px solid rgba(37,99,235,0.3); }
.pb-graph { background: rgba(5,150,105,0.2); color: #6EE7B7;  border: 1px solid rgba(5,150,105,0.3); }
.pipeline-body   { padding: 1.5rem; }
.pipeline-answer { font-size: 0.9rem; line-height: 1.85; color: #CBD5E1; }
.source-chip {
    display: inline-block;
    background: rgba(255,255,255,0.05);
    border: 1px solid #1E3251;
    border-radius: 20px;
    padding: 0.2rem 0.7rem;
    font-size: 0.7rem;
    color: #64748B;
    margin: 0.2rem 0.2rem 0 0;
}
.graph-path-card {
    background: rgba(5,150,105,0.08);
    border: 1px dashed rgba(5,150,105,0.3);
    border-radius: 8px;
    padding: 0.6rem 0.9rem;
    font-family: 'SF Mono', 'Fira Code', monospace;
    font-size: 0.76rem;
    color: #6EE7B7;
    margin-top: 0.4rem;
}
.chunk-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid #1A2745;
    border-radius: 8px;
    padding: 0.75rem;
    margin-top: 0.5rem;
}

/* ── Section headers ── */
.section-hdr {
    font-size: 0.95rem;
    font-weight: 700;
    color: #E2E8F0;
    margin: 1.5rem 0 1rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.section-hdr::before {
    content: '';
    display: block;
    width: 4px;
    height: 20px;
    background: #E31837;
    border-radius: 2px;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: #0D1728;
    border-radius: 12px;
    padding: 0.3rem;
    border: 1px solid #1A2745;
    margin-bottom: 1.5rem;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 0.5rem 1.2rem;
    font-weight: 500;
    font-size: 0.875rem;
    color: #475569 !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #94A3B8 !important; }
.stTabs [aria-selected="true"] {
    background: #E31837 !important;
    color: white !important;
}

/* ── Architecture boxes ── */
.arch-box {
    background: #0D1728;
    border: 1px solid #1A2745;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.arch-steps { display: flex; align-items: center; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.75rem; }
.arch-step  { padding: 0.35rem 0.8rem; border-radius: 20px; font-size: 0.76rem; font-weight: 600; }
.s-input { background: rgba(100,116,139,0.2); color: #94A3B8; }
.s-trad  { background: rgba(37,99,235,0.15);  color: #93C5FD; }
.s-graph { background: rgba(5,150,105,0.15);  color: #6EE7B7; }
.s-out   { background: rgba(245,158,11,0.15); color: #FCD34D; }
.arr     { color: #334155; font-size: 1rem; }
.insight   { background: rgba(37,99,235,0.08);  border-left: 3px solid #2563EB; border-radius: 0 8px 8px 0; padding: 0.75rem 1rem; margin-top: 0.75rem; font-size: 0.82rem; color: #93C5FD; }
.insight-g { background: rgba(5,150,105,0.08); border-left: 3px solid #059669; border-radius: 0 8px 8px 0; padding: 0.75rem 1rem; margin-top: 0.75rem; font-size: 0.82rem; color: #6EE7B7;  }

/* ── Dataframes ── */
[data-testid="stDataFrame"] { background: #0D1728 !important; border-radius: 10px; overflow: hidden; }
[data-testid="stDataFrame"] th { background: #0A1020 !important; color: #94A3B8 !important; font-weight: 600 !important; font-size: 0.78rem !important; text-transform: uppercase !important; letter-spacing: 0.04em !important; }
[data-testid="stDataFrame"] td { background: #0D1728 !important; color: #CBD5E1 !important; font-size: 0.85rem !important; }

/* ── Inputs & buttons ── */
.stTextArea textarea {
    background: #0D1728 !important;
    border: 1.5px solid #1A2745 !important;
    color: #F1F5F9 !important;
    border-radius: 10px !important;
    font-size: 0.9rem !important;
}
.stTextArea textarea:focus { border-color: #E31837 !important; }
.stTextArea textarea::placeholder { color: #334155 !important; }
.stSelectbox > div > div {
    background: #0D1728 !important;
    border-color: #1A2745 !important;
    color: #F1F5F9 !important;
}
.stButton > button[kind="primary"] {
    background: #E31837 !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    padding: 0.6rem 2rem !important;
    box-shadow: 0 4px 16px rgba(227,24,55,0.35) !important;
    letter-spacing: 0.02em !important;
}
.stButton > button[kind="primary"]:hover {
    background: #c0132d !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(227,24,55,0.45) !important;
}
div[data-testid="stProgress"] > div > div { background: #E31837 !important; border-radius: 10px !important; }

/* ── Metrics ── */
[data-testid="stMetric"] { background: #0D1728; border: 1px solid #1A2745; border-radius: 10px; padding: 0.8rem 1rem; }
[data-testid="stMetricLabel"]  { color: #475569 !important; font-size: 0.72rem !important; font-weight: 700 !important; text-transform: uppercase; letter-spacing: 0.06em; }
[data-testid="stMetricValue"]  { color: #F1F5F9 !important; font-weight: 800 !important; }

/* ── Expanders ── */
[data-testid="stExpander"] { background: #0D1728 !important; border: 1px solid #1A2745 !important; border-radius: 10px !important; }
[data-testid="stExpander"] summary { color: #CBD5E1 !important; }

/* ── Info/alert boxes ── */
[data-testid="stAlert"] { background: rgba(37,99,235,0.1) !important; border-color: #1E3A8A !important; color: #93C5FD !important; border-radius: 10px !important; }

/* ── Slider ── */
[data-testid="stSlider"] > div > div > div { background: #E31837 !important; }

/* ── Caption ── */
.stCaption { color: #334155 !important; }

/* ── Hide Streamlit chrome ── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
.stDeployButton { display: none; }
header    { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────
for k, v in [("trad_rag", None), ("graph_rag", None), ("query_history", []), ("pipelines_ready", False), ("last_result", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f"<div style='text-align:center;padding:1.2rem 0 0.5rem;'>{LOGO_SIDEBAR}"
        "<p style='color:#334155;font-size:0.72rem;margin:0.6rem 0 0;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;'>ESADE Capstone 2026</p></div>",
        unsafe_allow_html=True
    )
    st.markdown("---")

    status = check_config()
    st.markdown("<p style='color:#334155;font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.6rem;'>System Status</p>", unsafe_allow_html=True)
    for label, ok in [
        ("Groq API key", status["groq_key"]),
        (f"Corpus ({status['corpus_files']} files)", status["corpus_files"] > 0),
        ("Vector index (ChromaDB)", status["chroma_exists"]),
        ("Graph cache (Neo4j)", status["graph_cache_exists"])
    ]:
        icon, color = ("✓", "#10B981") if ok else ("✗", "#EF4444")
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:6px;'>"
            f"<span style='color:{color};font-weight:800;font-size:0.9rem;'>{icon}</span>"
            f"<span style='font-size:0.8rem;color:#64748B;'>{label}</span></div>",
            unsafe_allow_html=True
        )

    if not status["groq_key"]:
        st.error("Add GROQ_API_KEY to .env")
        st.stop()

    st.markdown("---")
    use_neo4j = st.toggle("Use Neo4j", value=True)

    if not st.session_state.pipelines_ready:
        if st.button("🚀 Initialize Pipelines", type="primary", use_container_width=True):
            with st.spinner("Loading pipelines…"):
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
        st.markdown(
            "<div style='background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);border-radius:8px;"
            "padding:0.5rem;text-align:center;'>"
            "<span style='color:#10B981;font-weight:700;font-size:0.82rem;'>● Pipelines ready</span></div>",
            unsafe_allow_html=True
        )
        if st.button("↺ Rebuild", use_container_width=True):
            st.session_state.pipelines_ready = False
            st.session_state.trad_rag = None
            st.session_state.graph_rag = None
            st.rerun()

    st.markdown("---")
    st.markdown("<p style='color:#334155;font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.6rem;'>Team</p>", unsafe_allow_html=True)
    for name in ["Mohamed Aymen Elmezouari", "Abhay Mathahalli", "Warren Liu"]:
        initials = "".join(w[0] for w in name.split()[:2])
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:6px;'>"
            f"<div style='width:26px;height:26px;border-radius:50%;background:#1A2745;display:flex;"
            f"align-items:center;justify-content:center;font-size:0.62rem;font-weight:800;color:#93C5FD;flex-shrink:0;'>{initials}</div>"
            f"<span style='font-size:0.78rem;color:#64748B;'>{name}</span></div>",
            unsafe_allow_html=True
        )

# ── Hero ──────────────────────────────────────────────────────
st.markdown(
    f"<div class='hero'>"
    f"  <div class='hero-text'>"
    f"    <h1>Traditional RAG vs. Graph RAG</h1>"
    f"    <p>Banking regulatory document retrieval &nbsp;·&nbsp; Banc Sabadell IT &amp; Operations &nbsp;·&nbsp; ESADE Capstone 2026</p>"
    f"  </div>"
    f"  <div class='hero-right'>"
    f"    {LOGO_HERO}"
    f"    <span class='hero-badge'>Mid-Term Prototype</span>"
    f"  </div>"
    f"</div>",
    unsafe_allow_html=True
)

tab_demo, tab_eval, tab_arch, tab_hist = st.tabs(["⚡  Live Demo", "📊  Evaluation", "🏗️  Architecture", "📋  History"])

# ══════════════════════════════════════════════════════════════
# TAB 1 — LIVE DEMO
# ══════════════════════════════════════════════════════════════
with tab_demo:
    if not st.session_state.pipelines_ready:
        st.markdown(
            "<div style='text-align:center;padding:4rem 2rem;background:#0D1728;border-radius:16px;border:1px solid #1A2745;'>"
            "<div style='font-size:3rem;margin-bottom:1rem;'>🚀</div>"
            "<h3 style='color:#F1F5F9;margin:0 0 0.5rem;'>Initialize the pipelines to get started</h3>"
            "<p style='color:#475569;margin:0;'>Click <strong style=\"color:#E31837;\">Initialize Pipelines</strong> in the sidebar — ~30 seconds on first run.</p>"
            "</div>",
            unsafe_allow_html=True
        )
    else:
        presets = [
            "— type your own —",
            "What is the minimum CET1 capital ratio under Basel III?",
            "What CDD obligations apply to Politically Exposed Persons under AML?",
            "Which products require both MiFID II suitability and AML enhanced due diligence?",
            "How should banks handle GDPR data breaches and what are notification deadlines?",
            "What is the maximum fine for violating Basel III capital requirements?",
        ]
        choice   = st.selectbox("Quick preset", presets, label_visibility="collapsed")
        default_q = "" if choice == "— type your own —" else choice
        query    = st.text_area(
            "Query",
            value=default_q,
            placeholder="Ask anything about banking regulations, compliance, or financial products…",
            height=90,
            label_visibility="collapsed"
        )

        c1, c2 = st.columns([4, 1])
        with c1:
            run = st.button("▶  Run Comparison", type="primary", disabled=not query.strip(), use_container_width=True)
        with c2:
            top_k = st.slider("k", 3, 10, 5, label_visibility="collapsed")
            st.caption(f"Top-k: {top_k}")

        if run and query.strip():
            prog = st.progress(0)
            msg  = st.empty()
            msg.markdown("*⚡ Traditional RAG — retrieving chunks…*")
            prog.progress(15)
            t_res = st.session_state.trad_rag.query(query, top_k=top_k)
            prog.progress(55)
            msg.markdown("*🔗 Graph RAG — traversing knowledge graph…*")
            g_res = st.session_state.graph_rag.query(query)
            prog.progress(100)
            time.sleep(0.3)
            prog.empty(); msg.empty()
            st.session_state.last_result = {"query": query, "trad": t_res, "graph": g_res}
            st.session_state.query_history.append({
                "query": query,
                "trad": t_res,
                "graph": g_res,
                "timestamp": time.strftime("%H:%M:%S")
            })

        if st.session_state.last_result:
            t  = st.session_state.last_result["trad"]
            g  = st.session_state.last_result["graph"]
            tl, gl = t["latency_total"], g["latency_total"]
            delta   = gl - tl
            dc      = "#10B981" if delta < 0 else "#EF4444"

            st.markdown(f"""<div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-label">Traditional latency</div>
                    <div class="stat-value" style="color:#93C5FD;">{tl:.2f}s</div>
                    <div class="stat-sub">vector cosine similarity</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Graph RAG latency</div>
                    <div class="stat-value" style="color:#6EE7B7;">{gl:.2f}s</div>
                    <div class="stat-sub" style="color:{dc};font-weight:700;">{delta:+.2f}s vs Traditional</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Chunks retrieved</div>
                    <div class="stat-value">{len(t.get('chunks', []))}</div>
                    <div class="stat-sub">top-{top_k} by similarity</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Graph nodes found</div>
                    <div class="stat-value">{g.get('entities_found', 0)}</div>
                    <div class="stat-sub">entity relationships traversed</div>
                </div>
            </div>""", unsafe_allow_html=True)

            st.markdown("<div class='section-hdr'>Pipeline Answers</div>", unsafe_allow_html=True)
            ca, cb = st.columns(2)

            with ca:
                chunks_html = ""
                for i, c in enumerate(t.get("chunks", [])[:3], 1):
                    sim = c.get("similarity_score", 0)
                    bw  = int(sim * 100)
                    chunks_html += (
                        f"<div class='chunk-card'>"
                        f"<div style='display:flex;justify-content:space-between;margin-bottom:4px;'>"
                        f"<span style='font-size:0.7rem;font-weight:700;color:#93C5FD;'>Chunk {i} — {c['source'][:30]}</span>"
                        f"<span style='font-size:0.7rem;color:#475569;'>{sim:.3f}</span></div>"
                        f"<div style='height:3px;background:#1A2745;border-radius:2px;margin-bottom:6px;'>"
                        f"<div style='height:100%;width:{bw}%;background:#2563EB;border-radius:2px;'></div></div>"
                        f"<p style='font-size:0.78rem;color:#64748B;margin:0;line-height:1.5;'>{c['text'][:200]}…</p>"
                        f"</div>"
                    )
                srcs = "".join(f'<span class="source-chip">📄 {s}</span>' for s in t["sources"][:4])
                st.markdown(
                    f"<div class='pipeline-card'>"
                    f"<div class='pipeline-header ph-trad'>"
                    f"<div><div class='pipeline-title pt-trad'>🔵 Traditional RAG</div>"
                    f"<div style='font-size:0.7rem;color:#334155;'>ChromaDB · all-MiniLM-L6-v2 · Top-{top_k} cosine</div></div>"
                    f"<span class='pipeline-badge pb-trad'>Vector-based</span></div>"
                    f"<div class='pipeline-body'>"
                    f"<p class='pipeline-answer'>{t['answer']}</p>"
                    f"<div style='margin-top:1rem;padding-top:1rem;border-top:1px solid #1A2745;'>"
                    f"<div style='font-size:0.7rem;font-weight:700;color:#334155;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px;'>Sources retrieved</div>{srcs}</div>"
                    f"<div style='margin-top:1rem;'>"
                    f"<div style='font-size:0.7rem;font-weight:700;color:#334155;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;'>Top chunks</div>{chunks_html}</div>"
                    f"</div></div>",
                    unsafe_allow_html=True
                )

            with cb:
                neo_label  = "Neo4j" if g.get("neo4j_used") else "In-memory graph"
                paths      = g.get("graph_paths", [])
                paths_html = (
                    "".join(f'<div class="graph-path-card">→ {p}</div>' for p in paths[:4])
                    if paths else
                    "<div style='color:#334155;font-size:0.82rem;font-style:italic;'>No graph paths found — entity matching refinement planned</div>"
                )
                srcs_g = "".join(f'<span class="source-chip">📄 {s}</span>' for s in g["sources"][:4])
                st.markdown(
                    f"<div class='pipeline-card'>"
                    f"<div class='pipeline-header ph-graph'>"
                    f"<div><div class='pipeline-title pt-graph'>🟢 Graph RAG</div>"
                    f"<div style='font-size:0.7rem;color:#334155;'>{neo_label} · Entity traversal · Relationship-aware</div></div>"
                    f"<span class='pipeline-badge pb-graph'>Knowledge graph</span></div>"
                    f"<div class='pipeline-body'>"
                    f"<p class='pipeline-answer'>{g['answer']}</p>"
                    f"<div style='margin-top:1rem;padding-top:1rem;border-top:1px solid #1A2745;'>"
                    f"<div style='font-size:0.7rem;font-weight:700;color:#334155;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px;'>Graph traversal paths</div>{paths_html}</div>"
                    f"<div style='margin-top:1rem;'>"
                    f"<div style='font-size:0.7rem;font-weight:700;color:#334155;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;'>Source documents</div>{srcs_g}</div>"
                    f"</div></div>",
                    unsafe_allow_html=True
                )

# ══════════════════════════════════════════════════════════════
# TAB 2 — EVALUATION
# ══════════════════════════════════════════════════════════════
with tab_eval:
    st.markdown("<div class='section-hdr'>Evaluation Dashboard</div>", unsafe_allow_html=True)

    _DARK_PLOT = dict(
        plot_bgcolor="#0D1728",
        paper_bgcolor="#0D1728",
        font=dict(family="Inter", size=13, color="#94A3B8"),
        margin=dict(t=50, b=20, l=20, r=20),
        xaxis=dict(showgrid=False, color="#334155", tickfont=dict(color="#64748B")),
        yaxis=dict(showgrid=True, gridcolor="#1A2745", tickfont=dict(color="#64748B")),
    )

    history = st.session_state.query_history
    if history:
        atl = sum(h["trad"]["latency_total"] for h in history) / len(history)
        agl = sum(h["graph"]["latency_total"] for h in history) / len(history)
        st.markdown(f"""<div class="stat-grid">
            <div class="stat-card">
                <div class="stat-label">Session queries</div>
                <div class="stat-value">{len(history)}</div>
                <div class="stat-sub">this session</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Traditional latency</div>
                <div class="stat-value" style="color:#93C5FD;">{atl:.2f}s</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Graph RAG latency</div>
                <div class="stat-value" style="color:#6EE7B7;">{agl:.2f}s</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Graph overhead</div>
                <div class="stat-value" style="color:{'#10B981' if agl < atl else '#EF4444'};">{agl - atl:+.2f}s</div>
            </div>
        </div>""", unsafe_allow_html=True)

    rf = EVAL_DIR / "results.json"
    if rf.exists():
        with open(rf) as f:
            ev = json.load(f)
        s  = ev["summary"]
        t, g = s["traditional_rag"], s["graph_rag"]

        ca, cb, cc = st.columns(3)
        ca.metric("Graph RAG wins",    f"{s['graph_wins_accuracy']}/{s['total_questions']}")
        cb.metric("Traditional wins",  f"{s['trad_wins_accuracy']}/{s['total_questions']}")
        cc.metric("Ties",              f"{s['ties_accuracy']}/{s['total_questions']}")

        metrics = ["Accuracy", "Faithfulness", "Source Citation", "Answer Quality"]
        tv      = [t["avg_accuracy"], t["avg_faithfulness"], t["avg_source_citation"], t["avg_answer_quality"]]
        gv      = [g["avg_accuracy"], g["avg_faithfulness"], g["avg_source_citation"], g["avg_answer_quality"]]

        fig = go.Figure(data=[
            go.Bar(name="Traditional RAG", x=metrics, y=tv,
                   marker_color="#2563EB", marker_line_color="rgba(0,0,0,0)",
                   text=[f"{v}%" for v in tv], textposition="outside",
                   textfont=dict(color="#93C5FD")),
            go.Bar(name="Graph RAG", x=metrics, y=gv,
                   marker_color="#059669", marker_line_color="rgba(0,0,0,0)",
                   text=[f"{v}%" for v in gv], textposition="outside",
                   textfont=dict(color="#6EE7B7")),
        ])
        fig.update_layout(
            barmode="group", yaxis_range=[0, 115],
            **_DARK_PLOT,
            legend=dict(orientation="h", yanchor="bottom", y=1.02,
                        font=dict(color="#94A3B8"), bgcolor="rgba(0,0,0,0)"),
            yaxis=dict(**_DARK_PLOT["yaxis"], ticksuffix="%"),
        )
        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            fig2 = go.Figure(go.Bar(
                x=["Traditional RAG", "Graph RAG"],
                y=[t["avg_hallucination_risk"], g["avg_hallucination_risk"]],
                marker_color=["#2563EB", "#059669"],
                marker_line_color="rgba(0,0,0,0)",
                text=[f"{t['avg_hallucination_risk']}%", f"{g['avg_hallucination_risk']}%"],
                textposition="outside",
                textfont=dict(color="#94A3B8")
            ))
            fig2.update_layout(
                title=dict(text="Hallucination risk % (lower = better)", font=dict(color="#64748B", size=12)),
                yaxis_range=[0, 100],
                **_DARK_PLOT,
                yaxis=dict(**_DARK_PLOT["yaxis"], ticksuffix="%"),
            )
            st.plotly_chart(fig2, use_container_width=True)
        with c2:
            fig3 = go.Figure(go.Bar(
                x=["Traditional RAG", "Graph RAG"],
                y=[t["avg_latency"], g["avg_latency"]],
                marker_color=["#2563EB", "#059669"],
                marker_line_color="rgba(0,0,0,0)",
                text=[f"{t['avg_latency']}s", f"{g['avg_latency']}s"],
                textposition="outside",
                textfont=dict(color="#94A3B8")
            ))
            fig3.update_layout(
                title=dict(text="Average latency in seconds (lower = better)", font=dict(color="#64748B", size=12)),
                **_DARK_PLOT,
            )
            st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No full evaluation yet. Run: `python3 evaluation/evaluator.py` in your terminal.")
        if st.session_state.pipelines_ready:
            if st.button("▶ Run Quick Evaluation (5 questions)", type="primary"):
                with st.spinner("Running… ~3 minutes"):
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
        st.markdown("""<div class="arch-box">
            <div style='font-weight:800;color:#93C5FD;font-size:0.95rem;margin-bottom:0.5rem;'>🔵 Traditional RAG Pipeline</div>
            <div class="arch-steps">
                <span class="arch-step s-input">PDF/TXT</span><span class="arr">→</span>
                <span class="arch-step s-trad">PyMuPDF</span><span class="arr">→</span>
                <span class="arch-step s-trad">Chunking 500 tok</span><span class="arr">→</span>
                <span class="arch-step s-trad">MiniLM embed</span><span class="arr">→</span>
                <span class="arch-step s-trad">ChromaDB</span><span class="arr">→</span>
                <span class="arch-step s-trad">Top-k cosine</span><span class="arr">→</span>
                <span class="arch-step s-out">Groq Llama 3.3</span>
            </div>
            <div class="insight"><strong>Strengths:</strong> Fast build, low latency, easy updates.<br>
            <strong>Weaknesses:</strong> Loses entity relationships, semantic noise.</div>
        </div>""", unsafe_allow_html=True)
    with cb:
        st.markdown("""<div class="arch-box">
            <div style='font-weight:800;color:#6EE7B7;font-size:0.95rem;margin-bottom:0.5rem;'>🟢 Graph RAG Pipeline</div>
            <div class="arch-steps">
                <span class="arch-step s-input">PDF/TXT</span><span class="arr">→</span>
                <span class="arch-step s-graph">spaCy NER</span><span class="arr">→</span>
                <span class="arch-step s-graph">Entity extract</span><span class="arr">→</span>
                <span class="arch-step s-graph">Neo4j graph</span><span class="arr">→</span>
                <span class="arch-step s-graph">Cypher query</span><span class="arr">→</span>
                <span class="arch-step s-graph">Subgraph ctx</span><span class="arr">→</span>
                <span class="arch-step s-out">Groq Llama 3.3</span>
            </div>
            <div class="insight-g"><strong>Strengths:</strong> Captures relationships, better multi-hop, explicit citations.<br>
            <strong>Weaknesses:</strong> Slower build, higher latency, harder maintenance.</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-hdr'>Technology Stack</div>", unsafe_allow_html=True)
    st.dataframe(
        pd.DataFrame({
            "Component":  ["LLM", "Embeddings", "Vector store", "Graph DB", "NLP/NER", "Evaluation", "Frontend"],
            "Technology": ["Llama 3.3-70B via Groq API", "all-MiniLM-L6-v2 (local)", "ChromaDB 0.4.x",
                           "Neo4j Community 5.x + APOC", "spaCy en_core_web_sm",
                           "LLM-as-judge + Ragas", "Streamlit + Plotly"],
            "Role":       ["Generation (both pipelines)", "Document & query embedding",
                           "Vector similarity search", "Knowledge graph storage",
                           "Entity & relationship extraction", "Accuracy, hallucination, faithfulness",
                           "Interactive demo"],
        }),
        use_container_width=True, hide_index=True
    )

    st.markdown("<div class='section-hdr'>Corpus (9 files, ~750 pages)</div>", unsafe_allow_html=True)
    st.dataframe(
        pd.DataFrame({
            "Document": ["Basel III BIS Framework", "MiFID II Directive 2014/65/EU",
                         "GDPR Regulation 2016/679/EU", "Sabadell Pillar III 2025",
                         "Sabadell Annual Report 2025", "EBA AML Sample (txt)",
                         "Basel III Sample (txt)", "GDPR Banking Sample (txt)", "MiFID II Sample (txt)"],
            "Size":   ["1.2 MB", "1.8 MB", "959 KB", "33 MB", "38 MB", "2.4 KB", "2.7 KB", "3.1 KB", "2.9 KB"],
            "Status": ["✅"] * 9,
        }),
        use_container_width=True, hide_index=True
    )

# ══════════════════════════════════════════════════════════════
# TAB 4 — HISTORY
# ══════════════════════════════════════════════════════════════
with tab_hist:
    st.markdown("<div class='section-hdr'>Query History</div>", unsafe_allow_html=True)
    if not st.session_state.query_history:
        st.markdown(
            "<div style='text-align:center;padding:3rem 2rem;background:#0D1728;border-radius:16px;border:1px solid #1A2745;'>"
            "<div style='font-size:2.5rem;margin-bottom:0.75rem;'>📋</div>"
            "<p style='color:#475569;margin:0;'>No queries yet. Run a comparison in the Live Demo tab.</p></div>",
            unsafe_allow_html=True
        )
    else:
        c1, c2 = st.columns([4, 1])
        c1.caption(f"{len(st.session_state.query_history)} queries this session")
        with c2:
            if st.button("🗑 Clear"):
                st.session_state.query_history = []
                st.session_state.last_result   = None
                st.rerun()
        for item in reversed(st.session_state.query_history):
            tl, gl  = item["trad"]["latency_total"], item["graph"]["latency_total"]
            faster  = "Graph RAG" if gl < tl else "Traditional RAG"
            fc      = "#6EE7B7" if gl < tl else "#93C5FD"
            with st.expander(f"[{item['timestamp']}]  {item['query'][:80]}"):
                ca, cb = st.columns(2)
                with ca:
                    st.markdown(
                        f"<div style='font-weight:800;color:#93C5FD;margin-bottom:6px;'>"
                        f"🔵 Traditional RAG <span style='font-size:0.75rem;font-weight:400;color:#334155;'>({tl:.2f}s)</span></div>",
                        unsafe_allow_html=True
                    )
                    st.write(item["trad"]["answer"])
                    if item["trad"]["sources"]:
                        st.markdown("**Sources:** " + " · ".join(item["trad"]["sources"][:3]))
                with cb:
                    st.markdown(
                        f"<div style='font-weight:800;color:#6EE7B7;margin-bottom:6px;'>"
                        f"🟢 Graph RAG <span style='font-size:0.75rem;font-weight:400;color:#334155;'>({gl:.2f}s)</span></div>",
                        unsafe_allow_html=True
                    )
                    st.write(item["graph"]["answer"])
                    if item["graph"].get("graph_paths"):
                        for p in item["graph"]["graph_paths"][:2]:
                            st.markdown(f"<div class='graph-path-card'>→ {p}</div>", unsafe_allow_html=True)
                st.markdown(
                    f"<div style='margin-top:10px;padding-top:10px;border-top:1px solid #1A2745;"
                    f"font-size:0.8rem;color:{fc};font-weight:700;'>⚡ Faster pipeline: {faster}</div>",
                    unsafe_allow_html=True
                )
