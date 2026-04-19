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
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%23E31837'/><text x='5' y='20' font-family='Georgia' font-size='14' font-weight='900' fill='white'>B</text><text x='5' y='30' font-family='Georgia' font-size='14' font-weight='900' fill='white'>S</text></svg>",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Banc Sabadell SVG logos ────────────────────────────────────
LOGO_SIDEBAR = """
<svg width="156" height="50" viewBox="0 0 156 50" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="42" height="42" x="0" y="4" rx="9" fill="#E31837"/>
  <text x="8" y="21" font-family="Georgia,serif" font-size="15" font-weight="900" fill="white">B</text>
  <text x="8" y="38" font-family="Georgia,serif" font-size="15" font-weight="900" fill="white">S</text>
  <text x="50" y="23" font-family="Inter,Arial,sans-serif" font-size="13" font-weight="700" fill="#F1F5F9" letter-spacing="0.3">Banc</text>
  <text x="50" y="39" font-family="Inter,Arial,sans-serif" font-size="13" font-weight="700" fill="#F1F5F9" letter-spacing="0.3">Sabadell</text>
  <rect x="50" y="43" width="68" height="2" rx="1" fill="#E31837"/>
</svg>
"""

LOGO_HERO = """
<svg width="148" height="50" viewBox="0 0 148 50" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="42" height="42" x="0" y="4" rx="9" fill="#E31837"/>
  <text x="8" y="21" font-family="Georgia,serif" font-size="15" font-weight="900" fill="white">B</text>
  <text x="8" y="38" font-family="Georgia,serif" font-size="15" font-weight="900" fill="white">S</text>
  <text x="50" y="23" font-family="Inter,Arial,sans-serif" font-size="13" font-weight="700" fill="white" letter-spacing="0.3">Banc</text>
  <text x="50" y="39" font-family="Inter,Arial,sans-serif" font-size="13" font-weight="700" fill="white" letter-spacing="0.3">Sabadell</text>
  <rect x="50" y="43" width="68" height="2" rx="1" fill="#E31837"/>
</svg>
"""

# ── SVG micro-icons (no emoji) ─────────────────────────────────
ICON_VECTOR = '<svg width="14" height="14" viewBox="0 0 14 14" fill="none" style="display:inline;vertical-align:middle;margin-right:6px;"><circle cx="7" cy="7" r="6" fill="#2563EB" opacity="0.25"/><circle cx="7" cy="7" r="3.5" fill="#3B82F6"/></svg>'
ICON_GRAPH  = '<svg width="14" height="14" viewBox="0 0 14 14" fill="none" style="display:inline;vertical-align:middle;margin-right:6px;"><circle cx="7" cy="7" r="6" fill="#059669" opacity="0.25"/><circle cx="7" cy="7" r="3.5" fill="#10B981"/></svg>'

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
*, html, body, [class*="css"] { font-family: 'Inter', sans-serif; box-sizing: border-box; }

/* ── Top accent bar ── */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #E31837 0%, #FF6B6B 50%, #E31837 100%);
    z-index: 9999;
}

