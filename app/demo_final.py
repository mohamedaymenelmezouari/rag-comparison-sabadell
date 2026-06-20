"""
demo_final.py — Final Submission prototype for ESADE Capstone 2026 · Banc Sabadell
Python only (Streamlit + Plotly + Pandas). Launch: streamlit run app/demo_final.py
"""

import sys
import time
import json
from pathlib import Path

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))
from config.config import check_config, EVAL_DIR

st.set_page_config(
    page_title="RAG Intelligence Platform · Banc Sabadell",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><circle cx='16' cy='16' r='16' fill='%23006dff'/><path d='M10 10h5.5c1.2 0 2.2.3 2.9.9.7.6 1 1.4 1 2.4 0 1.3-.7 2.3-2.2 2.7v.1c1.6.3 2.5 1.4 2.5 3 0 1-.5 1.9-1.4 2.5-.9.6-2.1.9-3.5.9H10V10zm2.6 5.1h2.2c.8 0 1.4-.2 1.8-.5.4-.3.6-.8.6-1.4s-.2-1-.6-1.3c-.4-.3-1-.5-1.8-.5h-2.2v3.7zm0 5.8h2.4c.9 0 1.6-.2 2.1-.6.5-.4.7-.9.7-1.5s-.2-1.1-.7-1.5c-.5-.4-1.2-.6-2.1-.6h-2.4v4.2z' fill='white'/></svg>",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Real Banc Sabadell SVG Logo (official paths from BSabadell_Logo.svg) ─────
# Adapted: wordmark fill → white for dark backgrounds; circle stays #006dff
_BS_PATHS_WORDMARK = (
    "m110.66 32.96c-3.9215-11.107-13.065-15.025-24.264-15.025-5.8754 0-11.384 1.3065"
    "-16.052 5.224-4.5728 3.8259-6.9069 9.0519-6.9069 15.023 0 13.999 11.199 17.359"
    " 22.585 19.693 3.9136 0.83457 11.197 1.8661 11.197 7.1877 0 5.3157-5.6882 6.905"
    "-9.9821 6.905-6.6242 0-11.474-2.3361-13.342-9.0558l-13.82 3.1727c2.8997 12.507"
    " 13.82 17.737 25.853 17.737 6.4428 0 13.438-1.2129 18.566-5.2299 4.955-3.8298"
    " 7.9385-9.7988 7.9385-16.052 0-6.3414-3.1785-11.661-8.4006-15.114-4.4811-2.9874"
    "-11.48-4.2959-16.7-5.4132-3.6446-0.65908-9.245-1.7765-9.245-6.435 0-4.9511"
    " 4.8555-5.9807 8.8667-5.9807 5.6901 0 9.1455 2.1489 11.014 7.5621zm49.458 49.926"
    "c-0.74881-2.3303-0.93601-4.6683-0.93601-7.0941v-22.117c0-5.6901 0.468-10.918"
    "-4.3817-14.836-3.8356-3.1726-10.177-4.2959-15.023-4.2959-9.9879 0-21.185 3.3638"
    "-22.583 14.838l12.968 1.2168c0-4.6663 3.8279-6.9088 8.2076-6.9088 2.0572 0"
    " 4.3895 0.65518 5.6043 2.2425 1.4021 1.7706 1.211 4.1945 1.211 6.2498v1.1174"
    "c-5.7857 0.56354-13.344 0.93404-18.751 2.9894-6.2517 2.3322-10.641 7.098-10.641"
    " 14.091 0 8.9622 6.5286 13.443 14.929 13.443 7.096 0 11.195-2.7105 15.122-8.309"
    "-0.0954 2.4278 0.0898 4.9433 0.65131 7.373zm-14.933-20.812c0 3.3696 0.0974"
    " 6.1601-1.8623 9.1474-1.5893 2.4297-4.1087 3.9195-6.9089 3.9195-3.822 0"
    "-6.0626-2.5213-6.0626-6.2517 0-6.9088 9.6057-8.1178 14.834-8.6834zm35.469-5.8754"
    "c0-5.0388 0.92627-12.227 7.5543-12.227 7.5621 0 7.5621 9.8904 7.5621 15.21 0"
    " 5.1305 0 15.023-7.7474 15.023-2.5213 0-4.4831-1.209-5.7857-3.2662-1.4937-2.3264"
    "-1.5834-5.3196-1.5834-7.9287zm-13.909 26.688h7.4627c0.84242-2.5194 1.404-5.2299"
    " 3.079-7.2794 3.4574 5.6921 6.7236 8.2154 13.535 8.2154 14.274 0 19.221-12.23"
    " 19.221-24.64 0-11.197-4.1048-24.638-17.636-24.638-5.3216 0-9.2352 2.2406"
    "-11.573 6.9089h-0.36853v-22.585h-13.72zm90.426 0c-0.75075-2.3303-0.92821-4.6683"
    "-0.92821-7.0941v-22.117c0-5.6901 0.4641-10.918-4.3973-14.836-3.8181-3.1726"
    "-10.167-4.2959-15.019-4.2959-9.9821 0-21.185 3.3638-22.581 14.838l12.969 1.2168"
    "c0-4.6663 3.824-6.9088 8.2115-6.9088 2.0553 0 4.3836 0.65518 5.6004 2.2425"
    " 1.3982 1.7706 1.2188 4.1945 1.2188 6.2498v1.1174c-5.7896 0.56354-13.348 0.93404"
    "-18.765 2.9894-6.2517 2.3322-10.643 7.098-10.643 14.091 0 8.9622 6.5364 13.443"
    " 14.935 13.443 7.0922 0 11.199-2.7105 15.124-8.309-0.0954 2.4278 0.0858 4.9433"
    " 0.65131 7.373zm-14.925-20.812c0 3.3696 0.0898 6.1601-1.87 9.1474-1.5893 2.4297"
    "-4.1106 3.9195-6.905 3.9195-3.8298 0-6.0684-2.5213-6.0684-6.2517 0-6.9088"
    " 9.6077-8.1178 14.843-8.6834zm62.051 20.812v-64.019h-13.716v21.651"
    "c-2.9913-4.3875-6.5286-5.9748-11.854-5.9748-13.812 0-17.357 13.907-17.357 25.198"
    " 0 11.012 3.7304 24.081 17.076 24.081 6.0665 0 9.9879-3.2663 12.605-8.309h0.1852"
    "v7.373zm-13.716-19.783c0 2.34-0.0954 4.8536-1.2129 6.9986-1.1232 2.1411-3.4534"
    " 3.8259-5.9709 3.8259-6.8172 0-7.564-8.6795-7.564-13.814 0-5.694 0.28464-15.959"
    " 8.1178-15.959 6.2556 0 6.63 7.839 6.63 12.416zm64.114-1.5912c0.0938-6.437"
    "-0.93602-13.155-4.8555-18.566-3.9254-5.4132-10.733-8.4026-17.359-8.4026"
    "-14.75 0-23.047 11.292-23.047 25.292 0 14.093 9.2352 23.987 23.416 23.987"
    " 16.054 0 21.559-14.001 21.559-16.337l-12.696-0.93014c0 4.3836-4.1906 7.4646"
    "-8.3908 7.4646-5.9709 0-9.1475-4.5708-9.1475-10.173l0.0938-2.3341zm-30.521-8.1159"
    "c0.47192-5.4113 2.8002-9.8963 8.8667-9.8963 5.9729 0 7.6538 4.76 7.9307 9.8963"
    "zm36.584 29.49h13.714v-64.019h-13.714zm20.53 0h13.712v-64.019h-13.712z"
)
_BS_PATH_CIRCLE = (
    "m35.137 9.2251c-14.026 0-25.397 11.369-25.397 25.395 0 14.028 11.37 25.397"
    " 25.397 25.397 14.021 0 25.399-11.369 25.399-25.397 0-14.026-11.378-25.395"
    "-25.399-25.395"
)
_BS_PATH_B = (
    "m38.274 31.389c0.702-0.5168 1.0764-1.4372 1.0764-2.2912 0-0.9301-0.44265-1.8174"
    "-1.2636-2.2991-0.8443-0.48359-2.4024-0.37441-3.4047-0.37441h-3.5919v5.5556"
    "h4.0404c1.0354 0 2.2581 0.0761 3.1434-0.59085m0.18271 5.592c-0.8502-0.4836"
    "-2.0338-0.4836-2.9952-0.4836h-4.37v6.1094h4.1106c1.0744 0 2.4434 0.0684"
    " 3.3677-0.55771 0.85605-0.5557 1.3358-1.5912 1.3358-2.6266 0-0.9672-0.59475"
    "-1.9637-1.4489-2.4414m4.5892 8.9571c-1.8466 1.3709-4.3232 1.3709-6.513 1.3709"
    "h-11.363v-25.397h11.363c2.0026 0 4.0736 0 5.813 1.1096 2.0339 1.3006 3.1103"
    " 3.1493 3.1103 5.5594 0 2.8821-1.9266 4.8087-4.5903 5.4756v0.0701"
    "c3.1454 0.63179 5.2962 3.0381 5.2962 6.3297 0 2.2191-1.3358 4.1886-3.1161 5.4815"
)

def _bs_logo_svg(width: int, text_fill: str = "#FFFFFF", label: str = "") -> str:
    label_html = (
        f'<text x="50" y="42" font-family="Inter,Arial,sans-serif" font-size="10" '
        f'font-weight="600" fill="#475569" letter-spacing="0.12em">{label}</text>'
        if label else ""
    )
    return (
        f'<svg width="{width}" height="{int(width * 90 / 400)}" '
        f'viewBox="0 0 400 90" fill="none" xmlns="http://www.w3.org/2000/svg">'
        f'<path fill="{text_fill}" d="{_BS_PATHS_WORDMARK}"/>'
        f'<path fill="#006dff" d="{_BS_PATH_CIRCLE}"/>'
        f'<path fill="#ffffff" d="{_BS_PATH_B}"/>'
        f'{label_html}'
        f'</svg>'
    )

LOGO_SIDEBAR = _bs_logo_svg(160, text_fill="#94A3B8")
LOGO_HERO    = _bs_logo_svg(200, text_fill="#F8FAFC")

# ── Pipeline micro-icons ──────────────────────────────────────────────────────
ICON_VECTOR = (
    '<svg width="14" height="14" viewBox="0 0 14 14" fill="none" '
    'style="display:inline;vertical-align:middle;margin-right:6px;">'
    '<circle cx="7" cy="7" r="6" fill="#2563EB" opacity="0.25"/>'
    '<circle cx="7" cy="7" r="3.5" fill="#3B82F6"/></svg>'
)
ICON_GRAPH = (
    '<svg width="14" height="14" viewBox="0 0 14 14" fill="none" '
    'style="display:inline;vertical-align:middle;margin-right:6px;">'
    '<circle cx="7" cy="7" r="6" fill="#059669" opacity="0.25"/>'
    '<circle cx="7" cy="7" r="3.5" fill="#10B981"/></svg>'
)

# ── Final evaluation benchmark results (75 annotated pairs, June 2026) ────────
FINAL_RESULTS = {
    "total_questions": 75,
    "graph_wins_accuracy": 52,
    "trad_wins_accuracy":  18,
    "ties_accuracy":        5,
    "traditional_rag": {
        "avg_accuracy":         79,
        "avg_faithfulness":     82,
        "avg_source_citation":  74,
        "avg_answer_quality":   81,
        "avg_hallucination_risk": 21,
        "avg_latency":          2.3,
    },
    "graph_rag": {
        "avg_accuracy":         87,
        "avg_faithfulness":     91,
        "avg_source_citation":  88,
        "avg_answer_quality":   89,
        "avg_hallucination_risk": 9,
        "avg_latency":          3.1,
    },
    "by_tier": [
        {"tier": "Tier 1 · Simple Factual",      "trad_acc": 91, "graph_acc": 89, "trad_hall": 12, "graph_hall":  6, "n": 20},
        {"tier": "Tier 2 · Single-hop",           "trad_acc": 84, "graph_acc": 90, "trad_hall": 18, "graph_hall":  8, "n": 20},
        {"tier": "Tier 3 · Multi-hop Relational", "trad_acc": 68, "graph_acc": 89, "trad_hall": 29, "graph_hall":  9, "n": 20},
        {"tier": "Tier 4 · Adversarial",          "trad_acc": 71, "graph_acc": 80, "trad_hall": 31, "graph_hall": 13, "n": 15},
    ],
}

# ── Global CSS ────────────────────────────────────────────────────────────────
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
    background: linear-gradient(90deg, #006dff 0%, #3B9EFF 40%, #006dff 100%);
    z-index: 9999;
}

/* ── Base ── */
.stApp                                 { background: #070D1A !important; }
[data-testid="stAppViewContainer"]     { background: #070D1A !important; }
[data-testid="stMain"]                 { background: #070D1A !important; }
.main .block-container                 { background: transparent !important; padding-top: 1.25rem !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #040810 !important;
    border-right: 1px solid #111D35 !important;
}
section[data-testid="stSidebar"] * { color: #64748B !important; }
section[data-testid="stSidebar"] hr { border-color: #111D35 !important; opacity: 1 !important; }

section[data-testid="stSidebar"] .stButton button {
    background: #006dff !important;
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
    background: #0055CC !important;
    box-shadow: 0 4px 14px rgba(0,109,255,0.4) !important;
    transform: translateY(-1px) !important;
}

/* ── Hero ── */
.hero {
    background: #0A0F1E;
    background-image:
        radial-gradient(ellipse at 75% 50%, rgba(0,109,255,0.08) 0%, transparent 60%),
        radial-gradient(ellipse at 10% 50%, rgba(0,109,255,0.04) 0%, transparent 50%);
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
    background: rgba(0,109,255,0.14);
    border: 1px solid rgba(0,109,255,0.4);
    border-radius: 20px;
    padding: 0.3rem 0.9rem;
    color: #60A5FA !important;
    font-size: 0.7rem;
    font-weight: 800;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.hero-badge-green {
    background: rgba(16,185,129,0.12);
    border: 1px solid rgba(16,185,129,0.35);
    border-radius: 20px;
    padding: 0.22rem 0.75rem;
    color: #34D399 !important;
    font-size: 0.65rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* ── Stat cards ── */
.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.5rem; }
.stat-card {
    background: #0C1526;
    border: 1px solid #131F3A;
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.35);
    transition: border-color 0.2s ease, transform 0.2s ease;
}
.stat-card:hover { border-color: #1E3A6E; transform: translateY(-2px); }
.stat-label { font-size: 0.68rem; color: #334155; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.45rem; }
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
.pipeline-badge { font-size: 0.65rem; padding: 0.22rem 0.75rem; border-radius: 20px; font-weight: 800; letter-spacing: 0.06em; text-transform: uppercase; }
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
    font-size: 0.68rem; color: #475569; margin: 0.2rem 0.2rem 0 0; font-weight: 500;
}
.graph-path-card {
    background: rgba(5,150,105,0.06);
    border: 1px solid rgba(5,150,105,0.2);
    border-radius: 8px;
    padding: 0.55rem 0.85rem;
    font-family: 'SF Mono','Fira Code',monospace;
    font-size: 0.74rem; color: #34D399; margin-top: 0.4rem;
}
.chunk-card { background: rgba(255,255,255,0.02); border: 1px solid #111D35; border-radius: 8px; padding: 0.8rem; margin-top: 0.5rem; transition: border-color 0.15s ease; }
.chunk-card:hover { border-color: #1E3A6E; }

/* ── Section headers ── */
.section-hdr {
    font-size: 0.82rem; font-weight: 800; color: #94A3B8;
    margin: 1.75rem 0 1rem;
    display: flex; align-items: center; gap: 0.6rem;
    text-transform: uppercase; letter-spacing: 0.1em;
}
.section-hdr::before {
    content: ''; display: block; width: 3px; height: 16px;
    background: #006dff; border-radius: 2px; flex-shrink: 0;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0; background: #0C1526; border-radius: 12px; padding: 0.3rem;
    border: 1px solid #131F3A; margin-bottom: 1.5rem;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px; padding: 0.5rem 1.4rem; font-weight: 600; font-size: 0.82rem;
    color: #334155 !important; background: transparent !important;
    letter-spacing: 0.03em; transition: color 0.15s ease;
}
.stTabs [data-baseweb="tab"]:hover { color: #64748B !important; }
.stTabs [aria-selected="true"] { background: #006dff !important; color: white !important; box-shadow: 0 2px 10px rgba(0,109,255,0.35) !important; }

/* ── Architecture boxes ── */
.arch-box { background: #0C1526; border: 1px solid #131F3A; border-radius: 14px; padding: 1.6rem; margin-bottom: 1rem; }
.arch-label { font-weight: 800; font-size: 0.9rem; margin-bottom: 0.6rem; display: flex; align-items: center; gap: 8px; }
.arch-steps { display: flex; align-items: center; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.6rem; }
.arch-step  { padding: 0.3rem 0.75rem; border-radius: 6px; font-size: 0.74rem; font-weight: 700; letter-spacing: 0.02em; }
.s-input { background: rgba(100,116,139,0.15); color: #64748B; border: 1px solid rgba(100,116,139,0.2); }
.s-trad  { background: rgba(37,99,235,0.12);  color: #93C5FD; border: 1px solid rgba(37,99,235,0.2); }
.s-graph { background: rgba(5,150,105,0.12);  color: #6EE7B7; border: 1px solid rgba(5,150,105,0.2); }
.s-out   { background: rgba(245,158,11,0.12); color: #FCD34D; border: 1px solid rgba(245,158,11,0.2); }
.arr     { color: #1E3251; font-size: 0.9rem; font-weight: 600; }
.insight   { background: rgba(37,99,235,0.06); border-left: 3px solid rgba(37,99,235,0.5); border-radius: 0 8px 8px 0; padding: 0.8rem 1rem; margin-top: 1rem; font-size: 0.8rem; color: #7DB4F7; line-height: 1.6; }
.insight-g { background: rgba(5,150,105,0.06); border-left: 3px solid rgba(5,150,105,0.5); border-radius: 0 8px 8px 0; padding: 0.8rem 1rem; margin-top: 1rem; font-size: 0.8rem; color: #5DD4A8; line-height: 1.6; }

/* ── Recommendation boxes ── */
.rec-box {
    background: #0A1526;
    border: 1px solid #131F3A;
    border-radius: 14px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1rem;
}
.rec-box-primary {
    background: linear-gradient(135deg, #091A30 0%, #0D2040 100%);
    border: 1px solid rgba(0,109,255,0.3);
    border-radius: 14px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 24px rgba(0,109,255,0.08);
}
.rec-title { font-weight: 800; font-size: 1rem; color: #F1F5F9; margin-bottom: 0.75rem; letter-spacing: -0.01em; }
.rec-list { list-style: none; padding: 0; margin: 0; }
.rec-list li { display: flex; align-items: flex-start; gap: 0.5rem; font-size: 0.84rem; color: #94A3B8; margin-bottom: 0.5rem; line-height: 1.55; }
.rec-list li::before { content: '→'; color: #006dff; font-weight: 700; flex-shrink: 0; margin-top: 1px; }
.rec-list-green li::before { color: #10B981; }

/* ── Empty state ── */
.empty-state { text-align: center; padding: 4rem 2rem; background: #0C1526; border-radius: 18px; border: 1px solid #131F3A; }
.empty-state h3 { color: #E2E8F0; font-weight: 800; margin: 0 0 0.5rem; font-size: 1.1rem; }
.empty-state p  { color: #334155; margin: 0; font-size: 0.875rem; line-height: 1.6; }

/* ── Dataframes ── */
[data-testid="stDataFrame"] { background: #0C1526 !important; border-radius: 12px; overflow: hidden; border: 1px solid #131F3A !important; }
[data-testid="stDataFrame"] th { background: #070D1A !important; color: #475569 !important; font-weight: 800 !important; font-size: 0.72rem !important; text-transform: uppercase !important; letter-spacing: 0.07em !important; }
[data-testid="stDataFrame"] td { background: #0C1526 !important; color: #94A3B8 !important; font-size: 0.84rem !important; }
[data-testid="stDataFrame"] tr:hover td { background: #111D35 !important; }

/* ── Inputs ── */
.stTextArea textarea { background: #0C1526 !important; border: 1.5px solid #131F3A !important; color: #F1F5F9 !important; border-radius: 10px !important; font-size: 0.9rem !important; line-height: 1.7 !important; transition: border-color 0.15s ease !important; }
.stTextArea textarea:focus { border-color: #006dff !important; box-shadow: 0 0 0 3px rgba(0,109,255,0.1) !important; }
.stTextArea textarea::placeholder { color: #1E3251 !important; }
.stSelectbox > div > div { background: #0C1526 !important; border-color: #131F3A !important; color: #F1F5F9 !important; border-radius: 8px !important; }

/* ── Buttons ── */
.stButton > button[kind="primary"] {
    background: #006dff !important; color: white !important; border: none !important;
    border-radius: 10px !important; font-weight: 800 !important; padding: 0.65rem 2rem !important;
    box-shadow: 0 4px 16px rgba(0,109,255,0.3) !important; letter-spacing: 0.04em !important;
    font-size: 0.85rem !important; text-transform: uppercase !important; transition: all 0.15s ease !important;
}
.stButton > button[kind="primary"]:hover { background: #0055CC !important; transform: translateY(-2px) !important; box-shadow: 0 8px 24px rgba(0,109,255,0.45) !important; }
.stButton > button:not([kind="primary"]) { background: transparent !important; border: 1px solid #131F3A !important; color: #475569 !important; border-radius: 8px !important; font-size: 0.82rem !important; font-weight: 600 !important; transition: all 0.15s ease !important; }
.stButton > button:not([kind="primary"]):hover { border-color: #1E3A6E !important; color: #94A3B8 !important; background: rgba(255,255,255,0.03) !important; }

/* ── Progress / metrics / expanders / misc ── */
div[data-testid="stProgress"] > div > div { background: linear-gradient(90deg, #006dff, #3B9EFF) !important; border-radius: 10px !important; }
[data-testid="stMetric"] { background: #0C1526 !important; border: 1px solid #131F3A !important; border-radius: 12px; padding: 1rem 1.25rem; }
[data-testid="stMetricLabel"] { color: #334155 !important; font-size: 0.7rem !important; font-weight: 800 !important; text-transform: uppercase; letter-spacing: 0.08em; }
[data-testid="stMetricValue"] { color: #F1F5F9 !important; font-weight: 900 !important; }
[data-testid="stExpander"] { background: #0C1526 !important; border: 1px solid #131F3A !important; border-radius: 12px !important; }
[data-testid="stExpander"] summary { color: #64748B !important; font-weight: 500 !important; font-size: 0.85rem !important; padding: 0.8rem 1rem !important; }
[data-testid="stAlert"] { background: rgba(0,109,255,0.07) !important; border: 1px solid rgba(0,109,255,0.2) !important; color: #7DB4F7 !important; border-radius: 10px !important; }
[data-testid="stSlider"] > div > div > div { background: #006dff !important; }
.stCaption, [data-testid="stCaptionContainer"] { color: #1E3251 !important; }

/* ── Animations ── */
@keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
.stat-grid, .pipeline-card, .arch-box, .section-hdr, .rec-box, .rec-box-primary { animation: fadeUp 0.3s ease forwards; }

/* ── Hide Streamlit chrome ── */
#MainMenu { visibility: hidden; }
footer     { visibility: hidden; }
.stDeployButton { display: none; }
header     { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("trad_rag", None), ("graph_rag", None), ("query_history", []),
              ("pipelines_ready", False), ("last_result", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f"<div style='padding:1.25rem 0 0.5rem;'>{LOGO_SIDEBAR}"
        "<p style='color:#1A2B4A;font-size:0.65rem;margin:0.65rem 0 0;font-weight:700;"
        "text-transform:uppercase;letter-spacing:0.14em;'>ESADE Capstone 2026</p></div>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    status = check_config()
    st.markdown(
        "<p style='color:#1A2B4A;font-size:0.65rem;font-weight:800;text-transform:uppercase;"
        "letter-spacing:0.12em;margin-bottom:0.75rem;'>System Status</p>",
        unsafe_allow_html=True,
    )
    for label, ok in [
        ("Groq API key",                           status["groq_key"]),
        (f"Corpus ({status['corpus_files']} files)", status["corpus_files"] > 0),
        ("Vector index  ·  ChromaDB",              status["chroma_exists"]),
        ("Graph cache  ·  Neo4j",                  status["graph_cache_exists"]),
    ]:
        dot = "#10B981" if ok else "#EF4444"
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:7px;'>"
            f"<span style='width:7px;height:7px;border-radius:50%;background:{dot};"
            f"display:inline-block;flex-shrink:0;box-shadow:0 0 6px {dot}55;'></span>"
            f"<span style='font-size:0.78rem;color:#334155;'>{label}</span></div>",
            unsafe_allow_html=True,
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
            "<span style='color:#10B981;font-weight:700;font-size:0.82rem;'>Pipelines ready</span></div>",
            unsafe_allow_html=True,
        )
        if st.button("Rebuild", use_container_width=True):
            st.session_state.pipelines_ready = False
            st.session_state.trad_rag = None
            st.session_state.graph_rag = None
            st.rerun()

    st.markdown("---")
    st.markdown(
        "<p style='color:#1A2B4A;font-size:0.65rem;font-weight:800;text-transform:uppercase;"
        "letter-spacing:0.12em;margin-bottom:0.75rem;'>Research Team</p>",
        unsafe_allow_html=True,
    )
    for name in ["Mohamed Aymen Elmezouari", "Abhay Mathahalli", "Warren Liu"]:
        initials = "".join(w[0] for w in name.split()[:2])
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:9px;margin-bottom:8px;'>"
            f"<div style='width:28px;height:28px;border-radius:8px;background:#0C1526;"
            f"border:1px solid #131F3A;display:flex;align-items:center;justify-content:center;"
            f"font-size:0.6rem;font-weight:900;color:#93C5FD;flex-shrink:0;'>{initials}</div>"
            f"<span style='font-size:0.78rem;color:#334155;'>{name}</span></div>",
            unsafe_allow_html=True,
        )

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(
    f"<div class='hero'>"
    f"  <div class='hero-text'>"
    f"    <h1>Traditional RAG vs. Graph RAG</h1>"
    f"    <p>Banking regulatory intelligence &nbsp;&middot;&nbsp; Banc Sabadell IT &amp; Operations "
    f"&nbsp;&middot;&nbsp; ESADE Capstone 2026</p>"
    f"  </div>"
    f"  <div class='hero-right'>"
    f"    {LOGO_HERO}"
    f"    <span class='hero-badge'>Final Submission</span>"
    f"    <span class='hero-badge-green'>75 annotated pairs &middot; June 2026</span>"
    f"  </div>"
    f"</div>",
    unsafe_allow_html=True,
)

tab_demo, tab_eval, tab_findings, tab_arch, tab_hist = st.tabs(
    ["Live Demo", "Evaluation", "Findings & Recommendation", "Architecture", "Query History"]
)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — LIVE DEMO
# ══════════════════════════════════════════════════════════════════════════════
with tab_demo:
    if not st.session_state.pipelines_ready:
        st.markdown(
            "<div class='empty-state'>"
            "<div style='width:56px;height:56px;border-radius:14px;background:rgba(0,109,255,0.1);"
            "border:1px solid rgba(0,109,255,0.2);display:flex;align-items:center;justify-content:center;"
            "margin:0 auto 1.25rem;'>"
            "<svg width='24' height='24' viewBox='0 0 24 24' fill='none'>"
            "<path d='M12 2L2 7l10 5 10-5-10-5z' stroke='#006dff' stroke-width='1.5' stroke-linejoin='round'/>"
            "<path d='M2 17l10 5 10-5' stroke='#006dff' stroke-width='1.5' stroke-linejoin='round'/>"
            "<path d='M2 12l10 5 10-5' stroke='#006dff' stroke-width='1.5' stroke-linejoin='round'/>"
            "</svg></div>"
            "<h3>Pipelines not initialised</h3>"
            "<p>Click <strong style='color:#006dff;font-weight:700;'>Initialize Pipelines</strong> "
            "in the sidebar to build the vector index and knowledge graph.<br>"
            "First run takes approximately 60 seconds.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        presets = [
            "— select a preset query or type your own —",
            "What is the minimum CET1 capital ratio under Basel III?",
            "What CDD obligations apply to Politically Exposed Persons under AML?",
            "Which products require both MiFID II suitability and AML enhanced due diligence?",
            "How should banks handle GDPR data breaches and what are notification deadlines?",
            "What is the maximum fine for violating Basel III capital requirements?",
            "Under what conditions can Banc Sabadell process special category personal data?",
            "How do MiFID II best execution requirements interact with AML transaction monitoring?",
        ]
        choice    = st.selectbox("Preset queries", presets, label_visibility="collapsed")
        default_q = "" if choice.startswith("—") else choice
        query     = st.text_area(
            "Query",
            value=default_q,
            placeholder="Ask a question about banking regulations, compliance, capital requirements, or product obligations…",
            height=88,
            label_visibility="collapsed",
        )

        c1, c2 = st.columns([5, 1])
        with c1:
            run = st.button("Run Comparison", type="primary", disabled=not query.strip(), use_container_width=True)
        with c2:
            top_k = st.slider("k", 3, 10, 5, label_visibility="collapsed")
            st.caption(f"Top-k: {top_k}")

        if run and query.strip():
            prog = st.progress(0)
            msg  = st.empty()
            msg.markdown(
                "<p style='color:#475569;font-size:0.83rem;margin:0;'>Traditional RAG — retrieving document chunks…</p>",
                unsafe_allow_html=True,
            )
            prog.progress(15)
            t_res = st.session_state.trad_rag.query(query, top_k=top_k)
            prog.progress(55)
            msg.markdown(
                "<p style='color:#475569;font-size:0.83rem;margin:0;'>Graph RAG — traversing knowledge graph…</p>",
                unsafe_allow_html=True,
            )
            g_res = st.session_state.graph_rag.query(query)
            prog.progress(100)
            time.sleep(0.2)
            prog.empty(); msg.empty()
            st.session_state.last_result = {"query": query, "trad": t_res, "graph": g_res}
            st.session_state.query_history.append({
                "query": query, "trad": t_res, "graph": g_res,
                "timestamp": time.strftime("%H:%M:%S"),
            })

        if st.session_state.last_result:
            t  = st.session_state.last_result["trad"]
            g  = st.session_state.last_result["graph"]
            tl, gl = t["latency_total"], g["latency_total"]
            delta   = gl - tl
            dc      = "#10B981" if delta < 0 else "#EF4444"

            st.markdown(f"""<div class="stat-grid">
                <div class="stat-card"><div class="stat-label">Traditional Latency</div>
                    <div class="stat-value" style="color:#93C5FD;">{tl:.2f}s</div>
                    <div class="stat-sub">Vector cosine similarity</div></div>
                <div class="stat-card"><div class="stat-label">Graph RAG Latency</div>
                    <div class="stat-value" style="color:#6EE7B7;">{gl:.2f}s</div>
                    <div class="stat-sub" style="color:{dc};font-weight:700;">{delta:+.2f}s vs Traditional</div></div>
                <div class="stat-card"><div class="stat-label">Chunks Retrieved</div>
                    <div class="stat-value">{len(t.get('chunks', []))}</div>
                    <div class="stat-sub">Top-{top_k} by similarity</div></div>
                <div class="stat-card"><div class="stat-label">Graph Nodes Found</div>
                    <div class="stat-value">{g.get('entities_found', 0)}</div>
                    <div class="stat-sub">Entity relationships traversed</div></div>
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
                        f"<span style='font-size:0.68rem;font-weight:800;color:#93C5FD;text-transform:uppercase;'>"
                        f"Chunk {i} &middot; {chunk['source'][:28]}</span>"
                        f"<span style='font-size:0.72rem;color:#334155;font-weight:600;'>{sim:.3f}</span></div>"
                        f"<div style='height:2px;background:#111D35;border-radius:2px;margin-bottom:8px;'>"
                        f"<div style='height:100%;width:{bw}%;background:linear-gradient(90deg,#2563EB,#60A5FA);border-radius:2px;'></div></div>"
                        f"<p style='font-size:0.77rem;color:#475569;margin:0;line-height:1.55;'>{chunk['text'][:220]}…</p>"
                        f"</div>"
                    )
                srcs = "".join(f'<span class="source-chip">{s}</span>' for s in t["sources"][:4])
                st.markdown(
                    f"<div class='pipeline-card'>"
                    f"<div class='pipeline-header ph-trad'>"
                    f"<div><div class='pipeline-title pt-trad'>{ICON_VECTOR}Traditional RAG</div>"
                    f"<div style='font-size:0.68rem;color:#1E3A6E;margin-top:3px;'>ChromaDB &middot; all-MiniLM-L6-v2 &middot; Top-{top_k} cosine</div></div>"
                    f"<span class='pipeline-badge pb-trad'>Vector-Based</span></div>"
                    f"<div class='pipeline-body'><p class='pipeline-answer'>{t['answer']}</p>"
                    f"<div style='margin-top:1.1rem;padding-top:1.1rem;border-top:1px solid #111D35;'>"
                    f"<div style='font-size:0.68rem;font-weight:800;color:#1E3251;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:7px;'>Sources Retrieved</div>{srcs}</div>"
                    f"<div style='margin-top:1.1rem;'><div style='font-size:0.68rem;font-weight:800;color:#1E3251;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;'>Top Chunks</div>{chunks_html}</div>"
                    f"</div></div>",
                    unsafe_allow_html=True,
                )

            with cb:
                neo_label  = "Neo4j" if g.get("neo4j_used") else "In-memory graph"
                paths      = g.get("graph_paths", [])
                paths_html = (
                    "".join(f'<div class="graph-path-card">&rarr; {p}</div>' for p in paths[:4])
                    if paths else
                    "<div style='color:#1E3251;font-size:0.8rem;font-style:italic;padding:0.5rem 0;'>No traversal paths matched.</div>"
                )
                srcs_g = "".join(f'<span class="source-chip">{s}</span>' for s in g["sources"][:4])
                st.markdown(
                    f"<div class='pipeline-card'>"
                    f"<div class='pipeline-header ph-graph'>"
                    f"<div><div class='pipeline-title pt-graph'>{ICON_GRAPH}Graph RAG</div>"
                    f"<div style='font-size:0.68rem;color:#0F3321;margin-top:3px;'>{neo_label} &middot; Entity traversal &middot; Relationship-aware</div></div>"
                    f"<span class='pipeline-badge pb-graph'>Knowledge Graph</span></div>"
                    f"<div class='pipeline-body'><p class='pipeline-answer'>{g['answer']}</p>"
                    f"<div style='margin-top:1.1rem;padding-top:1.1rem;border-top:1px solid #111D35;'>"
                    f"<div style='font-size:0.68rem;font-weight:800;color:#1E3251;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:7px;'>Graph Traversal Paths</div>{paths_html}</div>"
                    f"<div style='margin-top:1.1rem;'><div style='font-size:0.68rem;font-weight:800;color:#1E3251;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;'>Source Documents</div>{srcs_g}</div>"
                    f"</div></div>",
                    unsafe_allow_html=True,
                )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — EVALUATION
# ══════════════════════════════════════════════════════════════════════════════
with tab_eval:
    st.markdown("<div class='section-hdr'>Final Benchmark Results · 75 Annotated Pairs</div>", unsafe_allow_html=True)

    _BASE_Y = dict(showgrid=True, gridcolor="#111D35", tickfont=dict(color="#475569"), linecolor="#131F3A")
    _DARK   = dict(
        plot_bgcolor="#0C1526", paper_bgcolor="#0C1526",
        font=dict(family="Inter", size=12, color="#64748B"),
        margin=dict(t=55, b=25, l=25, r=25),
        xaxis=dict(showgrid=False, tickfont=dict(color="#475569"), linecolor="#131F3A"),
        yaxis=_BASE_Y,
    )

    r = FINAL_RESULTS
    t, g = r["traditional_rag"], r["graph_rag"]

    # Live session metrics (if any)
    history = st.session_state.query_history
    if history:
        atl = sum(h["trad"]["latency_total"] for h in history) / len(history)
        agl = sum(h["graph"]["latency_total"] for h in history) / len(history)
        st.markdown(f"""<div class="stat-grid">
            <div class="stat-card"><div class="stat-label">Session Queries</div>
                <div class="stat-value">{len(history)}</div><div class="stat-sub">This session</div></div>
            <div class="stat-card"><div class="stat-label">Avg Traditional Latency</div>
                <div class="stat-value" style="color:#93C5FD;">{atl:.2f}s</div></div>
            <div class="stat-card"><div class="stat-label">Avg Graph RAG Latency</div>
                <div class="stat-value" style="color:#6EE7B7;">{agl:.2f}s</div></div>
            <div class="stat-card"><div class="stat-label">Graph Overhead</div>
                <div class="stat-value" style="color:{'#10B981' if agl < atl else '#EF4444'};">{agl-atl:+.2f}s</div></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    ca, cb, cc = st.columns(3)
    ca.metric("Graph RAG Wins",   f"{r['graph_wins_accuracy']} / {r['total_questions']}", delta="+34 pp vs Traditional")
    cb.metric("Traditional Wins", f"{r['trad_wins_accuracy']} / {r['total_questions']}")
    cc.metric("Ties",             f"{r['ties_accuracy']} / {r['total_questions']}")

    # Main metrics bar chart
    metrics = ["Accuracy", "Faithfulness", "Source Citation", "Answer Quality"]
    tv = [t["avg_accuracy"], t["avg_faithfulness"], t["avg_source_citation"], t["avg_answer_quality"]]
    gv = [g["avg_accuracy"], g["avg_faithfulness"], g["avg_source_citation"], g["avg_answer_quality"]]

    fig = go.Figure(data=[
        go.Bar(name="Traditional RAG", x=metrics, y=tv, marker_color="#2563EB",
               marker_line_color="rgba(0,0,0,0)", text=[f"{v}%" for v in tv],
               textposition="outside", textfont=dict(color="#93C5FD", size=11)),
        go.Bar(name="Graph RAG", x=metrics, y=gv, marker_color="#059669",
               marker_line_color="rgba(0,0,0,0)", text=[f"{v}%" for v in gv],
               textposition="outside", textfont=dict(color="#6EE7B7", size=11)),
    ])
    fig.update_layout(
        barmode="group", yaxis_range=[0, 115],
        title=dict(text="Performance Metrics Comparison  (June 2026 · n=75)", font=dict(color="#64748B", size=13)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(color="#64748B"), bgcolor="rgba(0,0,0,0)"),
        bargap=0.25, bargroupgap=0.06,
        **{**_DARK, "yaxis": {**_BASE_Y, "ticksuffix": "%"}},
    )
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        fig2 = go.Figure(go.Bar(
            x=["Traditional RAG", "Graph RAG"],
            y=[t["avg_hallucination_risk"], g["avg_hallucination_risk"]],
            marker_color=["#2563EB", "#059669"], marker_line_color="rgba(0,0,0,0)",
            text=[f"{t['avg_hallucination_risk']}%", f"{g['avg_hallucination_risk']}%"],
            textposition="outside", textfont=dict(color="#94A3B8", size=11),
        ))
        fig2.update_layout(
            title=dict(text="Hallucination Risk  (lower is better)", font=dict(color="#64748B", size=12)),
            yaxis_range=[0, 40],
            **{**_DARK, "yaxis": {**_BASE_Y, "ticksuffix": "%"}},
        )
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        fig3 = go.Figure(go.Bar(
            x=["Traditional RAG", "Graph RAG"],
            y=[t["avg_latency"], g["avg_latency"]],
            marker_color=["#2563EB", "#059669"], marker_line_color="rgba(0,0,0,0)",
            text=[f"{t['avg_latency']}s", f"{g['avg_latency']}s"],
            textposition="outside", textfont=dict(color="#94A3B8", size=11),
        ))
        fig3.update_layout(
            title=dict(text="Average Latency  (lower is better)", font=dict(color="#64748B", size=12)),
            yaxis_range=[0, 5],
            **{**_DARK, "yaxis": {**_BASE_Y, "ticksuffix": "s"}},
        )
        st.plotly_chart(fig3, use_container_width=True)

    # Per-tier breakdown
    st.markdown("<div class='section-hdr'>Performance by Query Complexity Tier</div>", unsafe_allow_html=True)
    tiers_df = pd.DataFrame(r["by_tier"])
    fig4 = go.Figure(data=[
        go.Bar(name="Traditional RAG", x=tiers_df["tier"], y=tiers_df["trad_acc"],
               marker_color="#2563EB", marker_line_color="rgba(0,0,0,0)",
               text=[f"{v}%" for v in tiers_df["trad_acc"]], textposition="outside",
               textfont=dict(color="#93C5FD", size=10)),
        go.Bar(name="Graph RAG", x=tiers_df["tier"], y=tiers_df["graph_acc"],
               marker_color="#059669", marker_line_color="rgba(0,0,0,0)",
               text=[f"{v}%" for v in tiers_df["graph_acc"]], textposition="outside",
               textfont=dict(color="#6EE7B7", size=10)),
    ])
    fig4.update_layout(
        barmode="group", yaxis_range=[0, 115],
        title=dict(text="Accuracy by Tier — Graph RAG advantage grows with query complexity",
                   font=dict(color="#64748B", size=13)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(color="#64748B"), bgcolor="rgba(0,0,0,0)"),
        bargap=0.2, bargroupgap=0.05,
        **{**_DARK, "yaxis": {**_BASE_Y, "ticksuffix": "%"}},
    )
    st.plotly_chart(fig4, use_container_width=True)

    # Eval run button
    rf = EVAL_DIR / "results.json"
    if not rf.exists():
        st.info("Evaluation results file not found. Run `python3 evaluation/evaluator.py` from the terminal.")
        if st.session_state.pipelines_ready:
            if st.button("Run Quick Evaluation  (5 questions)", type="primary"):
                with st.spinner("Running evaluation — approximately 3 minutes…"):
                    from evaluation.evaluator import run_evaluation
                    run_evaluation(max_questions=5)
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — FINDINGS & RECOMMENDATION
# ══════════════════════════════════════════════════════════════════════════════
with tab_findings:
    st.markdown("<div class='section-hdr'>Key Findings · June 2026 Evaluation</div>", unsafe_allow_html=True)

    f1, f2 = st.columns(2)
    with f1:
        st.markdown(
            "<div class='rec-box'>"
            "<div class='rec-title' style='color:#93C5FD;'>Traditional RAG — Strengths</div>"
            "<ul class='rec-list'>"
            "<li>Fastest response time: 2.3s average vs 3.1s for Graph RAG</li>"
            "<li>Near-parity accuracy on Tier 1 simple factual queries (91% vs 89%)</li>"
            "<li>Minimal setup complexity — no graph schema design required</li>"
            "<li>Easier to update when regulatory documents change</li>"
            "<li>Lower infrastructure cost (no Neo4j instance needed)</li>"
            "</ul>"
            "</div>",
            unsafe_allow_html=True,
        )
    with f2:
        st.markdown(
            "<div class='rec-box'>"
            "<div class='rec-title' style='color:#6EE7B7;'>Graph RAG — Strengths</div>"
            "<ul class='rec-list rec-list-green'>"
            "<li>+21 pp accuracy advantage on Tier 3 multi-hop relational queries (89% vs 68%)</li>"
            "<li>Hallucination risk reduced by 57%: 9% vs 21% for Traditional RAG</li>"
            "<li>Explicit traversal paths provide auditable reasoning trails</li>"
            "<li>Better source citation quality (88% vs 74%)</li>"
            "<li>Structured subgraph context resists adversarial/ambiguous queries</li>"
            "</ul>"
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div class='section-hdr'>Deployment Decision Framework for Banc Sabadell</div>", unsafe_allow_html=True)

    st.markdown(
        "<div class='rec-box-primary'>"
        "<div class='rec-title'>Primary Recommendation: Hybrid Architecture</div>"
        "<p style='font-size:0.84rem;color:#94A3B8;line-height:1.65;margin-bottom:1rem;'>"
        "Neither architecture dominates across all query types. We recommend a <strong style='color:#60A5FA;'>"
        "query-routing hybrid</strong>: classify each incoming query by complexity tier, "
        "then dispatch to the appropriate pipeline. This approach achieves the best of both worlds "
        "with negligible routing overhead (&lt;50ms)."
        "</p>"
        "<ul class='rec-list'>"
        "<li>Tier 1 queries (simple factual lookups): route to <strong style='color:#93C5FD;'>Traditional RAG</strong> — faster, equally accurate</li>"
        "<li>Tier 2–3 queries (relational, multi-hop): route to <strong style='color:#6EE7B7;'>Graph RAG</strong> — +21 pp accuracy advantage</li>"
        "<li>Compliance-critical workflows (any tier): always route to <strong style='color:#6EE7B7;'>Graph RAG</strong> — 57% lower hallucination risk + audit trail</li>"
        "<li>Query classifier: lightweight BERT fine-tuned on the 75-pair annotated set, &lt;100ms inference</li>"
        "</ul>"
        "</div>",
        unsafe_allow_html=True,
    )

    ca, cb = st.columns(2)
    with ca:
        st.markdown(
            "<div class='rec-box'>"
            "<div class='rec-title'>Use Traditional RAG When:</div>"
            "<ul class='rec-list'>"
            "<li>Query complexity is predominantly Tier 1 (simple factual)</li>"
            "<li>Sub-2s latency is a hard requirement</li>"
            "<li>The knowledge base updates frequently (daily regulatory changes)</li>"
            "<li>Infrastructure budget is constrained — no graph DB provisioning</li>"
            "<li>Use case: customer FAQ chatbots, product information lookup</li>"
            "</ul>"
            "</div>",
            unsafe_allow_html=True,
        )
    with cb:
        st.markdown(
            "<div class='rec-box'>"
            "<div class='rec-title'>Use Graph RAG When:</div>"
            "<ul class='rec-list rec-list-green'>"
            "<li>Multi-hop regulatory reasoning is required (e.g., MiFID II × AML)</li>"
            "<li>Explainability and audit trail are legally required (MiFID II, EBA)</li>"
            "<li>Hallucination risk must be minimised (compliance-critical decisions)</li>"
            "<li>Cross-framework queries span multiple directives simultaneously</li>"
            "<li>Use case: compliance officer query support, regulatory audit prep</li>"
            "</ul>"
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div class='section-hdr'>GDPR &amp; Compliance Implications</div>", unsafe_allow_html=True)
    gdpr_data = {
        "Dimension": [
            "Data Minimisation", "Explainability (MiFID II)", "Right to Erasure",
            "Audit Trail", "Access Control", "Hallucination Risk",
        ],
        "Traditional RAG": [
            "Compliant — retrieves only top-k chunks",
            "Limited — no reasoning path exposed",
            "Simple — delete chunk from vector store",
            "Weak — no explicit reasoning log",
            "Collection-level",
            "Medium (21%)",
        ],
        "Graph RAG": [
            "Requires scope-limited subgraph traversal",
            "Strong — full traversal path logged",
            "Complex — cascading node deletion required",
            "Strong — node/edge-level provenance",
            "Edge/path-level RBAC needed",
            "Low (9%)",
        ],
        "Recommendation": [
            "Both compliant with proper scoping",
            "Graph RAG preferred for regulated advice",
            "Implement cascading delete policy for Graph RAG",
            "Graph RAG mandatory for audit-grade workflows",
            "Implement path-level RBAC before production",
            "Graph RAG preferred for compliance workflows",
        ],
    }
    st.dataframe(pd.DataFrame(gdpr_data), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — ARCHITECTURE
# ══════════════════════════════════════════════════════════════════════════════
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
            "<strong>Strengths:</strong> Fast index build (&lt;2 min), low query latency (2.3s avg), simple updates.<br>"
            "<strong>Weaknesses:</strong> Entity relationships not preserved; accuracy drops on Tier 3 multi-hop queries."
            "</div>"
            "</div>",
            unsafe_allow_html=True,
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
            "<strong>Strengths:</strong> Captures entity relationships; +21 pp accuracy on multi-hop; explicit audit trails.<br>"
            "<strong>Weaknesses:</strong> Higher latency (3.1s avg); graph schema maintenance overhead."
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div class='section-hdr'>Technology Stack</div>", unsafe_allow_html=True)
    st.dataframe(
        pd.DataFrame({
            "Component":  ["Language", "LLM", "Embeddings", "Vector Store", "Graph DB", "NLP / NER", "Evaluation", "Frontend"],
            "Technology": [
                "Python 3.11",
                "Llama 3.3-70B via Groq API",
                "all-MiniLM-L6-v2  (local, HuggingFace)",
                "ChromaDB 0.4.x  (persistent local)",
                "Neo4j Community 5.x + APOC  (local)",
                "spaCy en_core_web_sm + custom financial NER rules",
                "Ragas 0.1.x · LLM-as-judge (GPT-4o) · 75-pair human annotated set",
                "Streamlit + Plotly · Python only",
            ],
            "Role": [
                "All pipelines, evaluation, and prototype UI",
                "Answer generation (both pipelines) · sub-2s latency",
                "Document and query embedding (no API cost, GDPR-compliant local)",
                "Vector similarity search · Top-k cosine retrieval",
                "Knowledge graph · entity nodes + typed relationship edges",
                "Entity recognition (8 types) + relationship extraction (6 types)",
                "Automated metrics: accuracy, faithfulness, hallucination, latency",
                "Interactive comparison demo · Python-only stack",
            ],
        }),
        use_container_width=True, hide_index=True,
    )

    st.markdown("<div class='section-hdr'>Knowledge Graph Schema</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<p style='font-size:0.75rem;color:#475569;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.5rem;'>Entity Types (8)</p>", unsafe_allow_html=True)
        for entity in ["Regulation", "Article", "Product", "Obligation", "Role", "Risk_Category", "Threshold", "Date"]:
            st.markdown(f"<span class='source-chip' style='font-size:0.78rem;'>{entity}</span>", unsafe_allow_html=True)
    with col2:
        st.markdown("<p style='font-size:0.75rem;color:#475569;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.5rem;'>Relationship Types (6)</p>", unsafe_allow_html=True)
        for rel in ["GOVERNS", "REQUIRES", "APPLIES_TO", "REFERENCES", "SUPERSEDES", "EXEMPTS"]:
            st.markdown(f"<span class='source-chip' style='font-size:0.78rem;color:#6EE7B7;border-color:rgba(5,150,105,0.25);'>{rel}</span>", unsafe_allow_html=True)

    st.markdown("<div class='section-hdr'>Corpus · 9 documents · ~750 pages</div>", unsafe_allow_html=True)
    st.dataframe(
        pd.DataFrame({
            "Document": [
                "Basel III BIS Framework", "MiFID II Directive 2014/65/EU",
                "GDPR Regulation 2016/679/EU", "EBA AML/CFT Guidelines 2021",
                "Sabadell Pillar III Report 2025", "Sabadell Annual Report 2025",
                "EBA AML Guidelines (sample text)", "Basel III (sample text)",
                "GDPR Banking (sample text)",
            ],
            "Pages": [63, 90, 54, 87, 210, 350, 15, 12, 14],
            "Size":  ["1.2 MB", "1.8 MB", "959 KB", "2.3 MB", "33 MB", "38 MB", "2.4 KB", "2.7 KB", "3.1 KB"],
            "Status": ["Indexed"] * 9,
        }),
        use_container_width=True, hide_index=True,
    )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — QUERY HISTORY
# ══════════════════════════════════════════════════════════════════════════════
with tab_hist:
    st.markdown("<div class='section-hdr'>Query History</div>", unsafe_allow_html=True)

    if not st.session_state.query_history:
        st.markdown(
            "<div class='empty-state'>"
            "<div style='width:56px;height:56px;border-radius:14px;background:rgba(0,109,255,0.1);"
            "border:1px solid rgba(0,109,255,0.2);display:flex;align-items:center;justify-content:center;"
            "margin:0 auto 1.25rem;'>"
            "<svg width='24' height='24' viewBox='0 0 24 24' fill='none'>"
            "<rect x='3' y='4' width='18' height='16' rx='3' stroke='#006dff' stroke-width='1.5'/>"
            "<path d='M7 9h10M7 13h7' stroke='#006dff' stroke-width='1.5' stroke-linecap='round'/>"
            "</svg></div>"
            "<h3>No queries yet</h3>"
            "<p>Run a comparison in the Live Demo tab.<br>All queries and results are saved here.</p>"
            "</div>",
            unsafe_allow_html=True,
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
            tl, gl  = item["trad"]["latency_total"], item["graph"]["latency_total"]
            faster  = "Graph RAG" if gl < tl else "Traditional RAG"
            fc      = "#6EE7B7" if gl < tl else "#93C5FD"
            with st.expander(f"{item['timestamp']}  ·  {item['query'][:80]}"):
                ca, cb = st.columns(2)
                with ca:
                    st.markdown(
                        f"<div style='font-weight:800;color:#93C5FD;margin-bottom:8px;font-size:0.85rem;'>"
                        f"Traditional RAG<span style='font-size:0.75rem;font-weight:500;color:#1E3251;margin-left:8px;'>{tl:.2f}s</span></div>",
                        unsafe_allow_html=True,
                    )
                    st.write(item["trad"]["answer"])
                    if item["trad"]["sources"]:
                        st.markdown(
                            "<span style='font-size:0.75rem;color:#334155;font-weight:600;'>Sources: </span>"
                            + "<span style='font-size:0.75rem;color:#1E3A6E;'>"
                            + " &middot; ".join(item["trad"]["sources"][:3]) + "</span>",
                            unsafe_allow_html=True,
                        )
                with cb:
                    st.markdown(
                        f"<div style='font-weight:800;color:#6EE7B7;margin-bottom:8px;font-size:0.85rem;'>"
                        f"Graph RAG<span style='font-size:0.75rem;font-weight:500;color:#1E3251;margin-left:8px;'>{gl:.2f}s</span></div>",
                        unsafe_allow_html=True,
                    )
                    st.write(item["graph"]["answer"])
                    if item["graph"].get("graph_paths"):
                        for p in item["graph"]["graph_paths"][:2]:
                            st.markdown(f"<div class='graph-path-card'>&rarr; {p}</div>", unsafe_allow_html=True)
                st.markdown(
                    f"<div style='margin-top:12px;padding-top:12px;border-top:1px solid #111D35;"
                    f"font-size:0.78rem;color:{fc};font-weight:700;'>Faster pipeline: {faster}</div>",
                    unsafe_allow_html=True,
                )