/* ── Base ── */
.stApp { background: #070D1A !important; }
[data-testid="stAppViewContainer"] { background: #070D1A !important; }
[data-testid="stMain"] { background: #070D1A !important; }
.main .block-container { background: transparent !important; padding-top: 1.25rem !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #040810 !important;
    border-right: 1px solid #111D35 !important;
}
section[data-testid="stSidebar"] * { color: #64748B !important; }
section[data-testid="stSidebar"] hr { border-color: #111D35 !important; opacity: 1 !important; }
section[data-testid="stSidebar"] [data-testid="stToggle"] { filter: hue-rotate(200deg); }

section[data-testid="stSidebar"] .stButton button {
    background: #E31837 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    width: 100% !important;
    padding: 0.65rem 1rem !important;
    letter-spacing: 0.03em !important;
    font-size: 0.85rem !important;
    transition: all 0.15s ease !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: #C01230 !important;
    box-shadow: 0 4px 14px rgba(227,24,55,0.4) !important;
    transform: translateY(-1px) !important;
}

/* ── Hero ── */
.hero {
    background: #0A0F1E;
    background-image:
        radial-gradient(ellipse at 70% 50%, rgba(227,24,55,0.07) 0%, transparent 60%),
        radial-gradient(ellipse at 10% 50%, rgba(37,99,235,0.06) 0%, transparent 50%);
    border: 1px solid #131F3A;
    border-radius: 18px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 8px 40px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.04);
}
.hero-text h1 {
    color: #F8FAFC;
    font-size: 1.7rem;
    font-weight: 900;
    margin: 0;
    letter-spacing: -0.03em;
    line-height: 1.15;
}
.hero-text p {
    color: #475569;
    margin: 0.4rem 0 0;
    font-size: 0.83rem;
    letter-spacing: 0.01em;
}
.hero-right { display: flex; flex-direction: column; align-items: flex-end; gap: 0.65rem; }
.hero-badge {
    background: rgba(227,24,55,0.12);
    border: 1px solid rgba(227,24,55,0.35);
    border-radius: 20px;
    padding: 0.3rem 0.9rem;
    color: #F87171 !important;
    font-size: 0.7rem;
    font-weight: 800;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* ── Stat cards ── */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.stat-card {
    background: #0C1526;
    border: 1px solid #131F3A;
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.35);
    transition: border-color 0.2s ease, transform 0.2s ease;
}
.stat-card:hover { border-color: #1E3A6E; transform: translateY(-2px); }
.stat-label {
    font-size: 0.68rem;
    color: #334155;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.45rem;
}
.stat-value { font-size: 2rem; font-weight: 900; color: #F1F5F9; line-height: 1; }
.stat-sub   { font-size: 0.68rem; color: #1E3251; margin-top: 0.3rem; font-weight: 500; }

/* ── Pipeline cards ── */
.pipeline-card {
    background: #0C1526;
    border: 1px solid #131F3A;
    border-radius: 18px;
    overflow: hidden;
    margin-bottom: 1rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    transition: border-color 0.2s ease;
}
.pipeline-card:hover { border-color: #1E3A6E; }
.pipeline-header { padding: 1.1rem 1.6rem; display: flex; align-items: center; justify-content: space-between; }
.ph-trad  { background: linear-gradient(105deg, #0A1530 0%, #0D2060 100%); border-bottom: 1px solid rgba(37,99,235,0.3); }
.ph-graph { background: linear-gradient(105deg, #091A12 0%, #0C2B1A 100%); border-bottom: 1px solid rgba(5,150,105,0.3); }
.pipeline-title { font-weight: 800; font-size: 0.95rem; letter-spacing: -0.01em; display: flex; align-items: center; }
.pt-trad  { color: #93C5FD; }
.pt-graph { color: #6EE7B7; }
.pipeline-badge {
    font-size: 0.65rem;
    padding: 0.22rem 0.75rem;
    border-radius: 20px;
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.pb-trad  { background: rgba(37,99,235,0.15); color: #93C5FD; border: 1px solid rgba(37,99,235,0.25); }
.pb-graph { background: rgba(5,150,105,0.15); color: #6EE7B7;  border: 1px solid rgba(5,150,105,0.25); }
.pipeline-body   { padding: 1.6rem; }
.pipeline-answer { font-size: 0.88rem; line-height: 1.9; color: #CBD5E1; }
.source-chip {
    display: inline-block;
    background: rgba(255,255,255,0.04);
    border: 1px solid #1A2B4A;
    border-radius: 6px;
    padding: 0.18rem 0.6rem;
    font-size: 0.68rem;
    color: #475569;
    margin: 0.2rem 0.2rem 0 0;
    font-weight: 500;
    letter-spacing: 0.02em;
}
.graph-path-card {
    background: rgba(5,150,105,0.06);
    border: 1px solid rgba(5,150,105,0.2);
    border-radius: 8px;
    padding: 0.55rem 0.85rem;
    font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', monospace;
    font-size: 0.74rem;
    color: #34D399;
    margin-top: 0.4rem;
    letter-spacing: 0.01em;
}
.chunk-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid #111D35;
    border-radius: 8px;
    padding: 0.8rem;
    margin-top: 0.5rem;
    transition: border-color 0.15s ease;
}
.chunk-card:hover { border-color: #1E3A6E; }

/* ── Section headers ── */
.section-hdr {
    font-size: 0.82rem;
    font-weight: 800;
    color: #94A3B8;
    margin: 1.75rem 0 1rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.section-hdr::before {
    content: '';
    display: block;
    width: 3px;
    height: 16px;
    background: #E31837;
    border-radius: 2px;
    flex-shrink: 0;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: #0C1526;
    border-radius: 12px;
    padding: 0.3rem;
    border: 1px solid #131F3A;
    margin-bottom: 1.5rem;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 0.5rem 1.4rem;
    font-weight: 600;
    font-size: 0.82rem;
    color: #334155 !important;
    background: transparent !important;
    letter-spacing: 0.03em;
    transition: color 0.15s ease;
}
.stTabs [data-baseweb="tab"]:hover { color: #64748B !important; }
.stTabs [aria-selected="true"] {
    background: #E31837 !important;
    color: white !important;
    box-shadow: 0 2px 10px rgba(227,24,55,0.35) !important;
}

/* ── Architecture boxes ── */
.arch-box {
    background: #0C1526;
    border: 1px solid #131F3A;
    border-radius: 14px;
    padding: 1.6rem;
    margin-bottom: 1rem;
}
.arch-label { font-weight: 800; font-size: 0.9rem; margin-bottom: 0.6rem; display: flex; align-items: center; gap: 8px; }
.arch-steps { display: flex; align-items: center; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.6rem; }
.arch-step  { padding: 0.3rem 0.75rem; border-radius: 6px; font-size: 0.74rem; font-weight: 700; letter-spacing: 0.02em; }
.s-input { background: rgba(100,116,139,0.15); color: #64748B; border: 1px solid rgba(100,116,139,0.2); }
.s-trad  { background: rgba(37,99,235,0.12);  color: #93C5FD; border: 1px solid rgba(37,99,235,0.2); }
.s-graph { background: rgba(5,150,105,0.12);  color: #6EE7B7; border: 1px solid rgba(5,150,105,0.2); }
.s-out   { background: rgba(245,158,11,0.12); color: #FCD34D; border: 1px solid rgba(245,158,11,0.2); }
.arr     { color: #1E3251; font-size: 0.9rem; font-weight: 600; }
.insight {
    background: rgba(37,99,235,0.06);
    border-left: 3px solid rgba(37,99,235,0.5);
    border-radius: 0 8px 8px 0;
    padding: 0.8rem 1rem;
    margin-top: 1rem;
    font-size: 0.8rem;
    color: #7DB4F7;
    line-height: 1.6;
}
.insight-g {
    background: rgba(5,150,105,0.06);
    border-left: 3px solid rgba(5,150,105,0.5);
    border-radius: 0 8px 8px 0;
    padding: 0.8rem 1rem;
    margin-top: 1rem;
    font-size: 0.8rem;
    color: #5DD4A8;
    line-height: 1.6;
}

/* ── Empty state placeholder ── */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    background: #0C1526;
    border-radius: 18px;
    border: 1px solid #131F3A;
}
.empty-state-icon {
    width: 56px;
    height: 56px;
    border-radius: 14px;
    background: rgba(227,24,55,0.1);
    border: 1px solid rgba(227,24,55,0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 1.25rem;
}
.empty-state h3 { color: #E2E8F0; font-weight: 800; margin: 0 0 0.5rem; font-size: 1.1rem; letter-spacing: -0.01em; }
.empty-state p  { color: #334155; margin: 0; font-size: 0.875rem; line-height: 1.6; }

/* ── Dataframes ── */
[data-testid="stDataFrame"] { background: #0C1526 !important; border-radius: 12px; overflow: hidden; border: 1px solid #131F3A !important; }
[data-testid="stDataFrame"] th { background: #070D1A !important; color: #475569 !important; font-weight: 800 !important; font-size: 0.72rem !important; text-transform: uppercase !important; letter-spacing: 0.07em !important; border-bottom: 1px solid #131F3A !important; }
[data-testid="stDataFrame"] td { background: #0C1526 !important; color: #94A3B8 !important; font-size: 0.84rem !important; border-bottom: 1px solid #0F1A2E !important; }
[data-testid="stDataFrame"] tr:hover td { background: #111D35 !important; }

/* ── Inputs ── */
.stTextArea textarea {
    background: #0C1526 !important;
    border: 1.5px solid #131F3A !important;
    color: #F1F5F9 !important;
    border-radius: 10px !important;
    font-size: 0.9rem !important;
    line-height: 1.7 !important;
    transition: border-color 0.15s ease !important;
}
.stTextArea textarea:focus { border-color: #E31837 !important; box-shadow: 0 0 0 3px rgba(227,24,55,0.1) !important; }
.stTextArea textarea::placeholder { color: #1E3251 !important; }
.stSelectbox > div > div { background: #0C1526 !important; border-color: #131F3A !important; color: #F1F5F9 !important; border-radius: 8px !important; }

/* ── Buttons ── */
.stButton > button[kind="primary"] {
    background: #E31837 !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 800 !important;
    padding: 0.65rem 2rem !important;
    box-shadow: 0 4px 16px rgba(227,24,55,0.3) !important;
    letter-spacing: 0.04em !important;
    font-size: 0.85rem !important;
    text-transform: uppercase !important;
    transition: all 0.15s ease !important;
}
.stButton > button[kind="primary"]:hover {
    background: #C01230 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(227,24,55,0.45) !important;
}
.stButton > button:not([kind="primary"]) {
    background: transparent !important;
    border: 1px solid #131F3A !important;
    color: #475569 !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    transition: all 0.15s ease !important;
}
.stButton > button:not([kind="primary"]):hover {
    border-color: #1E3A6E !important;
    color: #94A3B8 !important;
    background: rgba(255,255,255,0.03) !important;
}

/* ── Progress bar ── */
div[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #E31837, #FF5252) !important;
    border-radius: 10px !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: #0C1526 !important;
    border: 1px solid #131F3A !important;
    border-radius: 12px;
    padding: 1rem 1.25rem;
}
[data-testid="stMetricLabel"] { color: #334155 !important; font-size: 0.7rem !important; font-weight: 800 !important; text-transform: uppercase; letter-spacing: 0.08em; }
[data-testid="stMetricValue"] { color: #F1F5F9 !important; font-weight: 900 !important; }

/* ── Expanders ── */
[data-testid="stExpander"] {
    background: #0C1526 !important;
    border: 1px solid #131F3A !important;
    border-radius: 12px !important;
    overflow: hidden;
}
[data-testid="stExpander"] summary {
    color: #64748B !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    padding: 0.8rem 1rem !important;
}
[data-testid="stExpander"] summary:hover { color: #94A3B8 !important; background: rgba(255,255,255,0.02) !important; }

/* ── Alert/info ── */
[data-testid="stAlert"] {
    background: rgba(37,99,235,0.07) !important;
    border: 1px solid rgba(37,99,235,0.2) !important;
    color: #7DB4F7 !important;
    border-radius: 10px !important;
}
[data-testid="stAlert"] code { color: #93C5FD !important; }

/* ── Slider ── */
[data-testid="stSlider"] > div > div > div { background: #E31837 !important; }

/* ── Caption ── */
.stCaption, [data-testid="stCaptionContainer"] { color: #1E3251 !important; }

/* ── Spinner ── */
[data-testid="stSpinner"] { color: #E31837 !important; }

/* ── Fade-in animation ── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
.stat-grid, .pipeline-card, .arch-box, .section-hdr {
    animation: fadeUp 0.3s ease forwards;
}

/* ── Hide Streamlit chrome ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.stDeployButton { display: none; }
header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────
for k, v in [("trad_rag", None), ("graph_rag", None), ("query_history", []), ("pipelines_ready", False), ("last_result", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f"<div style='padding:1.25rem 0 0.5rem;'>{LOGO_SIDEBAR}"
        "<p style='color:#1A2B4A;font-size:0.68rem;margin:0.65rem 0 0;font-weight:700;"
        "text-transform:uppercase;letter-spacing:0.12em;'>ESADE Capstone 2026</p></div>",
        unsafe_allow_html=True
    )
    st.markdown("---")

    status = check_config()
    st.markdown(
        "<p style='color:#1A2B4A;font-size:0.68rem;font-weight:800;text-transform:uppercase;"
        "letter-spacing:0.12em;margin-bottom:0.75rem;'>System Status</p>",
        unsafe_allow_html=True
    )
    for label, ok in [
        ("Groq API key",                          status["groq_key"]),
        (f"Corpus ({status['corpus_files']} files)", status["corpus_files"] > 0),
        ("Vector index  ·  ChromaDB",             status["chroma_exists"]),
        ("Graph cache  ·  Neo4j",                 status["graph_cache_exists"]),
    ]:
        dot_color = "#10B981" if ok else "#EF4444"
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:7px;'>"
            f"<span style='width:7px;height:7px;border-radius:50%;background:{dot_color};"
            f"display:inline-block;flex-shrink:0;box-shadow:0 0 6px {dot_color}55;'></span>"
            f"<span style='font-size:0.78rem;color:#334155;'>{label}</span></div>",
            unsafe_allow_html=True
        )

    if not status["groq_key"]:
        st.error("GROQ_API_KEY missing — add it to your .env file.")
        st.stop()

    st.markdown("---")
    use_neo4j = st.toggle("Use Neo4j", value=True)

    if not st.session_state.pipelines_ready:
        if st.button("Initialize Pipelines", type="primary", use_container_width=True):
            with st.spinner("Building indexes…"):
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
            "<div style='background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.25);"
            "border-radius:8px;padding:0.55rem;text-align:center;'>"
            "<span style='display:inline-block;width:7px;height:7px;border-radius:50%;"
            "background:#10B981;margin-right:6px;box-shadow:0 0 6px #10B98155;vertical-align:middle;'></span>"
            "<span style='color:#10B981;font-weight:700;font-size:0.82rem;letter-spacing:0.03em;'>Pipelines ready</span></div>",
            unsafe_allow_html=True
        )
        if st.button("Rebuild", use_container_width=True):
            st.session_state.pipelines_ready = False
            st.session_state.trad_rag = None
            st.session_state.graph_rag = None
            st.rerun()

    st.markdown("---")
    st.markdown(
        "<p style='color:#1A2B4A;font-size:0.68rem;font-weight:800;text-transform:uppercase;"
        "letter-spacing:0.12em;margin-bottom:0.75rem;'>Research Team</p>",
        unsafe_allow_html=True
    )
    for name in ["Mohamed Aymen Elmezouari", "Abhay Mathahalli", "Warren Liu"]:
        initials = "".join(w[0] for w in name.split()[:2])
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:9px;margin-bottom:8px;'>"
            f"<div style='width:28px;height:28px;border-radius:8px;background:#0C1526;"
            f"border:1px solid #131F3A;display:flex;align-items:center;justify-content:center;"
            f"font-size:0.6rem;font-weight:900;color:#93C5FD;flex-shrink:0;letter-spacing:0.02em;'>{initials}</div>"
            f"<span style='font-size:0.78rem;color:#334155;'>{name}</span></div>",
            unsafe_allow_html=True
        )

# ── Hero ──────────────────────────────────────────────────────
st.markdown(
    f"<div class='hero'>"
    f"  <div class='hero-text'>"
    f"    <h1>Traditional RAG vs. Graph RAG</h1>"
    f"    <p>Banking regulatory document retrieval &nbsp;&middot;&nbsp; Banc Sabadell IT &amp; Operations &nbsp;&middot;&nbsp; ESADE Capstone 2026</p>"
    f"  </div>"
    f"  <div class='hero-right'>"
    f"    {LOGO_HERO}"
    f"    <span class='hero-badge'>Mid-Term Prototype</span>"
    f"  </div>"
    f"</div>",
    unsafe_allow_html=True
)

tab_demo, tab_eval, tab_arch, tab_hist = st.tabs(
    ["Live Demo", "Evaluation", "Architecture", "Query History"]
)

# ══════════════════════════════════════════════════════════════
# TAB 1 — LIVE DEMO
# ══════════════════════════════════════════════════════════════
with tab_demo:
    if not st.session_state.pipelines_ready:
        st.markdown(
            "<div class='empty-state'>"
            "<div class='empty-state-icon'>"
            "<svg width='24' height='24' viewBox='0 0 24 24' fill='none'>"
            "<path d='M12 2L2 7l10 5 10-5-10-5z' stroke='#E31837' stroke-width='1.5' stroke-linejoin='round'/>"
            "<path d='M2 17l10 5 10-5' stroke='#E31837' stroke-width='1.5' stroke-linejoin='round'/>"
            "<path d='M2 12l10 5 10-5' stroke='#E31837' stroke-width='1.5' stroke-linejoin='round'/>"
            "</svg>"
            "</div>"
            "<h3>Pipelines not initialised</h3>"
            "<p>Click <strong style='color:#E31837;font-weight:700;'>Initialize Pipelines</strong> "
            "in the sidebar to build the vector index and knowledge graph.<br>"
            "First run takes approximately 30 seconds.</p>"
            "</div>",
            unsafe_allow_html=True
        )
    else:
        presets = [
            "— select a preset query or type your own —",
            "What is the minimum CET1 capital ratio under Basel III?",
            "What CDD obligations apply to Politically Exposed Persons under AML?",
            "Which products require both MiFID II suitability and AML enhanced due diligence?",
            "How should banks handle GDPR data breaches and what are notification deadlines?",
            "What is the maximum fine for violating Basel III capital requirements?",
        ]
        choice    = st.selectbox("Preset queries", presets, label_visibility="collapsed")
        default_q = "" if choice.startswith("—") else choice
        query     = st.text_area(
            "Query",
            value=default_q,
            placeholder="Ask a question about banking regulations, compliance, capital requirements, or product obligations…",
            height=88,
            label_visibility="collapsed"
        )

        c1, c2 = st.columns([5, 1])
        with c1:
            run = st.button(
                "Run Comparison",
                type="primary",
                disabled=not query.strip(),
                use_container_width=True
            )
        with c2:
            top_k = st.slider("k", 3, 10, 5, label_visibility="collapsed")
            st.caption(f"Top-k: {top_k}")

        if run and query.strip():
            prog = st.progress(0)
            msg  = st.empty()
            msg.markdown(
                "<p style='color:#475569;font-size:0.83rem;margin:0;'>"
                "Traditional RAG — retrieving document chunks…</p>",
                unsafe_allow_html=True
            )
            prog.progress(15)
            t_res = st.session_state.trad_rag.query(query, top_k=top_k)
            prog.progress(55)
            msg.markdown(
                "<p style='color:#475569;font-size:0.83rem;margin:0;'>"
                "Graph RAG — traversing knowledge graph…</p>",
                unsafe_allow_html=True
            )
            g_res = st.session_state.graph_rag.query(query)
            prog.progress(100)
            time.sleep(0.25)
            prog.empty()
            msg.empty()
            st.session_state.last_result = {"query": query, "trad": t_res, "graph": g_res}
            st.session_state.query_history.append({
                "query": query,
                "trad":  t_res,
                "graph": g_res,
                "timestamp": time.strftime("%H:%M:%S"),
            })

        if st.session_state.last_result:
            t  = st.session_state.last_result["trad"]
            g  = st.session_state.last_result["graph"]
            tl, gl = t["latency_total"], g["latency_total"]
            delta   = gl - tl
            dc      = "#10B981" if delta < 0 else "#EF4444"

            st.markdown(f"""<div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-label">Traditional Latency</div>
                    <div class="stat-value" style="color:#93C5FD;">{tl:.2f}s</div>
                    <div class="stat-sub">Vector cosine similarity</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Graph RAG Latency</div>
                    <div class="stat-value" style="color:#6EE7B7;">{gl:.2f}s</div>
                    <div class="stat-sub" style="color:{dc};font-weight:700;">{delta:+.2f}s vs Traditional</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Chunks Retrieved</div>
                    <div class="stat-value">{len(t.get('chunks', []))}</div>
                    <div class="stat-sub">Top-{top_k} by similarity</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Graph Nodes Found</div>
                    <div class="stat-value">{g.get('entities_found', 0)}</div>
                    <div class="stat-sub">Entity relationships traversed</div>
                </div>
            </div>""", unsafe_allow_html=True)

            st.markdown("<div class='section-hdr'>Pipeline Answers</div>", unsafe_allow_html=True)
            ca, cb = st.columns(2)

            with ca:
                chunks_html = ""
                for i, chunk in enumerate(t.get("chunks", [])[:3], 1):
                    sim = chunk.get("similarity_score", 0)
                    bw  = int(sim * 100)
                    chunks_html += (
                        f"<div class='chunk-card'>"
                        f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;'>"
                        f"<span style='font-size:0.68rem;font-weight:800;color:#93C5FD;text-transform:uppercase;"
                        f"letter-spacing:0.06em;'>Chunk {i} &middot; {chunk['source'][:28]}</span>"
                        f"<span style='font-size:0.72rem;color:#334155;font-weight:600;font-variant-numeric:tabular-nums;'>{sim:.3f}</span></div>"
                        f"<div style='height:2px;background:#111D35;border-radius:2px;margin-bottom:8px;'>"
                        f"<div style='height:100%;width:{bw}%;background:linear-gradient(90deg,#2563EB,#60A5FA);"
                        f"border-radius:2px;'></div></div>"
                        f"<p style='font-size:0.77rem;color:#475569;margin:0;line-height:1.55;'>"
                        f"{chunk['text'][:220]}…</p>"
                        f"</div>"
                    )
                srcs = "".join(
                    f'<span class="source-chip">{s}</span>' for s in t["sources"][:4]
                )
                st.markdown(
                    f"<div class='pipeline-card'>"
                    f"<div class='pipeline-header ph-trad'>"
                    f"<div><div class='pipeline-title pt-trad'>{ICON_VECTOR}Traditional RAG</div>"
                    f"<div style='font-size:0.68rem;color:#1E3A6E;margin-top:3px;'>"
                    f"ChromaDB &middot; all-MiniLM-L6-v2 &middot; Top-{top_k} cosine</div></div>"
                    f"<span class='pipeline-badge pb-trad'>Vector-Based</span></div>"
                    f"<div class='pipeline-body'>"
                    f"<p class='pipeline-answer'>{t['answer']}</p>"
                    f"<div style='margin-top:1.1rem;padding-top:1.1rem;border-top:1px solid #111D35;'>"
                    f"<div style='font-size:0.68rem;font-weight:800;color:#1E3251;text-transform:uppercase;"
                    f"letter-spacing:0.08em;margin-bottom:7px;'>Sources Retrieved</div>{srcs}</div>"
                    f"<div style='margin-top:1.1rem;'>"
                    f"<div style='font-size:0.68rem;font-weight:800;color:#1E3251;text-transform:uppercase;"
                    f"letter-spacing:0.08em;margin-bottom:6px;'>Top Chunks</div>{chunks_html}</div>"
                    f"</div></div>",
                    unsafe_allow_html=True
                )

            with cb:
                neo_label  = "Neo4j" if g.get("neo4j_used") else "In-memory graph"
                paths      = g.get("graph_paths", [])
                paths_html = (
                    "".join(
                        f'<div class="graph-path-card">&rarr; {p}</div>' for p in paths[:4]
                    )
                    if paths else
                    "<div style='color:#1E3251;font-size:0.8rem;font-style:italic;padding:0.5rem 0;'>"
                    "No traversal paths matched — entity resolution refinement in progress.</div>"
                )
                srcs_g = "".join(
                    f'<span class="source-chip">{s}</span>' for s in g["sources"][:4]
                )
                st.markdown(
                    f"<div class='pipeline-card'>"
                    f"<div class='pipeline-header ph-graph'>"
                    f"<div><div class='pipeline-title pt-graph'>{ICON_GRAPH}Graph RAG</div>"
                    f"<div style='font-size:0.68rem;color:#0F3321;margin-top:3px;'>"
                    f"{neo_label} &middot; Entity traversal &middot; Relationship-aware</div></div>"
                    f"<span class='pipeline-badge pb-graph'>Knowledge Graph</span></div>"
                    f"<div class='pipeline-body'>"
                    f"<p class='pipeline-answer'>{g['answer']}</p>"
                    f"<div style='margin-top:1.1rem;padding-top:1.1rem;border-top:1px solid #111D35;'>"
                    f"<div style='font-size:0.68rem;font-weight:800;color:#1E3251;text-transform:uppercase;"
                    f"letter-spacing:0.08em;margin-bottom:7px;'>Graph Traversal Paths</div>{paths_html}</div>"
                    f"<div style='margin-top:1.1rem;'>"
                    f"<div style='font-size:0.68rem;font-weight:800;color:#1E3251;text-transform:uppercase;"
                    f"letter-spacing:0.08em;margin-bottom:6px;'>Source Documents</div>{srcs_g}</div>"
                    f"</div></div>",
                    unsafe_allow_html=True
                )

# ══════════════════════════════════════════════════════════════
# TAB 2 — EVALUATION
# ══════════════════════════════════════════════════════════════
with tab_eval:
    st.markdown("<div class='section-hdr'>Evaluation Dashboard</div>", unsafe_allow_html=True)

    _DARK_PLOT = dict(
        plot_bgcolor="#0C1526",
        paper_bgcolor="#0C1526",
        font=dict(family="Inter", size=12, color="#64748B"),
        margin=dict(t=55, b=25, l=25, r=25),
        xaxis=dict(showgrid=False, tickfont=dict(color="#475569"), linecolor="#131F3A"),
        yaxis=dict(showgrid=True, gridcolor="#111D35", tickfont=dict(color="#475569"), linecolor="#131F3A"),
    )

    history = st.session_state.query_history
    if history:
        atl = sum(h["trad"]["latency_total"] for h in history) / len(history)
        agl = sum(h["graph"]["latency_total"] for h in history) / len(history)
        st.markdown(f"""<div class="stat-grid">
            <div class="stat-card">
                <div class="stat-label">Session Queries</div>
                <div class="stat-value">{len(history)}</div>
                <div class="stat-sub">This session</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Traditional Latency</div>
                <div class="stat-value" style="color:#93C5FD;">{atl:.2f}s</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Graph RAG Latency</div>
                <div class="stat-value" style="color:#6EE7B7;">{agl:.2f}s</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Graph Overhead</div>
                <div class="stat-value" style="color:{'#10B981' if agl < atl else '#EF4444'};">{agl - atl:+.2f}s</div>
            </div>
        </div>""", unsafe_allow_html=True)

    rf = EVAL_DIR / "results.json"
    if rf.exists():
        with open(rf) as f:
            ev = json.load(f)
        s    = ev["summary"]
        t, g = s["traditional_rag"], s["graph_rag"]

        ca, cb, cc = st.columns(3)
        ca.metric("Graph RAG Wins",    f"{s['graph_wins_accuracy']} / {s['total_questions']}")
        cb.metric("Traditional Wins",  f"{s['trad_wins_accuracy']} / {s['total_questions']}")
        cc.metric("Ties",              f"{s['ties_accuracy']} / {s['total_questions']}")

        metrics = ["Accuracy", "Faithfulness", "Source Citation", "Answer Quality"]
        tv      = [t["avg_accuracy"], t["avg_faithfulness"], t["avg_source_citation"], t["avg_answer_quality"]]
        gv      = [g["avg_accuracy"], g["avg_faithfulness"], g["avg_source_citation"], g["avg_answer_quality"]]

        fig = go.Figure(data=[
            go.Bar(
                name="Traditional RAG", x=metrics, y=tv,
                marker_color="#2563EB", marker_line_color="rgba(0,0,0,0)",
                text=[f"{v}%" for v in tv], textposition="outside",
                textfont=dict(color="#93C5FD", size=11),
            ),
            go.Bar(
                name="Graph RAG", x=metrics, y=gv,
                marker_color="#059669", marker_line_color="rgba(0,0,0,0)",
                text=[f"{v}%" for v in gv], textposition="outside",
                textfont=dict(color="#6EE7B7", size=11),
            ),
        ])
        fig.update_layout(
            barmode="group",
            yaxis_range=[0, 118],
            title=dict(text="Performance Metrics Comparison", font=dict(color="#64748B", size=13)),
            **_DARK_PLOT,
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02,
                font=dict(color="#64748B"), bgcolor="rgba(0,0,0,0)",
                bordercolor="rgba(0,0,0,0)",
            ),
            yaxis=dict(**_DARK_PLOT["yaxis"], ticksuffix="%"),
            bargap=0.25, bargroupgap=0.06,
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
                textfont=dict(color="#94A3B8", size=11),
            ))
            fig2.update_layout(
                title=dict(text="Hallucination Risk  (lower is better)", font=dict(color="#64748B", size=12)),
                yaxis_range=[0, 105],
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
                textfont=dict(color="#94A3B8", size=11),
            ))
            fig3.update_layout(
                title=dict(text="Average Latency  (lower is better)", font=dict(color="#64748B", size=12)),
                **_DARK_PLOT,
                yaxis=dict(**_DARK_PLOT["yaxis"], ticksuffix="s"),
            )
            st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No evaluation data yet. Run `python3 evaluation/evaluator.py` from the terminal to generate results.")
        if st.session_state.pipelines_ready:
            if st.button("Run Quick Evaluation  (5 questions)", type="primary"):
                with st.spinner("Running evaluation — approximately 3 minutes…"):
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
        st.markdown(
            "<div class='arch-box'>"
            f"<div class='arch-label'>{ICON_VECTOR}<span style='color:#93C5FD;'>Traditional RAG Pipeline</span></div>"
            "<div class='arch-steps'>"
            "<span class='arch-step s-input'>PDF / TXT</span><span class='arr'>&rarr;</span>"
            "<span class='arch-step s-trad'>PyMuPDF</span><span class='arr'>&rarr;</span>"
            "<span class='arch-step s-trad'>Chunking 500 tok</span><span class='arr'>&rarr;</span>"
            "<span class='arch-step s-trad'>MiniLM embed</span><span class='arr'>&rarr;</span>"
            "<span class='arch-step s-trad'>ChromaDB</span><span class='arr'>&rarr;</span>"
            "<span class='arch-step s-trad'>Top-k cosine</span><span class='arr'>&rarr;</span>"
            "<span class='arch-step s-out'>Groq Llama 3.3</span>"
            "</div>"
            "<div class='insight'>"
            "<strong>Strengths:</strong> Fast index build, low query latency, simple updates.<br>"
            "<strong>Weaknesses:</strong> Entity relationships not preserved, semantic noise on complex queries."
            "</div>"
            "</div>",
            unsafe_allow_html=True
        )

    with cb:
        st.markdown(
            "<div class='arch-box'>"
            f"<div class='arch-label'>{ICON_GRAPH}<span style='color:#6EE7B7;'>Graph RAG Pipeline</span></div>"
            "<div class='arch-steps'>"
            "<span class='arch-step s-input'>PDF / TXT</span><span class='arr'>&rarr;</span>"
            "<span class='arch-step s-graph'>spaCy NER</span><span class='arr'>&rarr;</span>"
            "<span class='arch-step s-graph'>Entity extract</span><span class='arr'>&rarr;</span>"
            "<span class='arch-step s-graph'>Neo4j graph</span><span class='arr'>&rarr;</span>"
            "<span class='arch-step s-graph'>Cypher query</span><span class='arr'>&rarr;</span>"
            "<span class='arch-step s-graph'>Subgraph ctx</span><span class='arr'>&rarr;</span>"
            "<span class='arch-step s-out'>Groq Llama 3.3</span>"
            "</div>"
            "<div class='insight-g'>"
            "<strong>Strengths:</strong> Captures entity relationships, stronger multi-hop reasoning, explicit citations.<br>"
            "<strong>Weaknesses:</strong> Slower index build, higher query latency, more complex to maintain."
            "</div>"
            "</div>",
            unsafe_allow_html=True
        )

    st.markdown("<div class='section-hdr'>Technology Stack</div>", unsafe_allow_html=True)
    st.dataframe(
        pd.DataFrame({
            "Component":  ["LLM", "Embeddings", "Vector Store", "Graph DB", "NLP / NER", "Evaluation", "Frontend"],
            "Technology": [
                "Llama 3.3-70B via Groq API", "all-MiniLM-L6-v2  (local)",
                "ChromaDB 0.4.x", "Neo4j Community 5.x + APOC",
                "spaCy en_core_web_sm", "LLM-as-judge + Ragas",
                "Streamlit + Plotly",
            ],
            "Role": [
                "Answer generation (both pipelines)", "Document and query embedding",
                "Vector similarity search", "Knowledge graph storage",
                "Entity and relationship extraction", "Accuracy, hallucination, faithfulness metrics",
                "Interactive prototype UI",
            ],
        }),
        use_container_width=True, hide_index=True
    )

    st.markdown("<div class='section-hdr'>Corpus  ·  9 documents  ·  ~750 pages</div>", unsafe_allow_html=True)
    st.dataframe(
        pd.DataFrame({
            "Document": [
                "Basel III BIS Framework", "MiFID II Directive 2014/65/EU",
                "GDPR Regulation 2016/679/EU", "Sabadell Pillar III 2025",
                "Sabadell Annual Report 2025", "EBA AML Guidelines (sample)",
                "Basel III (sample)", "GDPR Banking (sample)", "MiFID II (sample)",
            ],
            "Size":   ["1.2 MB", "1.8 MB", "959 KB", "33 MB", "38 MB", "2.4 KB", "2.7 KB", "3.1 KB", "2.9 KB"],
            "Status": ["Loaded"] * 9,
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
            "<div class='empty-state'>"
            "<div class='empty-state-icon'>"
            "<svg width='24' height='24' viewBox='0 0 24 24' fill='none'>"
            "<rect x='3' y='4' width='18' height='16' rx='3' stroke='#E31837' stroke-width='1.5'/>"
            "<path d='M7 9h10M7 13h7' stroke='#E31837' stroke-width='1.5' stroke-linecap='round'/>"
            "</svg>"
            "</div>"
            "<h3>No queries yet</h3>"
            "<p>Run a comparison in the Live Demo tab.<br>All queries and results will be saved here for review.</p>"
            "</div>",
            unsafe_allow_html=True
        )
    else:
        c1, c2 = st.columns([5, 1])
        c1.caption(f"{len(st.session_state.query_history)} quer{'y' if len(st.session_state.query_history) == 1 else 'ies'} this session")
        with c2:
            if st.button("Clear history"):
                st.session_state.query_history = []
                st.session_state.last_result   = None
                st.rerun()

        for item in reversed(st.session_state.query_history):
            tl, gl = item["trad"]["latency_total"], item["graph"]["latency_total"]
            faster = "Graph RAG" if gl < tl else "Traditional RAG"
            fc     = "#6EE7B7" if gl < tl else "#93C5FD"
            with st.expander(f"{item['timestamp']}  ·  {item['query'][:80]}"):
                ca, cb = st.columns(2)
                with ca:
                    st.markdown(
                        f"<div style='font-weight:800;color:#93C5FD;margin-bottom:8px;font-size:0.85rem;'>"
                        f"Traditional RAG"
                        f"<span style='font-size:0.75rem;font-weight:500;color:#1E3251;margin-left:8px;'>{tl:.2f}s</span></div>",
                        unsafe_allow_html=True
                    )
                    st.write(item["trad"]["answer"])
                    if item["trad"]["sources"]:
                        st.markdown(
                            "<span style='font-size:0.75rem;color:#334155;font-weight:600;'>Sources: </span>"
                            + "<span style='font-size:0.75rem;color:#1E3A6E;'>"
                            + " &middot; ".join(item["trad"]["sources"][:3])
                            + "</span>",
                            unsafe_allow_html=True
                        )
                with cb:
                    st.markdown(
                        f"<div style='font-weight:800;color:#6EE7B7;margin-bottom:8px;font-size:0.85rem;'>"
                        f"Graph RAG"
                        f"<span style='font-size:0.75rem;font-weight:500;color:#1E3251;margin-left:8px;'>{gl:.2f}s</span></div>",
                        unsafe_allow_html=True
                    )
                    st.write(item["graph"]["answer"])
                    if item["graph"].get("graph_paths"):
                        for p in item["graph"]["graph_paths"][:2]:
                            st.markdown(
                                f"<div class='graph-path-card'>&rarr; {p}</div>",
                                unsafe_allow_html=True
                            )
                st.markdown(
                    f"<div style='margin-top:12px;padding-top:12px;border-top:1px solid #111D35;"
                    f"font-size:0.78rem;color:{fc};font-weight:700;letter-spacing:0.02em;'>"
                    f"Faster pipeline: {faster}</div>",
                    unsafe_allow_html=True
                )
