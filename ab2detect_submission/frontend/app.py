# AB2DETECT - Hallucination Detection System
# Abubakar Khan (1RUA24CSE0010) - Abhishek D Nagoor (1RUA24CSE0009)
# SoCSE, RV University Bengaluru - Summer Internship 2025

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import random
import re
import time
import json
import requests
from datetime import date
from PIL import Image
import io

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
FAVICON_SVG = "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%230F1520'/><circle cx='14' cy='14' r='7' fill='none' stroke='%235B5FEF' stroke-width='2.5'/><line x1='19' y1='19' x2='26' y2='26' stroke='%235B5FEF' stroke-width='2.5' stroke-linecap='round'/><circle cx='14' cy='14' r='3' fill='%23DC3545' opacity='0.85'/></svg>"

st.set_page_config(
    page_title="AB2DETECT — Hallucination Detection",
    page_icon=FAVICON_SVG,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "api_url" not in st.session_state:
    st.session_state.api_url = "http://localhost:8000"
if "shared_hf_token" not in st.session_state:
    st.session_state["shared_hf_token"] = ""

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

:root {
    --ink: #060A10;
    --surface: #0F1520;
    --lift: #181B2E;
    --edge: #1A2535;
    --edge2: #252840;
    --mist: #8892B0;
    --fog: #5C6E82;
    --snow: #EEF2F8;
    --red: #DC3545;
    --red-dim: rgba(220,53,69,0.14);
    --green: #1A7F4B;
    --indigo: #5B5FEF;
    --indigo-dim: rgba(91,95,239,0.12);
    --mono: 'IBM Plex Mono', monospace;
    --sans: 'IBM Plex Sans', sans-serif;
}

html, body, [class*="css"] { font-family: var(--sans); background: var(--ink); color: var(--snow); }
* { box-sizing: border-box; }

/* ── 3D HERO CANVAS ── */
#ab2-hero-canvas {
    position: relative; width: 100%; height: 260px;
    overflow: hidden; border-radius: 8px;
    margin-bottom: 1.5rem;
    background: radial-gradient(ellipse at 60% 40%, rgba(91,95,239,0.18) 0%, transparent 70%),
                radial-gradient(ellipse at 20% 80%, rgba(220,53,69,0.10) 0%, transparent 60%),
                var(--surface);
    border: 1px solid var(--edge);
}
#ab2-hero-canvas canvas { position: absolute; inset: 0; }
.ab2-hero-text {
    position: absolute; inset: 0; display: flex; flex-direction: column;
    align-items: center; justify-content: center; gap: 0.5rem;
    pointer-events: none; z-index: 2;
    text-align: center; padding: 0 1rem;
}
.ab2-hero-title {
    font-family: var(--mono); font-size: 2.8rem; font-weight: 600;
    color: var(--snow); letter-spacing: -0.03em; line-height: 1;
    text-shadow: 0 0 40px rgba(91,95,239,0.6), 0 0 80px rgba(91,95,239,0.25);
    animation: hero-glow 3s ease-in-out infinite alternate;
}
@keyframes hero-glow {
    from { text-shadow: 0 0 30px rgba(91,95,239,0.5), 0 0 60px rgba(91,95,239,0.2); }
    to   { text-shadow: 0 0 60px rgba(91,95,239,0.9), 0 0 120px rgba(91,95,239,0.4), 0 2px 0 rgba(220,53,69,0.3); }
}
.ab2-hero-sub {
    font-family: var(--sans); font-size: 0.92rem; color: var(--mist);
    letter-spacing: 0.04em; text-transform: uppercase;
}
.ab2-hero-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(91,95,239,0.15); border: 1px solid rgba(91,95,239,0.4);
    border-radius: 20px; padding: 4px 14px;
    font-family: var(--mono); font-size: 0.72rem; color: #9EA1F5;
}
.ab2-hero-badge::before {
    content: ''; width: 6px; height: 6px; border-radius: 50%;
    background: #5B5FEF; box-shadow: 0 0 8px #5B5FEF;
    animation: dot-pulse 1.8s ease-in-out infinite;
}
@keyframes dot-pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.5;transform:scale(0.7)} }

/* ── 3D TILE CARDS ── */
.ab2-tile {
    background: var(--surface); border: 1px solid var(--edge); border-radius: 8px;
    padding: 1.2rem 1.4rem; margin-bottom: 1rem;
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    transform-style: preserve-3d; perspective: 800px;
    cursor: default;
}
.ab2-tile:hover {
    transform: translateY(-4px) rotateX(3deg) rotateY(-2deg);
    box-shadow: 0 16px 40px rgba(0,0,0,0.5), 0 0 20px rgba(91,95,239,0.15);
    border-color: rgba(91,95,239,0.45);
}
.ab2-tile-title { font-family: var(--mono); font-weight: 500; font-size: 0.92rem; color: var(--snow); margin-bottom: 0.4rem; }
.ab2-tile-body { font-family: var(--sans); font-size: 0.83rem; color: var(--mist); line-height: 1.65; }

/* ── 3D METRIC CARDS ── */
.ab2-met {
    background: var(--surface); border: 1px solid var(--edge); border-radius: 8px;
    padding: 1.1rem 1.2rem; text-align: left;
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    position: relative; overflow: hidden;
}
.ab2-met::before {
    content: ''; position: absolute; inset: 0;
    background: linear-gradient(135deg, rgba(91,95,239,0.06) 0%, transparent 60%);
    opacity: 0; transition: opacity 0.3s;
}
.ab2-met:hover { transform: translateY(-6px) scale(1.02); border-color: rgba(91,95,239,0.5); box-shadow: 0 20px 50px rgba(0,0,0,0.5), 0 0 30px rgba(91,95,239,0.2); }
.ab2-met:hover::before { opacity: 1; }
.ab2-met-val {
    font-family: var(--mono); font-size: 1.6rem; font-weight: 600; color: var(--snow); display: block;
    background: linear-gradient(135deg, #fff 0%, #9EA1F5 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.ab2-met-lbl { font-family: var(--sans); font-size: 0.8rem; color: var(--fog); margin-top: 2px; }

/* ── 3D PERSON CARDS ── */
.ab2-person {
    background: var(--surface); border: 1px solid var(--edge); border-radius: 8px;
    padding: 1.3rem 1.5rem;
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    position: relative; overflow: hidden;
}
.ab2-person::after {
    content: ''; position: absolute; top: -50%; right: -50%;
    width: 120px; height: 120px; border-radius: 50%;
    background: radial-gradient(circle, rgba(91,95,239,0.12), transparent 70%);
    transition: opacity 0.3s; opacity: 0;
}
.ab2-person:hover { transform: translateY(-5px) rotateY(3deg); box-shadow: 0 18px 45px rgba(0,0,0,0.5), 0 0 25px rgba(91,95,239,0.15); border-color: rgba(91,95,239,0.4); }
.ab2-person:hover::after { opacity: 1; }
.ab2-person-name { font-family: var(--mono); font-weight: 600; font-size: 1rem; color: var(--snow); }
.ab2-person-role { font-family: var(--sans); font-size: 0.82rem; color: var(--fog); margin-top: 3px; }

/* ── FLOATING PARTICLES ── */
.ab2-particle {
    position: fixed; border-radius: 50%; pointer-events: none; z-index: 0;
    animation: float-particle linear infinite;
    opacity: 0;
}
@keyframes float-particle {
    0%   { transform: translateY(100vh) scale(0); opacity: 0; }
    10%  { opacity: 0.6; }
    90%  { opacity: 0.2; }
    100% { transform: translateY(-10vh) scale(1); opacity: 0; }
}

/* ── 3D STEP LIST ── */
.ab2-steps { margin: 0.8rem 0; padding: 0; list-style: none; }
.ab2-step {
    display: flex; gap: 1rem; align-items: flex-start;
    padding: 0.75rem 0.8rem; border-bottom: 1px solid var(--edge);
    border-radius: 4px; margin-bottom: 2px;
    transition: background 0.2s, transform 0.2s;
}
.ab2-step:hover { background: var(--lift); transform: translateX(4px); }
.ab2-step:last-child { border-bottom: none; }
.ab2-step-num { font-family: var(--mono); font-size: 0.78rem; color: var(--indigo); min-width: 2rem; padding-top: 1px; }
.ab2-step-text { font-family: var(--sans); font-size: 0.88rem; color: var(--mist); line-height: 1.6; }

/* ── SCAN LINE EFFECT on answer box ── */
.ab2-answer-box {
    background: var(--ink); border: 1px solid var(--edge);
    border-left: 2.5px solid var(--indigo); border-radius: 4px;
    padding: 1.1rem 1.3rem; font-family: var(--sans); font-size: 0.93rem;
    line-height: 1.8; color: var(--snow); margin: 0.75rem 0;
    position: relative; overflow: hidden;
}
.ab2-answer-box::after {
    content: ''; position: absolute; left: 0; top: -100%;
    width: 100%; height: 2px;
    background: linear-gradient(90deg, transparent, rgba(91,95,239,0.5), transparent);
    animation: scan-line 3s linear infinite;
}
@keyframes scan-line { to { top: 200%; } }

/* ── TERMINAL 3D DEPTH ── */
.ab2-term {
    background: #080C14; border: 1px solid var(--edge); border-radius: 8px;
    padding: 1.1rem 1.3rem; font-family: var(--mono); font-size: 0.83rem;
    line-height: 1.75; color: var(--mist); overflow-x: auto;
    box-shadow: inset 0 2px 20px rgba(0,0,0,0.5), 0 0 0 1px rgba(91,95,239,0.1);
    position: relative;
}
.ab2-term::before {
    content: '● ● ●'; position: absolute; top: 10px; left: 14px;
    font-size: 0.6rem; color: rgba(255,255,255,0.15); letter-spacing: 4px;
}
.ab2-term .t-prompt { color: var(--indigo); }
.ab2-term .t-hall { color: #F4A0A8; text-decoration: underline; }


.skip-link {
    position: fixed; top: -999px; left: 12px;
    background: var(--indigo); color: #fff;
    padding: 8px 16px; border-radius: 4px;
    font-family: var(--mono); font-size: 0.8rem;
    z-index: 9999; text-decoration: none;
}
.skip-link:focus { top: 12px; }

#ab2-scroll {
    position: fixed; top: 0; left: 0;
    height: 2px; width: 0%;
    background: var(--indigo);
    z-index: 9998; transition: width 0.1s linear;
}

#ab2-top {
    position: fixed; bottom: 24px; right: 24px;
    background: var(--lift); border: 1px solid var(--edge2);
    color: var(--mist); font-family: var(--mono); font-size: 0.75rem;
    padding: 8px 14px; border-radius: 4px; cursor: pointer;
    opacity: 0; pointer-events: none; transition: opacity 0.2s;
    z-index: 9000;
}
#ab2-top.vis { opacity: 1; pointer-events: auto; }
#ab2-top:hover { color: var(--snow); border-color: var(--indigo); }

.ab2-toast {
    position: fixed; bottom: 72px; right: 24px;
    background: var(--lift); border: 1px solid var(--edge2);
    color: var(--snow); font-family: var(--mono); font-size: 0.78rem;
    padding: 10px 18px; border-radius: 4px;
    opacity: 0; pointer-events: none; transition: opacity 0.3s;
    z-index: 9000; max-width: 280px;
}
.ab2-toast.show { opacity: 1; }
.ab2-toast.ok { border-left: 3px solid var(--green); }
.ab2-toast.err { border-left: 3px solid var(--red); }

.cookie-bar {
    position: fixed; bottom: 0; left: 0; right: 0;
    background: var(--lift); border-top: 1px solid var(--edge);
    padding: 12px 24px; display: flex; align-items: center; gap: 16px;
    font-family: var(--sans); font-size: 0.82rem; color: var(--mist);
    z-index: 8999;
}
.cookie-bar button {
    background: var(--indigo); color: #fff;
    border: none; border-radius: 4px; padding: 6px 14px;
    font-family: var(--mono); font-size: 0.78rem; cursor: pointer;
}

.main { background: var(--ink); }
.block-container { padding-top: 1.5rem !important; padding-bottom: 3rem !important; max-width: 1140px; }
#ab2-main { outline: none; }

section[data-testid="stSidebar"] { background: var(--surface); border-right: 1px solid var(--edge); }
section[data-testid="stSidebar"] .block-container { padding-top: 1rem !important; }
div[data-testid="stSidebarNav"] { display: none; }

.ab2-h1 { font-family: var(--mono); font-weight: 600; font-size: 1.5rem; color: var(--snow); letter-spacing: -0.02em; margin: 0 0 0.25rem 0; }
.ab2-h2 { font-family: var(--mono); font-weight: 500; font-size: 1.05rem; color: var(--snow); margin: 1.5rem 0 0.75rem 0; }
.ab2-sub { font-family: var(--sans); font-size: 0.88rem; color: var(--mist); margin-bottom: 1.4rem; max-width: 68ch; line-height: 1.6; }
.ab2-rule { border: none; border-top: 1px solid var(--edge); margin: 1.5rem 0; }

.ab2-tile { background: var(--surface); border: 1px solid var(--edge); border-radius: 4px; padding: 1.2rem 1.4rem; margin-bottom: 1rem; transition: border-color 0.15s; }
.ab2-tile:hover { border-color: var(--edge2); }
.ab2-tile-title { font-family: var(--mono); font-weight: 500; font-size: 0.92rem; color: var(--snow); margin-bottom: 0.4rem; }
.ab2-tile-body { font-family: var(--sans); font-size: 0.83rem; color: var(--mist); line-height: 1.65; }

.ab2-met { background: var(--surface); border: 1px solid var(--edge); border-radius: 4px; padding: 1rem 1.2rem; text-align: left; }
.ab2-met-val { font-family: var(--mono); font-size: 1.5rem; font-weight: 600; color: var(--snow); display: block; }
.ab2-met-lbl { font-family: var(--sans); font-size: 0.8rem; color: var(--fog); margin-top: 2px; }

.ab2-answer-box {
    background: var(--ink); border: 1px solid var(--edge);
    border-left: 2.5px solid var(--indigo); border-radius: 4px;
    padding: 1.1rem 1.3rem; font-family: var(--sans); font-size: 0.93rem;
    line-height: 1.8; color: var(--snow); margin: 0.75rem 0;
}

.w-hall {
    background: var(--red-dim); color: #F4A0A8;
    border-bottom: 2px solid var(--red); border-radius: 2px;
    padding: 0 2px; font-weight: 500;
    animation: hall-pulse 2.2s ease-in-out infinite;
}
@keyframes hall-pulse {
    0%, 100% { border-bottom-color: var(--red); }
    50% { border-bottom-color: rgba(220,53,69,0.3); }
}

.ab2-steps { margin: 0.8rem 0; padding: 0; list-style: none; }
.ab2-step { display: flex; gap: 1rem; align-items: flex-start; padding: 0.65rem 0; border-bottom: 1px solid var(--edge); }
.ab2-step:last-child { border-bottom: none; }
.ab2-step-num { font-family: var(--mono); font-size: 0.78rem; color: var(--indigo); min-width: 2rem; padding-top: 1px; }
.ab2-step-text { font-family: var(--sans); font-size: 0.88rem; color: var(--mist); line-height: 1.6; }

.ab2-tag { display: inline-block; background: var(--lift); border: 1px solid var(--edge2); border-radius: 3px; padding: 2px 8px; font-family: var(--mono); font-size: 0.72rem; color: var(--mist); margin: 2px 3px 2px 0; }
.ab2-tag-red { border-color: rgba(220,53,69,0.35); color: #F4A0A8; }
.ab2-tag-green { border-color: rgba(26,127,75,0.4); color: #5FCA8E; }

.ab2-term { background: #080C14; border: 1px solid var(--edge); border-radius: 4px; padding: 1.1rem 1.3rem; font-family: var(--mono); font-size: 0.83rem; line-height: 1.75; color: var(--mist); overflow-x: auto; }
.ab2-term .t-prompt { color: var(--indigo); }
.ab2-term .t-hall { color: #F4A0A8; text-decoration: underline; }

.ab2-person { background: var(--surface); border: 1px solid var(--edge); border-radius: 4px; padding: 1.1rem 1.3rem; }
.ab2-person-name { font-family: var(--mono); font-weight: 600; font-size: 1rem; color: var(--snow); }
.ab2-person-role { font-family: var(--sans); font-size: 0.82rem; color: var(--fog); margin-top: 3px; }

.ab2-footer { border-top: 1px solid var(--edge); padding: 1.2rem 0 0.5rem 0; font-family: var(--mono); font-size: 0.76rem; color: var(--fog); text-align: center; }

div[data-testid="stButton"] button { font-family: var(--mono) !important; background: var(--surface) !important; border: 1px solid var(--edge2) !important; color: var(--mist) !important; border-radius: 3px !important; font-size: 0.85rem !important; transition: all 0.15s !important; }
div[data-testid="stButton"] button:hover { color: var(--snow) !important; border-color: var(--indigo) !important; }
div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea { background: var(--surface) !important; border-color: var(--edge) !important; color: var(--snow) !important; font-family: var(--sans) !important; }
div[data-testid="stSelectbox"] div { background: var(--surface) !important; border-color: var(--edge) !important; color: var(--snow) !important; }
.stSpinner > div { border-top-color: var(--indigo) !important; }
div[data-testid="stExpander"] { background: var(--surface) !important; border: 1px solid var(--edge) !important; border-radius: 4px !important; }

@media (max-width: 768px) {
    .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
    .ab2-h1 { font-size: 1.2rem !important; }
    #ab2-top { bottom: 16px; right: 16px; }
}

@media print {
    section[data-testid="stSidebar"], #ab2-scroll, #ab2-top, .ab2-toast, .cookie-bar { display: none !important; }
    .ab2-answer-box, .ab2-tile { break-inside: avoid; }
    body { background: #fff; color: #000; }
    .ab2-h1, .ab2-h2 { color: #000; }
    .ab2-sub, .ab2-tile-body { color: #333; }
}

@media (prefers-reduced-motion: reduce) {
    * { animation: none !important; transition: none !important; }
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<a href="#ab2-main" class="skip-link">Skip to main content</a>
<div id="ab2-scroll"></div>
<div id="ab2-top" onclick="window.scrollTo({top:0,behavior:'smooth'})">↑ top</div>
<div class="ab2-toast" id="ab2-toast"></div>
<script>
window.addEventListener('scroll', function() {
    var pct = window.scrollY / (document.documentElement.scrollHeight - window.innerHeight) * 100;
    var bar = document.getElementById('ab2-scroll');
    var btn = document.getElementById('ab2-top');
    if(bar) bar.style.width = Math.min(pct,100)+'%';
    if(btn) btn.classList.toggle('vis', window.scrollY > 300);
}, {passive:true});
function ab2Toast(msg, type) {
    var el = document.getElementById('ab2-toast');
    if(!el) return;
    el.textContent = msg;
    el.className = 'ab2-toast show ' + (type||'');
    setTimeout(function(){ el.className = 'ab2-toast'; }, 2800);
}
(function(){
    if(localStorage.getItem('ab2-cookie') === '1') return;
    var bar = document.createElement('div');
    bar.className = 'cookie-bar'; bar.id = 'ab2-cookie-bar';
    bar.innerHTML = '<span>This app uses session storage for detection results only. No personal data is collected or transmitted.</span>' +
        '<button onclick="localStorage.setItem(\'ab2-cookie\',\'1\');document.getElementById(\'ab2-cookie-bar\').remove()">OK</button>';
    document.body.appendChild(bar);
})();
</script>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
PAGES = [
    ("Home",         "Overview & team"),
    ("Detection",    "Ask, model, detect"),
    ("Image",        "OCR + detect"),
    ("Auto-Correct", "Detect and fix"),
    ("Dashboard",    "Model comparison"),
    ("Indian Lang",  "6 Indian languages"),
    ("Cricket",      "Domain dataset"),
    ("Extension",    "Chrome setup"),
    ("FAQ",          "Viva prep"),
]

with st.sidebar:
    st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:1.05rem;font-weight:600;color:#EEF2F8;padding:0.5rem 0 0.1rem 0;letter-spacing:-0.01em">AB2DETECT</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:\'IBM Plex Sans\',sans-serif;font-size:0.74rem;color:#5C6E82;margin-bottom:0.8rem">Hallucination Detection · RV University</div>', unsafe_allow_html=True)

    # ── Global HuggingFace token ──────────────────────────────────────────────
    _tok = st.text_input(
        "🔑 HuggingFace Token",
        value=st.session_state["shared_hf_token"],
        type="password",
        placeholder="hf_…  (enter once, used everywhere)",
        key="sidebar_hf_token",
    )
    if _tok and _tok != st.session_state["shared_hf_token"]:
        st.session_state["shared_hf_token"] = _tok
        st.rerun()
    if st.session_state["shared_hf_token"]:
        st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.72rem;color:#1A7F4B;margin-bottom:0.8rem">✓ Token active — all features unlocked</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.72rem;color:#5C6E82;margin-bottom:0.8rem">Enter token above to enable LLM generation</div>', unsafe_allow_html=True)
    st.markdown("<hr style='border:none;border-top:1px solid #1A2535;margin:0.5rem 0 1rem 0'>", unsafe_allow_html=True)

    for name, sub in PAGES:
        if st.button(f"{name}  —  {sub}", key=f"nav_{name}", use_container_width=True):
            st.session_state.page = name
            st.rerun()

    st.markdown("<hr style='border:none;border-top:1px solid #1A2535;margin:1rem 0'>", unsafe_allow_html=True)

    with st.expander("API settings"):
        api_url = st.text_input("Backend URL", value=st.session_state.api_url)
        if api_url != st.session_state.api_url:
            st.session_state.api_url = api_url
        try:
            r = requests.get(f"{st.session_state.api_url}/health", timeout=1)
            if r.status_code == 200:
                st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.72rem;color:#1A7F4B">backend connected</div>', unsafe_allow_html=True)
        except Exception:
            st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.72rem;color:#5C6E82">backend offline — using simulation</div>', unsafe_allow_html=True)

    st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.7rem;color:#5C6E82;margin-top:0.5rem">SoCSE · Batch 2024–28<br>Summer Internship 2025</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def call_api(endpoint: str, payload: dict):
    """Try the FastAPI backend, fall back to simulation."""
    try:
        r = requests.post(f"{st.session_state.api_url}{endpoint}", json=payload, timeout=5)
        if r.status_code == 200:
            return r.json(), True
    except Exception:
        pass
    return None, False


def simulate_hallucination_detection(context: str, answer: str):
    """
    Deterministic linguistic fallback — NO randomness.
    Flags a span only when there is clear evidence it contradicts the context:
      - Named entity where most tokens are absent from context
      - Number that does NOT appear in context (exact match)
    This avoids false positives like flagging '53' when '53.78' is in context.
    """
    time.sleep(0.2)
    context_lower  = context.lower()
    context_tokens = set(re.findall(r'\b\w+\b', context_lower))
    # Exact numbers in context (including decimals like 53.78)
    ctx_nums = set(re.findall(r'\b\d[\d,\.]*\b', context))
    answer_words = re.findall(r'\S+', answer)
    spans = []

    # 1. Named entities: multi-word proper nouns where >50% tokens absent
    for ent in re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', answer):
        parts = ent.split()
        missing = [p for p in parts if p.lower() not in context_tokens]
        if len(missing) > len(parts) * 0.5:
            spans.append(ent)

    # 2. Single-word proper names absent from context
    for name in re.findall(r'\b[A-Z][a-z]{2,}\b', answer):
        if name.lower() not in context_tokens and name not in spans:
            # Only flag if it looks like a proper noun (capital, not start of sentence)
            idx = answer.find(name)
            if idx > 2:  # not first word of sentence
                spans.append(name)

    # 3. Numbers: flag only if the EXACT number string is not in context
    for num in re.findall(r'\b\d[\d,\.]*\b', answer):
        if num not in ctx_nums:
            spans.append(num)

    spans = list(dict.fromkeys(spans))[:8]
    hall_count = len(spans)
    token_count = len(answer_words)
    return {
        "spans": spans,
        "is_hallucinated": hall_count > 0,
        "confidence": round(max(0.65, min(0.97, 0.97 - hall_count * 0.05)), 4),
        "token_count": token_count,
        "hall_count": hall_count,
        "hall_rate": round(hall_count / max(token_count, 1), 4),
        "sentence_scores": [],
        "method": "linguistic-analysis",
    }


def generate_answer_frontend(context: str, question: str, model_name: str, hf_token: str) -> dict:
    """
    Generate answer directly from HuggingFace Inference API.
    - If context is a real document: answers from context (for Step 2 detection).
    - If context is blank/placeholder: answers from model's own knowledge (Step 1 standalone).
    Falls back to knowledge-base simulation if API unavailable.
    """
    HF_MODELS = {
        "Mistral-7B":  "mistralai/Mistral-7B-Instruct-v0.2",
        "Zephyr-7B":   "HuggingFaceH4/zephyr-7b-beta",
        "Falcon-7B":   "tiiuae/falcon-7b-instruct",
        "LLaMA-2-7B":  "meta-llama/Llama-2-7b-chat-hf",
        "Phi-3-mini":  "microsoft/Phi-3-mini-4k-instruct",
    }
    # These models use the chat/conversational format
    CHAT_MODELS = {"Mistral-7B", "Zephyr-7B", "Phi-3-mini"}

    t0 = time.time()
    model_id = HF_MODELS.get(model_name, HF_MODELS["Mistral-7B"])

    # Decide if this is standalone (Step 1) or context-grounded (Step 2)
    PLACEHOLDER = "Answer based on your general knowledge."
    is_standalone = (not context.strip() or context.strip() == PLACEHOLDER)

    if hf_token and hf_token.startswith("hf_"):
        # ── Build prompt ──────────────────────────────────────────────────────
        if is_standalone:
            # No context: let the model answer from its own knowledge
            if model_name in CHAT_MODELS:
                prompt = f"<s>[INST] {question} [/INST]"
            else:
                prompt = f"Question: {question}\n\nAnswer:"
        else:
            # Context grounded
            if model_name in CHAT_MODELS:
                prompt = (
                    f"<s>[INST] Answer the question using ONLY the context below.\n\n"
                    f"Context: {context}\n\nQuestion: {question} [/INST]"
                )
            else:
                prompt = (
                    f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
                )

        # ── Try HF Inference API ──────────────────────────────────────────────
        hf_error = ""
        for attempt_model_id in [model_id, "HuggingFaceH4/zephyr-7b-beta"]:
            try:
                resp = requests.post(
                    f"https://api-inference.huggingface.co/models/{attempt_model_id}",
                    headers={"Authorization": f"Bearer {hf_token}", "Content-Type": "application/json"},
                    json={
                        "inputs": prompt,
                        "parameters": {
                            "max_new_tokens": 200,
                            "temperature": 0.7,
                            "do_sample": True,
                            "return_full_text": False,
                        },
                        "options": {"wait_for_model": True},
                    },
                    timeout=45,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, list) and data:
                        raw = data[0].get("generated_text", "").strip()
                        # Strip any re-echoed prompt fragments
                        for marker in ["[/INST]", "Answer:", "Answer :"]:
                            if marker in raw:
                                raw = raw.split(marker)[-1].strip()
                        if len(raw) > 15:
                            used_model = model_name if attempt_model_id == model_id else "Zephyr-7B (fallback)"
                            return {
                                "answer": raw,
                                "model_used": used_model,
                                "method": "hf_api",
                                "latency_ms": round((time.time() - t0) * 1000, 1),
                            }
                elif resp.status_code == 503:
                    hf_error = "Model loading (503)"
                    time.sleep(3)  # model cold-starting, brief wait then try fallback model
                    continue
                else:
                    hf_error = f"HTTP {resp.status_code}: {resp.text[:200]}"
                    break
            except requests.Timeout:
                hf_error = "timeout"
                break
            except Exception as e:
                hf_error = str(e)
                break

    # ── Knowledge-base fallback (no token or API failed) ─────────────────────
    # For standalone mode: use a curated knowledge base of common questions
    KNOWLEDGE_BASE = {
        # Geography / world facts
        "eiffel tower": "The Eiffel Tower is 330 metres (1,083 ft) tall, located in Paris, France. It was built between 1887 and 1889 as the entrance arch for the 1889 World's Fair and was designed by Gustave Eiffel.",
        "height eiffel": "The Eiffel Tower stands 330 metres tall including its broadcast antenna. The structure itself is 300 metres.",
        "capital france": "The capital of France is Paris.",
        "capital india": "The capital of India is New Delhi.",
        "capital usa": "The capital of the United States is Washington, D.C.",
        "largest country": "Russia is the largest country in the world by land area, covering approximately 17.1 million square kilometres.",
        "longest river": "The Nile River in Africa is traditionally considered the longest river in the world at approximately 6,650 km.",
        # Science / tech
        "what is ai": "Artificial Intelligence (AI) is the simulation of human intelligence processes by computer systems. It includes machine learning, natural language processing, computer vision, and expert systems. AI systems learn from data to perform tasks such as recognising speech, making decisions, translating languages, and generating text.",
        "what is machine learning": "Machine Learning (ML) is a subset of AI where systems learn from data to improve their performance on tasks without being explicitly programmed. It includes supervised learning, unsupervised learning, and reinforcement learning.",
        "what is deep learning": "Deep learning is a subset of machine learning that uses artificial neural networks with many layers to learn patterns from large amounts of data. It powers image recognition, speech recognition, and large language models.",
        "what is hallucination": "In AI, hallucination refers to when a language model generates confident-sounding text that is factually incorrect or not grounded in the provided context. It is a major reliability concern in LLM-based systems.",
        "what is llm": "A Large Language Model (LLM) is a type of AI model trained on massive text datasets to understand and generate human language. Examples include GPT-4, LLaMA, Mistral, and Gemini.",
        # Cricket / sports
        "sachin tendulkar": "Sachin Tendulkar is widely regarded as one of the greatest cricketers of all time. He scored 15,921 runs in Test cricket across 200 Test matches with an average of 53.78 and 51 centuries.",
        "virat kohli": "Virat Kohli is an Indian cricketer and former captain of the Indian national team. He is one of the leading batsmen in modern cricket with over 8,000 Test runs.",
        "ipl": "The Indian Premier League (IPL) is a professional Twenty20 cricket league in India, held annually. It was founded in 2008 by the BCCI.",
        # History / people
        "mahatma gandhi": "Mahatma Gandhi (1869–1948) was an Indian lawyer and activist who led India's independence movement against British rule through nonviolent civil disobedience. He is known as the Father of the Nation in India.",
        "albert einstein": "Albert Einstein (1879–1955) was a German-born theoretical physicist who developed the theory of relativity and made major contributions to quantum mechanics. He received the Nobel Prize in Physics in 1921.",
        "world war 2": "World War II (1939–1945) was a global conflict involving most of the world's nations. It began with Germany's invasion of Poland and ended with the Allied victory. It remains the deadliest conflict in human history with an estimated 70–85 million casualties.",
    }

    if is_standalone:
        q_lower = question.lower()
        best_answer = None
        best_score = 0
        for key, ans in KNOWLEDGE_BASE.items():
            score = sum(1 for word in key.split() if word in q_lower)
            if score > best_score:
                best_score = score
                best_answer = ans
        if best_answer and best_score > 0:
            return {
                "answer": best_answer,
                "model_used": model_name,
                "method": "knowledge_base_fallback",
                "latency_ms": round((time.time() - t0) * 1000, 1),
            }
        # Generic fallback for unknown questions
        return {
            "answer": (
                f"I don't have enough information to answer '{question}' precisely without a HuggingFace token for real LLM generation. "
                f"Please paste your `hf_` token above to get a real answer from {model_name}. "
                f"Alternatively, in Step 2 you can manually type an answer to check for hallucinations."
            ),
            "model_used": model_name,
            "method": "no_token_fallback",
            "latency_ms": round((time.time() - t0) * 1000, 1),
        }

    # Context-grounded fallback: extract best sentence from context
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', context) if len(s.strip()) > 15]
    if not sentences:
        return {"answer": context[:300], "model_used": model_name,
                "method": "context_extraction", "latency_ms": round((time.time()-t0)*1000,1)}
    q_words = set(re.findall(r'\b\w{4,}\b', question.lower()))
    best, best_score = sentences[0], -1
    for s in sentences:
        score = len(q_words & set(re.findall(r'\b\w{4,}\b', s.lower())))
        if score > best_score:
            best_score, best = score, s
    idx = sentences.index(best)
    answer = best
    if idx + 1 < len(sentences):
        answer = best + " " + sentences[idx + 1]
    return {"answer": answer.strip(), "model_used": model_name,
            "method": "context_extraction", "latency_ms": round((time.time()-t0)*1000,1)}


def run_detection(context, answer):
    api_result, api_ok = call_api("/detect", {"context": context, "question": "", "answer": answer})
    return api_result if api_ok else simulate_hallucination_detection(context, answer)


def highlight_answer(answer: str, spans: list) -> str:
    if not spans:
        return answer
    result = answer
    for span in sorted(spans, key=len, reverse=True):
        result = re.compile(re.escape(span), re.IGNORECASE).sub(
            f'<span class="w-hall">{span}</span>', result)
    return result


def simulate_model_answer(question: str, model_name: str, context: str = "") -> str:
    time.sleep(0.3)
    base = {
        "Mistral-7B": "Mistral's bidirectional analysis indicates the answer aligns with contextual evidence, though some peripheral details may require verification.",
        "Zephyr-7B":  "According to Zephyr's chain-of-thought reasoning, the response draws on retrieved context with high confidence across most spans.",
        "Falcon-7B":  "Falcon's output suggests a factual response based on the given context, though token-level analysis reveals minor unsupported claims.",
        "LLaMA-2-7B": "LLaMA-2 generates this response with 91% context grounding, where most answer tokens correspond directly to retrieved passages.",
    }
    answer = base.get(model_name, "Based on the provided context, the analysis shows relevant patterns that support this conclusion.")
    if context:
        sentences = [s.strip() for s in context.split('.') if len(s.strip()) > 15]
        if sentences:
            answer = sentences[0] + ". " + answer
    return answer


def auto_correct_answer(answer: str, context: str, spans: list) -> str:
    """Replace hallucinated spans with the best context-grounded facts. Returns HTML."""
    if not spans:
        return answer

    # Split context into sentences for targeted search
    ctx_sentences = [s.strip() for s in re.split(r'[.!?]', context) if len(s.strip()) > 5]
    ctx_nums  = re.findall(r'\b\d[\d,\./%]*\b', context)
    ctx_named = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', context)

    def best_replacement(span: str) -> str:
        is_num = bool(re.match(r'^[\d,\.]+$', span.replace(',', '').replace('.', '')))

        if is_num and ctx_nums:
            # Find context sentence nearest to this span's surroundings
            span_pos = answer.lower().find(span.lower())
            window = answer[max(0, span_pos-60):span_pos+60].lower()
            best_sent = max(ctx_sentences, key=lambda s: sum(
                1 for w in window.split() if w in s.lower()
            ), default="")
            nums_in_sent = re.findall(r'\b\d[\d,\./%]*\b', best_sent)
            if nums_in_sent:
                return nums_in_sent[0]
            return ctx_nums[0]

        # Named entity / text span: find context sentence with highest word overlap
        span_words = set(span.lower().split())
        span_pos = answer.lower().find(span.lower())
        window_words = set(answer[max(0, span_pos-80):span_pos+80].lower().split())
        query_words = span_words | window_words

        def sent_score(s):
            s_words = set(s.lower().split())
            return len(s_words & query_words)

        best_sent = max(ctx_sentences, key=sent_score, default="")
        # Extract named entity or number from best sentence
        names_in_sent = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', best_sent)
        nums_in_sent = re.findall(r'\b\d[\d,\./%]*\b', best_sent)

        if names_in_sent:
            return names_in_sent[0]
        if nums_in_sent:
            return nums_in_sent[0]
        if ctx_named:
            return ctx_named[0]
        return "[see context]"

    corrected = answer
    for span in spans:
        replacement = best_replacement(span)
        corrected = re.compile(re.escape(span), re.IGNORECASE).sub(
            f'<span style="color:#5FCA8E;font-weight:600;background:rgba(26,127,75,0.15);'
            f'border-bottom:2px solid #1A7F4B;padding:0 2px;border-radius:2px" '
            f'title="Was: {span}">{replacement}</span>',
            corrected, count=1
        )
    return corrected


def plotly_dark(fig, height=280):
    fig.update_layout(
        paper_bgcolor="#0B1018", plot_bgcolor="#0B1018",
        font=dict(family="IBM Plex Mono, monospace", color="#5C6E82", size=11),
        height=height, margin=dict(t=24, b=16, l=0, r=0),
    )
    fig.update_xaxes(gridcolor="#1A2535", zerolinecolor="#1A2535")
    fig.update_yaxes(gridcolor="#1A2535", zerolinecolor="#1A2535")
    return fig

# ─────────────────────────────────────────────────────────────────────────────
# DATASETS
# ─────────────────────────────────────────────────────────────────────────────
CRICKET_DATA = [
    {"question": "How many Test runs did Sachin Tendulkar score?",
     "context": "Sachin Tendulkar scored 15,921 runs in Test cricket across 200 Test matches with a batting average of 53.78. He made his international debut in 1989 against Pakistan at the age of 16.",
     "correct_answer": "Sachin Tendulkar scored 15,921 runs in 200 Test matches with an average of 53.78, debuting in 1989.",
     "hallucinated_answer": "Sachin Tendulkar scored 18,000 runs in Test cricket across 220 matches with a batting average of 61.5, debuting in 1987.",
     "hallucinated_spans": ["18,000", "220", "61.5", "1987"]},
    {"question": "Who holds the record for most wickets in Test cricket?",
     "context": "Muttiah Muralitharan of Sri Lanka holds the world record for most wickets in Test cricket with 800 wickets from 133 Tests. He retired in 2010.",
     "correct_answer": "Muttiah Muralitharan holds the record with 800 Test wickets from 133 Tests, retiring in 2010.",
     "hallucinated_answer": "Shane Warne holds the record with 850 wickets in 150 Test matches. He retired in 2011.",
     "hallucinated_spans": ["Shane Warne", "850", "150", "2011"]},
    {"question": "When was the first Cricket World Cup held?",
     "context": "The first ICC Cricket World Cup was held in 1975 in England. West Indies won the inaugural tournament by defeating Australia in the final at Lord's Cricket Ground.",
     "correct_answer": "The first Cricket World Cup was held in 1975 in England, won by West Indies who defeated Australia in the final.",
     "hallucinated_answer": "The first Cricket World Cup was held in 1979 in Australia. West Indies won by defeating India in the final at Melbourne.",
     "hallucinated_spans": ["1979", "Australia", "India", "Melbourne"]},
    {"question": "How many ODI centuries has Virat Kohli scored?",
     "context": "As of 2024, Virat Kohli has scored 50 centuries in One Day Internationals, making him the highest century scorer in ODI cricket history, surpassing Sachin Tendulkar's record of 49 ODI centuries.",
     "correct_answer": "Virat Kohli has scored 50 ODI centuries, surpassing Sachin Tendulkar's record of 49 ODI centuries.",
     "hallucinated_answer": "Virat Kohli has scored 55 ODI centuries, surpassing Ricky Ponting's record of 30 ODI centuries.",
     "hallucinated_spans": ["55", "Ricky Ponting", "30"]},
    {"question": "Which team won the 2023 ICC Cricket World Cup?",
     "context": "Australia won the 2023 ICC Cricket World Cup held in India. They defeated India in the final played at Narendra Modi Stadium in Ahmedabad on November 19, 2023. Travis Head was named Player of the Match.",
     "correct_answer": "Australia won the 2023 Cricket World Cup, defeating India in the final at Ahmedabad. Travis Head was Player of the Match.",
     "hallucinated_answer": "India won the 2023 Cricket World Cup, defeating Australia in the final at Mumbai. Virat Kohli was named Player of the Match.",
     "hallucinated_spans": ["India won", "Mumbai", "Virat Kohli"]},
]

INDIAN_LANG_DATA = [
    # ── KANNADA ──
    {"lang": "Kannada", "lang_code": "kn",
     "context": "ಭಾರತದ ರಾಷ್ಟ್ರೀಯ ಹಕ್ಕಿ ನವಿಲು. ಇದು 1963 ರಲ್ಲಿ ರಾಷ್ಟ್ರೀಯ ಹಕ್ಕಿಯಾಗಿ ಘೋಷಿಸಲಾಯಿತು.",
     "question": "ಭಾರತದ ರಾಷ್ಟ್ರೀಯ ಹಕ್ಕಿ ಯಾವುದು?",
     "correct_answer": "ಭಾರತದ ರಾಷ್ಟ್ರೀಯ ಹಕ್ಕಿ ನವಿಲು, ಇದನ್ನು 1963 ರಲ್ಲಿ ಘೋಷಿಸಲಾಯಿತು.",
     "hallucinated_answer": "ಭಾರತದ ರಾಷ್ಟ್ರೀಯ ಹಕ್ಕಿ ಗಿಳಿ, ಇದನ್ನು 1975 ರಲ್ಲಿ ಘೋಷಿಸಲಾಯಿತು.",
     "hallucinated_spans": ["ಗಿಳಿ", "1975"],
     "translation": "India's national bird is the peacock, declared in 1963. Hallucinated: parrot (ಗಿಳಿ), 1975"},
    {"lang": "Kannada", "lang_code": "kn",
     "context": "ಕರ್ನಾಟಕದ ರಾಜಧಾನಿ ಬೆಂಗಳೂರು. ಇದು ಭಾರತದ ಐಟಿ ರಾಜಧಾನಿ ಎಂದು ಕರೆಯಲ್ಪಡುತ್ತದೆ.",
     "question": "ಕರ್ನಾಟಕದ ರಾಜಧಾನಿ ಯಾವುದು?",
     "correct_answer": "ಕರ್ನಾಟಕದ ರಾಜಧಾನಿ ಬೆಂಗಳೂರು, ಇದನ್ನು ಭಾರತದ ಐಟಿ ರಾಜಧಾನಿ ಎನ್ನುತ್ತಾರೆ.",
     "hallucinated_answer": "ಕರ್ನಾಟಕದ ರಾಜಧಾನಿ ಮೈಸೂರು, ಇದನ್ನು ಭಾರತದ ಐಟಿ ರಾಜಧಾನಿ ಎನ್ನುತ್ತಾರೆ.",
     "hallucinated_spans": ["ಮೈಸೂರು"],
     "translation": "Capital of Karnataka is Bengaluru. Hallucinated: Mysuru (ಮೈಸೂರು)"},

    # ── HINDI ──
    {"lang": "Hindi", "lang_code": "hi",
     "context": "भारत की राजधानी नई दिल्ली है। यह 1911 में भारत की राजधानी बनी थी।",
     "question": "भारत की राजधानी कौन सी है?",
     "correct_answer": "भारत की राजधानी नई दिल्ली है, जो 1911 में राजधानी बनी।",
     "hallucinated_answer": "भारत की राजधानी मुंबई है, जो 1947 में राजधानी बनी।",
     "hallucinated_spans": ["मुंबई", "1947"],
     "translation": "India's capital is New Delhi, became capital in 1911. Hallucinated: Mumbai, 1947"},
    {"lang": "Hindi", "lang_code": "hi",
     "context": "महात्मा गांधी का जन्म 2 अक्टूबर 1869 को पोरबंदर, गुजरात में हुआ था।",
     "question": "महात्मा गांधी का जन्म कब हुआ?",
     "correct_answer": "महात्मा गांधी का जन्म 2 अक्टूबर 1869 को पोरबंदर में हुआ था।",
     "hallucinated_answer": "महात्मा गांधी का जन्म 15 अगस्त 1872 को अहमदाबाद में हुआ था।",
     "hallucinated_spans": ["1872", "अहमदाबाद"],
     "translation": "Gandhi born Oct 2 1869 in Porbandar. Hallucinated: 1872, Ahmedabad"},

    # ── TAMIL ──
    {"lang": "Tamil", "lang_code": "ta",
     "context": "தமிழ்நாட்டின் தலைநகரம் சென்னை. இது வங்காள விரிகுடாவின் கரையில் அமைந்துள்ளது.",
     "question": "தமிழ்நாட்டின் தலைநகரம் எது?",
     "correct_answer": "தமிழ்நாட்டின் தலைநகரம் சென்னை, இது வங்காள விரிகுடாவில் உள்ளது.",
     "hallucinated_answer": "தமிழ்நாட்டின் தலைநகரம் மதுரை, இது அரபிக் கடலின் கரையில் உள்ளது.",
     "hallucinated_spans": ["மதுரை", "அரபிக்"],
     "translation": "Capital of Tamil Nadu is Chennai on Bay of Bengal. Hallucinated: Madurai, Arabian Sea"},

    # ── TELUGU ──
    {"lang": "Telugu", "lang_code": "te",
     "context": "ఆంధ్రప్రదేశ్ రాజధాని అమరావతి. ఇది కృష్ణా నది ఒడ్డున నిర్మించబడింది.",
     "question": "ఆంధ్రప్రదేశ్ రాజధాని ఏది?",
     "correct_answer": "ఆంధ్రప్రదేశ్ రాజధాని అమరావతి, కృష్ణా నది ఒడ్డున ఉంది.",
     "hallucinated_answer": "ఆంధ్రప్రదేశ్ రాజధాని విజయవాడ, గోదావరి నది ఒడ్డున నిర్మించబడింది.",
     "hallucinated_spans": ["విజయవాడ", "గోదావరి"],
     "translation": "AP capital is Amaravati on Krishna river. Hallucinated: Vijayawada, Godavari"},

    # ── MARATHI ──
    {"lang": "Marathi", "lang_code": "mr",
     "context": "महाराष्ट्राची राजधानी मुंबई आहे. ती भारतातील सर्वात मोठे शहर आहे.",
     "question": "महाराष्ट्राची राजधानी कोणती आहे?",
     "correct_answer": "महाराष्ट्राची राजधानी मुंबई आहे, जी भारतातील सर्वात मोठे शहर आहे.",
     "hallucinated_answer": "महाराष्ट्राची राजधानी पुणे आहे, जी भारतातील सर्वात मोठे शहर आहे.",
     "hallucinated_spans": ["पुणे"],
     "translation": "Maharashtra capital is Mumbai, largest city in India. Hallucinated: Pune"},

    # ── BENGALI ──
    {"lang": "Bengali", "lang_code": "bn",
     "context": "রবীন্দ্রনাথ ঠাকুর ১৯১৩ সালে সাহিত্যে নোবেল পুরস্কার পান। তিনি প্রথম ভারতীয় নোবেল বিজয়ী।",
     "question": "রবীন্দ্রনাথ ঠাকুর কখন নোবেল পুরস্কার পান?",
     "correct_answer": "রবীন্দ্রনাথ ঠাকুর ১৯১৩ সালে সাহিত্যে নোবেল পুরস্কার পান।",
     "hallucinated_answer": "রবীন্দ্রনাথ ঠাকুর ১৯২০ সালে পদার্থবিজ্ঞানে নোবেল পুরস্কার পান।",
     "hallucinated_spans": ["১৯২০", "পদার্থবিজ্ঞানে"],
     "translation": "Tagore won Nobel in Literature 1913. Hallucinated: 1920, Physics"},
]
# Keep KANNADA_DATA as alias for backward compatibility
KANNADA_DATA = [d for d in INDIAN_LANG_DATA if d["lang"] == "Kannada"]

FAQ_DATA = [
    {"cat": "Basic", "q": "What is a hallucination in the context of LLMs?",
     "a": "A hallucination is when an LLM generates text that is factually incorrect or not supported by the provided context, stated with high confidence. Two types: Intrinsic (contradicts context) and Extrinsic (adds unsupported information)."},
    {"cat": "Basic", "q": "What is RAG (Retrieval-Augmented Generation)?",
     "a": "RAG combines information retrieval with text generation. It retrieves relevant document chunks from a knowledge base and passes them to an LLM along with the user's question. The LLM generates an answer grounded in the retrieved context."},
    {"cat": "Basic", "q": "What is AB2DETECT and what problem does it solve?",
     "a": "AB2DETECT is a span-level hallucination detection system for RAG pipelines built by Abubakar Khan and Abhishek D Nagoor at RV University. It uses ModernBERT to classify every answer token as supported or hallucinated, pinpointing exactly which words are wrong."},
    {"cat": "Basic", "q": "What is token-level classification and why is it important?",
     "a": "Token-level classification assigns label 0 (supported) or label 1 (hallucinated) to every individual token in the answer. It is more precise than sentence-level detection — it pinpoints exactly which words are wrong rather than flagging an entire sentence."},
    {"cat": "Technical", "q": "How is the input formatted for the detection model?",
     "a": "Input is a concatenated sequence: [CLS] context [SEP] question [SEP] answer [SEP]. Only answer tokens receive labels (0 or 1). Context and question tokens are masked with label -100 so they don't contribute to loss or evaluation."},
    {"cat": "Technical", "q": "What optimizer and learning rate does the Trainer use?",
     "a": "The Trainer uses AdamW optimizer with a default learning rate of 1e-5 and 6 epochs. Best model is saved based on hallucinated-class F1 on the validation set. AdamW is preferred for fine-tuning transformers due to correct weight decay implementation."},
    {"cat": "Technical", "q": "What is Flash Attention and why does ModernBERT use it?",
     "a": "Flash Attention is an optimized attention algorithm that reduces memory from O(n²) to O(n) using IO-aware tiling. ModernBERT uses it to enable 4K token context windows efficiently. Without it, processing long [context + question + answer] sequences would be too slow."},
    {"cat": "Technical", "q": "What are Rotary Positional Embeddings (RoPE)?",
     "a": "RoPE encodes position by rotating query and key vectors in attention. Unlike BERT's fixed absolute embeddings (max 512 tokens), RoPE naturally encodes relative distances and can extrapolate to longer sequences. This enables ModernBERT's 4K context window."},
    {"cat": "Models", "q": "What is ModernBERT and how is it different from original BERT?",
     "a": "ModernBERT (2024) is a completely updated encoder with: 4,096 token context (8× BERT's 512), Rotary Positional Embeddings, Flash Attention 2, 2 trillion tokens of training data (125× BERT). Two sizes: base (149M) and large (395M parameters)."},
    {"cat": "Models", "q": "Why use an encoder model instead of a decoder (GPT-style) model?",
     "a": "Hallucination detection is an NLU task, not generation. Encoders have bidirectional attention — each answer token attends to ALL context tokens simultaneously, which is crucial for faithfulness checking. Encoders are also smaller, faster, and cheaper."},
    {"cat": "Dataset", "q": "What is the RAGTruth dataset?",
     "a": "RAGTruth (ACL 2024) is the primary hallucination detection benchmark. It contains outputs from GPT-4, GPT-3.5, LLaMA-2, Mistral across three tasks: Question Answering, Summarization, and Data-to-Text. Human annotators labeled hallucinated spans at word level."},
    {"cat": "Dataset", "q": "What metrics are used to evaluate hallucination detection?",
     "a": "Span-level Precision, Recall, and F1 (primary metric). A predicted span must overlap with a gold span (IoU ≥ 0.5) to count as correct. AUROC is also reported. Span-level F1 is stricter than token-level F1 for user-facing applications."},
    {"cat": "Dataset", "q": "What is the domain gap in medical QA testing?",
     "a": "When applying the detector (trained on RAGTruth) to PubMedQA (medical domain), performance drops ~8-13 F1 points. Root causes: clinical terminology, negation patterns, numerical conventions in medical papers, and citation-heavy writing style."},
    {"cat": "Results", "q": "How does AB2DETECT compare to GPT-4 as a judge?",
     "a": "ModernBERT-base achieves ~68 F1 vs GPT-4's ~61 F1 on RAGTruth, while being 10-60× faster (150ms vs 2-10 seconds) and essentially free (local model vs $0.02/query). ModernBERT-large pushes F1 even higher."},
    {"cat": "Results", "q": "Does lightweight fine-tuning on 24 medical samples help?",
     "a": "Yes — even 24 training samples close ~5-7 of the 12 F1 point domain gap. This works because the base model already has strong hallucination detection capabilities; fine-tuning only needs to learn domain-specific patterns."},
    {"cat": "Tricky", "q": "What happens if the context itself contains incorrect information?",
     "a": "AB2DETECT will NOT flag it. The system checks faithfulness to the retrieved context, not real-world factual correctness. If context says wrong information and the LLM repeats it faithfully, no hallucination is detected. Context quality is handled upstream."},
    {"cat": "Tricky", "q": "Can the detection model be fooled? What are its failure modes?",
     "a": "Known failure modes: adversarial paraphrasing, subtle numerical errors, out-of-domain terminology (medical, legal), very long contexts, correct inferences not verbatim in context (false positives), and clinical negation patterns."},
    {"cat": "Tricky", "q": "Why is this project a valuable independent contribution?",
     "a": "Key contributions: (1) First systematic domain-gap study quantifying RAGTruth→PubMedQA performance drop. (2) Mitigation strategy comparison. (3) Production integration — Streamlit UI, REST API, Chrome extension. (4) Original Cricket and Kannada evaluation datasets."},
    {"cat": "Future", "q": "What are the most promising future research directions?",
     "a": "Multi-domain robustness training, span correction (detect + fix), active learning for annotation, streaming real-time detection, multimodal RAG (image+text), Indian language support, and federated learning for privacy-preserving domain adaptation."},
    {"cat": "Future", "q": "How would you scale AB2DETECT to production?",
     "a": "Deploy ModernBERT behind FastAPI with async batching, add a Redis cache for repeated pairs, expose a WebSocket endpoint for streaming detection, integrate into LangChain as a custom output parser, and containerize with Docker + Kubernetes."},
]

# ─────────────────────────────────────────────────────────────────────────────
# MAIN ANCHOR
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div id="ab2-main" tabindex="-1"></div>', unsafe_allow_html=True)
page = st.session_state.page

# ─────────────────────────────────────────────────────────────────────────────
# HOME
# ─────────────────────────────────────────────────────────────────────────────
if page == "Home":
    # ── 3D ANIMATED HERO (Three.js via components.html — actually executes JS) ─
    components.html("""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background: #0F1520; overflow: hidden; font-family: 'IBM Plex Mono', monospace; }
  canvas { display:block; position:absolute; top:0; left:0; width:100%; height:100%; }
  .hero-text {
    position: absolute; inset: 0;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    gap: 10px; z-index: 10; pointer-events: none;
    text-align: center; padding: 0 20px;
  }
  .hero-title {
    font-size: 3rem; font-weight: 700; letter-spacing: -0.03em;
    color: #EEF2F8; line-height: 1;
    text-shadow: 0 0 40px rgba(91,95,239,0.8), 0 0 80px rgba(91,95,239,0.4);
    animation: glow 3s ease-in-out infinite alternate;
  }
  @keyframes glow {
    from { text-shadow: 0 0 30px rgba(91,95,239,0.6), 0 0 60px rgba(91,95,239,0.25); }
    to   { text-shadow: 0 0 70px rgba(91,95,239,1.0), 0 0 140px rgba(91,95,239,0.5), 0 0 200px rgba(220,53,69,0.2); }
  }
  .hero-sub {
    font-size: 0.78rem; color: #8892B0; letter-spacing: 0.1em;
    text-transform: uppercase;
  }
  .hero-badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(91,95,239,0.15); border: 1px solid rgba(91,95,239,0.45);
    border-radius: 20px; padding: 5px 16px;
    font-size: 0.70rem; color: #9EA1F5;
    animation: badge-pulse 2s ease-in-out infinite;
  }
  @keyframes badge-pulse {
    0%,100% { box-shadow: 0 0 0 rgba(91,95,239,0); }
    50%      { box-shadow: 0 0 16px rgba(91,95,239,0.4); }
  }
  .hero-badge::before {
    content: ''; width: 7px; height: 7px; border-radius: 50%;
    background: #5B5FEF; box-shadow: 0 0 10px #5B5FEF;
    animation: dot 1.8s ease-in-out infinite;
  }
  @keyframes dot { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.4;transform:scale(0.6)} }
</style>
</head>
<body>
<canvas id="c"></canvas>
<div class="hero-text">
  <div class="hero-title">AB2DETECT</div>
  <div class="hero-sub">Span-Level Hallucination Detection &nbsp;·&nbsp; ModernBERT &nbsp;·&nbsp; RAG</div>
  <div class="hero-badge">68.2 F1 on RAGTruth &nbsp;·&nbsp; 10× faster than GPT-4 &nbsp;·&nbsp; ~150ms</div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function() {
  var canvas = document.getElementById('c');
  var W = window.innerWidth, H = window.innerHeight;

  var renderer = new THREE.WebGLRenderer({canvas:canvas, alpha:true, antialias:true});
  renderer.setSize(W,H); renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));

  var scene = new THREE.Scene();
  var camera = new THREE.PerspectiveCamera(60,W/H,0.1,1000);
  camera.position.z = 5;

  // ── Floating token nodes ──
  var nodes = [], nodeMeshes = [];
  var nodeGeom = new THREE.SphereGeometry(0.055,14,14);
  var colors = [0x5B5FEF,0xDC3545,0x1A7F4B,0x9EA1F5,0xF4A0A8,0x5FCA8E];
  for (var i=0; i<65; i++) {
    var mat = new THREE.MeshBasicMaterial({color:colors[i%colors.length],transparent:true,opacity:0.8});
    var mesh = new THREE.Mesh(nodeGeom, mat);
    var pos = {
      x:(Math.random()-0.5)*10, y:(Math.random()-0.5)*5.5, z:(Math.random()-0.5)*4,
      vx:(Math.random()-0.5)*0.007, vy:(Math.random()-0.5)*0.007, vz:(Math.random()-0.5)*0.004,
      phase: Math.random()*Math.PI*2
    };
    mesh.position.set(pos.x,pos.y,pos.z);
    mesh.userData = pos;
    scene.add(mesh); nodes.push(mesh);
  }

  // ── Connection lines ──
  var edges = [];
  var lineMat = new THREE.LineBasicMaterial({color:0x5B5FEF,transparent:true,opacity:0.14});
  for (var j=0; j<nodes.length; j++) {
    for (var k=j+1; k<nodes.length; k++) {
      if (nodes[j].position.distanceTo(nodes[k].position) < 2.4) {
        var lg = new THREE.BufferGeometry().setFromPoints([nodes[j].position.clone(), nodes[k].position.clone()]);
        var line = new THREE.Line(lg, lineMat.clone());
        line.userData = {a:j,b:k};
        scene.add(line); edges.push(line);
      }
    }
  }

  // ── Spinning rings ──
  function ring(r,tube,col,op,rx,rz) {
    var g = new THREE.TorusGeometry(r,tube,10,100);
    var m = new THREE.MeshBasicMaterial({color:col,transparent:true,opacity:op});
    var mesh = new THREE.Mesh(g,m);
    mesh.rotation.x = rx||0; mesh.rotation.z = rz||0;
    scene.add(mesh); return mesh;
  }
  var r1 = ring(1.1,0.013,0x5B5FEF,0.50, Math.PI*0.25,0);
  var r2 = ring(1.7,0.009,0xDC3545,0.28,-Math.PI*0.35,Math.PI*0.1);
  var r3 = ring(2.3,0.006,0x9EA1F5,0.16, Math.PI*0.5, Math.PI*0.2);

  // ── Central sphere (pulsing) ──
  var coreGeom = new THREE.SphereGeometry(0.22,32,32);
  var coreMat  = new THREE.MeshBasicMaterial({color:0x5B5FEF,transparent:true,opacity:0.3});
  var core = new THREE.Mesh(coreGeom, coreMat);
  scene.add(core);

  var t=0;
  function animate() {
    requestAnimationFrame(animate); t+=0.013;

    // Rings
    r1.rotation.y = t*0.42; r1.rotation.z = t*0.14;
    r2.rotation.y =-t*0.27; r2.rotation.x =-Math.PI*0.35+Math.sin(t*0.3)*0.12;
    r3.rotation.y = t*0.18; r3.rotation.z =-t*0.09;

    // Core pulse
    var s = 1+0.18*Math.sin(t*1.5);
    core.scale.set(s,s,s);
    coreMat.opacity = 0.2+0.2*Math.sin(t*1.5);

    // Nodes drift
    nodes.forEach(function(n) {
      var u=n.userData;
      n.position.x += u.vx;
      n.position.y += u.vy + Math.sin(t+u.phase)*0.003;
      n.position.z += u.vz;
      if(Math.abs(n.position.x)>5.5) u.vx*=-1;
      if(Math.abs(n.position.y)>3.0) u.vy*=-1;
      if(Math.abs(n.position.z)>2.5) u.vz*=-1;
      n.material.opacity = 0.35+0.45*Math.abs(Math.sin(t*0.9+u.phase));
    });

    // Edges update
    edges.forEach(function(line) {
      var pa=nodes[line.userData.a].position, pb=nodes[line.userData.b].position;
      var d = pa.distanceTo(pb);
      line.material.opacity = d<2.4 ? (1-d/2.4)*0.22 : 0;
      line.geometry.setFromPoints([pa.clone(),pb.clone()]);
    });

    // Camera drift
    camera.position.x = Math.sin(t*0.07)*0.5;
    camera.position.y = Math.cos(t*0.05)*0.25;
    camera.lookAt(scene.position);
    renderer.render(scene,camera);
  }
  animate();

  window.addEventListener('resize',function(){
    W=window.innerWidth; H=window.innerHeight;
    renderer.setSize(W,H); camera.aspect=W/H; camera.updateProjectionMatrix();
  });
})();
</script>
</body>
</html>
""", height=300)

    # ── Terminal demo ────────────────────────────────────────────────────────
    st.markdown("""
    <div class="ab2-term" style="padding-top:2rem">
    <div><span class="t-prompt">context </span> Australia won the 2023 ICC World Cup at Narendra Modi Stadium. Travis Head was Player of the Match.</div>
    <div style="margin-top:4px"><span class="t-prompt">question</span> Which team won the 2023 Cricket World Cup?</div>
    <div style="margin-top:4px"><span class="t-prompt">answer  </span> <span class="t-hall">India</span> won the 2023 Cricket World Cup, defeating Australia at <span class="t-hall">Mumbai</span>. <span class="t-hall">Virat Kohli</span> was Player of the Match.</div>
    <div style="margin-top:8px;color:#5C6E82;font-size:0.78rem">→ detected: India · Mumbai · Virat Kohli &nbsp;|&nbsp; confidence 0.94 &nbsp;|&nbsp; 3 spans flagged &nbsp;|&nbsp; ~150ms</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    for col, (val, lbl) in zip([c1,c2,c3,c4], [("4","models evaluated"),("68.2","F1 on RAGTruth"),("~150ms","per query"),("20","FAQ answers")]):
        with col:
            st.markdown(f'<div class="ab2-met"><span class="ab2-met-val">{val}</span><div class="ab2-met-lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown('<hr class="ab2-rule">', unsafe_allow_html=True)
    st.markdown('<div class="ab2-h2">What AB2DETECT does</div>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    feats = [
        ("Detection", "Provide context, question, and LLM answer. Token-level classification flags every hallucinated span with red underline highlighting."),
        ("Image OCR", "Upload a document image. EasyOCR extracts the text automatically, which becomes your retrieval context for detection."),
        ("Auto-Correct", "Hallucinated spans are replaced with context-grounded corrections extracted directly from the retrieved passage."),
        ("Dashboard", "Interactive Plotly charts compare F1, precision, recall, latency, and hallucination rate across four open-source models."),
        ("Indian Language", "Detection examples across 6 Indian languages — Kannada, Hindi, Tamil, Telugu, Marathi, Bengali — using multilingual NLI models."),
        ("Cricket Dataset", "Original cricket Q&A dataset with annotated hallucination spans — a custom domain evaluation contribution."),
    ]
    for i, (title, desc) in enumerate(feats):
        with [f1, f2, f3][i % 3]:
            st.markdown(f'<div class="ab2-tile"><div class="ab2-tile-title">{title}</div><div class="ab2-tile-body">{desc}</div></div>', unsafe_allow_html=True)

    st.markdown('<hr class="ab2-rule">', unsafe_allow_html=True)
    st.markdown('<div class="ab2-h2">Project team</div>', unsafe_allow_html=True)
    tc1, tc2 = st.columns(2)
    with tc1:
        st.markdown('<div class="ab2-person"><div class="ab2-person-name">Abubakar Khan</div><div class="ab2-person-role">1RUA24CSE0010 · B.Tech CSE · SoCSE, RV University</div></div>', unsafe_allow_html=True)
    with tc2:
        st.markdown('<div class="ab2-person"><div class="ab2-person-name">Abhishek D Nagoor</div><div class="ab2-person-role">1RUA24CSE0009 · B.Tech CSE · SoCSE, RV University</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="ab2-tile" style="margin-top:1rem"><div class="ab2-tile-title">Faculty Guide</div><div class="ab2-tile-body">Dr. Ramakrishnan Varadharajan · School of Computer Science &amp; Engineering · RV University, Bengaluru</div></div>', unsafe_allow_html=True)

    st.markdown('<hr class="ab2-rule">', unsafe_allow_html=True)
    st.markdown('<div class="ab2-h2">Detection pipeline</div>', unsafe_allow_html=True)
    st.markdown("""
    <ol class="ab2-steps">
    <li class="ab2-step"><span class="ab2-step-num">01</span><span class="ab2-step-text">User provides context passage, question, and LLM-generated answer</span></li>
    <li class="ab2-step"><span class="ab2-step-num">02</span><span class="ab2-step-text">Input concatenated as [CLS] context [SEP] question [SEP] answer [SEP]</span></li>
    <li class="ab2-step"><span class="ab2-step-num">03</span><span class="ab2-step-text">ModernBERT encoder assigns token labels: 0 = supported, 1 = hallucinated</span></li>
    <li class="ab2-step"><span class="ab2-step-num">04</span><span class="ab2-step-text">Contiguous label-1 tokens are grouped into hallucinated spans</span></li>
    <li class="ab2-step"><span class="ab2-step-num">05</span><span class="ab2-step-text">Spans are highlighted in the UI and optionally corrected using context</span></li>
    </ol>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DETECTION  — 3-Step Wizard: Question → Generate → Detect
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Detection":
    st.markdown('<div class="ab2-h1">Hallucination Detection Pipeline</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ab2-sub">Three steps: <b>Ask a question</b> → <b>LLM generates an answer</b> → '
        '<b>Paste context to detect hallucinations</b></div>',
        unsafe_allow_html=True,
    )

    # ── Token warning banner ───────────────────────────────────────────────────
    st.info(
        "⚠️ **HuggingFace Token required for real LLM generation.**  \n"
        "Go to **huggingface.co/settings/tokens** → click **New token** → select **Read** → copy the token.  \n"
        "It must start with **`hf_`** (NOT an AWS key that starts with `HFAK…`).",
        icon="🔑",
    )

    # ── Session state initialisation ──────────────────────────────────────────
    if "det_step" not in st.session_state:
        st.session_state["det_step"] = 1
    if "det_generated_answer" not in st.session_state:
        st.session_state["det_generated_answer"] = ""
    if "det_gen_method" not in st.session_state:
        st.session_state["det_gen_method"] = ""
    if "det_model_name" not in st.session_state:
        st.session_state["det_model_name"] = "Mistral-7B"
    if "det_question" not in st.session_state:
        st.session_state["det_question"] = ""
    if "det_result" not in st.session_state:
        st.session_state["det_result"] = None
    # Token persists across all pages and steps
    if "shared_hf_token" not in st.session_state:
        st.session_state["shared_hf_token"] = ""

    # ── Step indicator ────────────────────────────────────────────────────────
    step = st.session_state["det_step"]
    step_cols = st.columns(3)
    step_labels = ["1️⃣ Ask Question", "2️⃣ Review Answer", "3️⃣ Detect Hallucination"]
    for i, (col, lbl) in enumerate(zip(step_cols, step_labels)):
        active = (i + 1 == step)
        done = (i + 1 < step)
        bg = "#1A7F4B" if done else ("#0A2540" if active else "#1C2A3A")
        border = "2px solid #5FCA8E" if active else ("2px solid #1A7F4B" if done else "2px solid #2A3A4A")
        col.markdown(
            f'<div style="text-align:center;padding:10px;border-radius:8px;background:{bg};border:{border};'
            f'font-size:0.85rem;font-weight:{"700" if active else "400"};color:{"#5FCA8E" if active else "#CDD6F4"}">'
            f'{lbl}</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="ab2-rule">', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════════
    # STEP 1 — Ask a question, choose model, enter HF token, generate answer
    # ════════════════════════════════════════════════════════════════════════════
    if step == 1:
        st.markdown('<div class="ab2-h2">Step 1 — Ask Your Question</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="ab2-tile-body" style="margin-bottom:1rem">Type any question. '
            'The LLM will generate an answer <b>without any context</b> first — '
            'then in Step 2 you provide the real facts so we can detect hallucinations.</div>',
            unsafe_allow_html=True,
        )

        det_question = st.text_input(
            "Your question",
            value=st.session_state.get("det_question", "How many Test runs did Sachin Tendulkar score?"),
            placeholder="e.g. How many Test runs did Sachin Tendulkar score?",
        )

        det_model = st.selectbox(
            "LLM Model",
            ["Mistral-7B", "Zephyr-7B", "Falcon-7B", "LLaMA-2-7B", "Phi-3-mini"],
            index=["Mistral-7B", "Zephyr-7B", "Falcon-7B", "LLaMA-2-7B", "Phi-3-mini"].index(
                st.session_state.get("det_model_name", "Mistral-7B")
            ),
            help="The LLM that will generate an answer to your question",
        )

        det_hf_token = st.text_input(
            "HuggingFace Token (hf_…)",
            value=st.session_state.get("shared_hf_token", ""),
            type="password",
            placeholder="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            help="Get a free token at huggingface.co/settings/tokens → New token → Read",
        )
        # Save token to session so it persists across pages / Start Over
        if det_hf_token:
            st.session_state["shared_hf_token"] = det_hf_token

        # Warn if user pastes wrong key
        if det_hf_token and not det_hf_token.startswith("hf_"):
            st.error(
                f"❌ That doesn't look like a HuggingFace token (yours starts with `{det_hf_token[:4]}…`).  \n"
                "A real HF token starts with **`hf_`**.  \n"
                "Go to **huggingface.co/settings/tokens** → click **New token** (not S3 credentials) → copy the `hf_…` value."
            )

        gen_btn = st.button("🚀 Generate Answer", type="primary", use_container_width=True)

        if gen_btn:
            if not det_question.strip():
                st.warning("Please enter a question first.")
            else:
                # Save inputs to session state
                st.session_state["det_question"] = det_question
                st.session_state["det_model_name"] = det_model
                st.session_state["det_hf_token"] = det_hf_token

                # Generate answer — LLM answers the question from its own knowledge (no context).
                # Passing empty string triggers standalone mode in generate_answer_frontend.
                valid_token = det_hf_token if (det_hf_token and det_hf_token.startswith("hf_")) else ""

                with st.spinner(f"🤖 {det_model} is generating an answer…"):
                    # Try backend first; if offline, call HF directly from frontend
                    gen_ok = False
                    if valid_token:
                        gen_payload = {
                            "context": "",   # empty = standalone, model uses its own knowledge
                            "question": det_question,
                            "model_name": det_model,
                            "hf_token": valid_token,
                        }
                        gen_result, gen_ok = call_api("/generate", gen_payload)

                    if not gen_ok:
                        # Always use frontend HF call directly (works without backend)
                        gen_result = generate_answer_frontend(
                            "",           # empty context = standalone mode
                            det_question,
                            det_model,
                            valid_token,
                        )

                    generated_answer = gen_result.get("answer", "")
                    gen_method = gen_result.get("method", "unknown")

                    # Show what method was used so user understands
                    if gen_method == "hf_api":
                        st.success(f"✅ Answer generated by {det_model} via HuggingFace API")
                    elif gen_method == "knowledge_base_fallback":
                        st.info("ℹ️ Answer from built-in knowledge base (add `hf_` token for real LLM generation)")
                    elif gen_method == "no_token_fallback":
                        st.warning("⚠️ No HF token provided — please add your `hf_` token above for real LLM answers")

                st.session_state["det_generated_answer"] = generated_answer
                st.session_state["det_gen_method"] = gen_method
                st.session_state["det_step"] = 2
                st.rerun()

    # ════════════════════════════════════════════════════════════════════════════
    # STEP 2 — Show generated answer, ask for context document
    # ════════════════════════════════════════════════════════════════════════════
    elif step == 2:
        st.markdown('<div class="ab2-h2">Step 2 — LLM Answer Generated</div>', unsafe_allow_html=True)

        gen_method = st.session_state.get("det_gen_method", "unknown")
        model_name = st.session_state.get("det_model_name", "LLM")
        question_shown = st.session_state.get("det_question", "")

        st.markdown(
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.7rem;color:#5C6E82;margin-bottom:8px">'
            f'question: {question_shown} &nbsp;·&nbsp; model: {model_name} &nbsp;·&nbsp; method: {gen_method}'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Display the generated answer
        generated_answer = st.session_state.get("det_generated_answer", "")
        st.markdown(
            f'<div class="ab2-answer-box" style="margin-bottom:1.5rem">{generated_answer}</div>',
            unsafe_allow_html=True,
        )

        # Allow editing the answer
        edited_answer = st.text_area(
            "✏️ Edit answer if needed (optional)",
            value=generated_answer,
            height=100,
            help="You can modify the generated answer before detection.",
        )

        st.markdown('<div class="ab2-h2" style="margin-top:1.5rem">Now paste your Context Document</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="ab2-tile-body" style="margin-bottom:0.8rem">Paste the real facts / knowledge base passage. '
            'AB2DETECT will compare the LLM answer above against this context to find hallucinations.</div>',
            unsafe_allow_html=True,
        )

        det_context = st.text_area(
            "Context (knowledge base / source document)",
            height=160,
            value="Sachin Tendulkar scored 15,921 runs in Test cricket across 200 Test matches with a batting average of 53.78. He made his international debut in 1989 against Pakistan at the age of 16.",
            placeholder="Paste your retrieval context / ground-truth document here…",
        )

        col_back, col_detect = st.columns([1, 3])
        with col_back:
            if st.button("← Back", use_container_width=True):
                st.session_state["det_step"] = 1
                st.rerun()
        with col_detect:
            detect_btn = st.button("🔍 Detect Hallucinations", type="primary", use_container_width=True)

        if detect_btn:
            if not det_context.strip():
                st.warning("Please paste a context document to compare against.")
            else:
                final_answer = edited_answer.strip() if edited_answer.strip() else generated_answer
                st.session_state["det_generated_answer"] = final_answer
                st.session_state["det_context"] = det_context

                with st.spinner("🔬 Analysing for hallucinations…"):
                    det_payload = {
                        "context": det_context,
                        "question": st.session_state.get("det_question", ""),
                        "answer": final_answer,
                    }
                    det_result, det_ok = call_api("/detect", det_payload)
                    if not det_ok:
                        det_result = simulate_hallucination_detection(det_context, final_answer)
                        det_result["sentence_scores"] = []

                st.session_state["det_result"] = det_result
                st.session_state["det_step"] = 3
                st.rerun()

    # ════════════════════════════════════════════════════════════════════════════
    # STEP 3 — Show detection results
    # ════════════════════════════════════════════════════════════════════════════
    elif step == 3:
        st.markdown('<div class="ab2-h2">Step 3 — Detection Results</div>', unsafe_allow_html=True)

        generated_answer = st.session_state.get("det_generated_answer", "")
        det_result = st.session_state.get("det_result", {})
        model_name = st.session_state.get("det_model_name", "LLM")
        gen_method = st.session_state.get("det_gen_method", "")
        det_context = st.session_state.get("det_context", "")
        question_shown = st.session_state.get("det_question", "")

        method_badge = det_result.get("method", "simulation")
        st.markdown(
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.7rem;color:#5C6E82;margin-bottom:8px">'
            f'question: {question_shown} &nbsp;·&nbsp; model: {model_name} &nbsp;·&nbsp; '
            f'generation: {gen_method} &nbsp;·&nbsp; detection: {method_badge}'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Highlighted answer
        st.markdown('<div class="ab2-h2">Answer with Hallucinations Highlighted</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="ab2-answer-box">{highlight_answer(generated_answer, det_result.get("spans", []))}</div>',
            unsafe_allow_html=True,
        )

        # ── Metrics row ───────────────────────────────────────────────────────
        is_hall = det_result.get("is_hallucinated", False)
        confidence = det_result.get("confidence", 0.0)
        hall_count = det_result.get("hall_count", 0)
        token_count = det_result.get("token_count", 0)
        hall_rate = det_result.get("hall_rate", 0.0)
        spans = det_result.get("spans", [])

        hall_pct = round(hall_rate * 100, 1)
        sc = "#DC3545" if is_hall else "#1A7F4B"
        sv = "HALLUCINATED" if is_hall else "SUPPORTED"

        r1, r2, r3, r4, r5 = st.columns(5)
        with r1:
            st.markdown(f'<div class="ab2-met"><span class="ab2-met-val" style="color:{sc};font-size:1rem">{sv}</span><div class="ab2-met-lbl">verdict</div></div>', unsafe_allow_html=True)
        with r2:
            st.markdown(f'<div class="ab2-met"><span class="ab2-met-val">{confidence:.0%}</span><div class="ab2-met-lbl">confidence</div></div>', unsafe_allow_html=True)
        with r3:
            st.markdown(f'<div class="ab2-met"><span class="ab2-met-val" style="color:#DC3545">{hall_pct}%</span><div class="ab2-met-lbl">hallucinated</div></div>', unsafe_allow_html=True)
        with r4:
            st.markdown(f'<div class="ab2-met"><span class="ab2-met-val">{hall_count}</span><div class="ab2-met-lbl">flagged spans</div></div>', unsafe_allow_html=True)
        with r5:
            st.markdown(f'<div class="ab2-met"><span class="ab2-met-val">{token_count}</span><div class="ab2-met-lbl">total tokens</div></div>', unsafe_allow_html=True)

        # ── Flagged spans ─────────────────────────────────────────────────
        if spans:
            st.markdown('<div class="ab2-h2">Hallucinated Spans</div>', unsafe_allow_html=True)
            tags = " ".join(f'<span class="ab2-tag ab2-tag-red">{s}</span>' for s in spans)
            st.markdown(f'<div style="margin-bottom:1rem">{tags}</div>', unsafe_allow_html=True)
        else:
            st.success("No hallucinations detected — answer is fully grounded in context.")

        # ── Sentence-level breakdown ──────────────────────────────────────
        sentence_scores = det_result.get("sentence_scores", [])
        if sentence_scores:
            st.markdown('<div class="ab2-h2">Sentence-Level Analysis</div>', unsafe_allow_html=True)
            for ss in sentence_scores:
                verdict = ss.get("verdict", "uncertain")
                color = "#DC3545" if verdict == "hallucinated" else ("#1A7F4B" if verdict == "supported" else "#8892B0")
                contra = ss.get("contradiction", 0)
                entail = ss.get("entailment", 0)
                st.markdown(
                    f'<div class="ab2-tile" style="margin-bottom:0.5rem;border-left:3px solid {color}">'
                    f'<div class="ab2-tile-body">{ss["sentence"]}</div>'
                    f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.7rem;color:{color};margin-top:6px">'
                    f'{verdict.upper()} &nbsp;·&nbsp; entailment: {entail:.0%} &nbsp;·&nbsp; contradiction: {contra:.0%}'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )

        # ── Token breakdown table ─────────────────────────────────────────
        with st.expander("Token-level breakdown"):
            rows = [
                {
                    "token": t,
                    "label": 1 if any(s.lower() in t.lower() for s in spans) else 0,
                    "status": "hallucinated" if any(s.lower() in t.lower() for s in spans) else "supported",
                }
                for t in re.findall(r'\S+', generated_answer)
            ]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, height=220)

        # ── Context used ──────────────────────────────────────────────────
        with st.expander("📄 Context document used for detection"):
            st.markdown(
                f'<div class="ab2-tile-body" style="white-space:pre-wrap">{det_context}</div>',
                unsafe_allow_html=True,
            )

        # ── Start over ────────────────────────────────────────────────────
        st.markdown('<hr class="ab2-rule">', unsafe_allow_html=True)
        if st.button("🔄 Start Over — Ask a New Question", use_container_width=True):
            for k in ["det_step", "det_generated_answer", "det_gen_method", "det_model_name",
                      "det_question", "det_result", "det_context", "det_hf_token"]:
                st.session_state.pop(k, None)
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# IMAGE
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Image":
    st.markdown('<div class="ab2-h1">Image Detection</div>', unsafe_allow_html=True)
    st.markdown('<div class="ab2-sub">Upload any image — AB2DETECT extracts colors, themes, objects and text, builds a rich context, generates an LLM answer, then checks for hallucinations.</div>', unsafe_allow_html=True)

    # ── helper: dominant colors via PIL quantization ──────────────────────────
    def describe_colors(pil_img, n=6):
        small = pil_img.convert("RGB").resize((120, 120))
        palette = small.quantize(colors=n).convert("RGB")
        cols = palette.getcolors(120*120)
        if not cols:
            return "various colors"
        cols_sorted = sorted(cols, key=lambda x: -x[0])
        def rgb_name(r, g, b):
            mx = max(r, g, b); mn = min(r, g, b)
            if mx < 60: return "dark/black"
            if mn > 195: return "white/light"
            if mx - mn < 30: return "grey"
            if r > g and r > b: return "red/warm" if g > 80 else "red/dark"
            if g > r and g > b: return "green"
            if b > r and b > g: return "blue/cool"
            if r > 160 and g > 130 and b < 80: return "yellow/golden"
            if r > 160 and g < 100: return "orange/brown"
            return "mixed"
        names = []
        for cnt, (r, g, b) in cols_sorted[:4]:
            nm = rgb_name(r, g, b)
            if nm not in names:
                names.append(nm)
        return ", ".join(names)

    # ── helper: HF vision caption ─────────────────────────────────────────────
    def hf_image_caption(pil_img, token):
        import base64
        buf2 = io.BytesIO()
        pil_img.convert("RGB").save(buf2, format="JPEG", quality=85)
        b64 = base64.b64encode(buf2.getvalue()).decode()
        headers = {"Authorization": f"Bearer {token}"}
        # Try BLIP captioning
        for model in ["Salesforce/blip-image-captioning-large",
                       "Salesforce/blip-image-captioning-base"]:
            try:
                resp = requests.post(
                    f"https://api-inference.huggingface.co/models/{model}",
                    headers=headers,
                    json={"inputs": b64},
                    timeout=20,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, list) and data:
                        return data[0].get("generated_text", ""), model
                    if isinstance(data, dict) and "generated_text" in data:
                        return data["generated_text"], model
            except Exception:
                pass
        return "", ""

    # ── helper: OCR text ─────────────────────────────────────────────────────
    def extract_ocr_text(pil_img):
        try:
            import easyocr
            buf3 = io.BytesIO()
            pil_img.save(buf3, format='PNG')
            reader = easyocr.Reader(['en'], gpu=False)
            return " ".join([r[1] for r in reader.readtext(buf3.getvalue())])
        except Exception:
            return ""

    uploaded = st.file_uploader("Upload image (photo, screenshot, document, chart…)", type=["png","jpg","jpeg","webp"])
    if uploaded:
        img = Image.open(uploaded)
        ci, ct = st.columns([1, 1])
        with ci:
            st.image(img, caption="Uploaded image", use_column_width=True)

        with ct:
            hf_tok = st.session_state.get("shared_hf_token", "")
            if not hf_tok:
                st.warning("Enter your HuggingFace token in the sidebar to enable AI image description.")

            if st.button("🔍 Analyse Image", type="primary", use_container_width=True):
                rich_parts = []

                # 1. Visual description via HF
                with st.spinner("Getting AI visual description…"):
                    if hf_tok:
                        caption, used_model = hf_image_caption(img, hf_tok)
                        if caption:
                            rich_parts.append(f"Visual description: {caption}")
                            st.success(f"Caption ({used_model.split('/')[-1]}): {caption}")
                        else:
                            st.info("Vision API unavailable — using local analysis only.")
                    else:
                        st.info("No token — using local color/size analysis only.")

                # 2. Color palette
                with st.spinner("Analysing colors and layout…"):
                    w, h = img.size
                    color_desc = describe_colors(img)
                    layout = "landscape" if w > h else ("portrait" if h > w else "square")
                    size_desc = f"{w}×{h}px {layout}"
                    rich_parts.append(f"Image dimensions: {size_desc}. Dominant colors: {color_desc}.")

                # 3. OCR text
                with st.spinner("Extracting any text in the image (OCR)…"):
                    ocr_text = extract_ocr_text(img)
                    if ocr_text.strip():
                        rich_parts.append(f"Text found in image: {ocr_text}")
                    else:
                        rich_parts.append("No significant text detected in the image.")

                full_context = " ".join(rich_parts)
                st.session_state["img_context"] = full_context

        # Show context and detection once analysis done
        if "img_context" in st.session_state:
            st.markdown('<hr class="ab2-rule">', unsafe_allow_html=True)
            ctx_edit = st.text_area("📋 Rich image context (edit if needed)", value=st.session_state["img_context"], height=140, key="img_ctx_edit")

            st.markdown('<div class="ab2-h2">Step 2 — Ask a question & check the answer</div>', unsafe_allow_html=True)
            q_img = st.text_input("Your question about the image")
            hf_tok2 = st.session_state.get("shared_hf_token", "")

            if q_img and hf_tok2 and st.button("Generate answer with LLM", use_container_width=True):
                with st.spinner("Generating answer…"):
                    gen_answer = generate_answer_frontend(q_img, ctx_edit, hf_tok2)
                st.session_state["img_gen_answer"] = gen_answer

            a_img = st.text_area("LLM answer to check (auto-filled or paste your own)",
                                  value=st.session_state.get("img_gen_answer", ""), height=100, key="img_answer")

            if st.button("🔬 Run hallucination detection", type="primary"):
                if a_img and ctx_edit:
                    with st.spinner("Detecting…"):
                        result = run_detection(ctx_edit, a_img)
                    sc = "#DC3545" if result["is_hallucinated"] else "#1A7F4B"
                    sv = "Hallucinated" if result["is_hallucinated"] else "Supported"
                    st.markdown(f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.85rem;color:{sc};margin:0.5rem 0">{sv} · confidence {result["confidence"]:.2f} · {result["hall_count"]} spans flagged</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="ab2-answer-box">{highlight_answer(a_img, result["spans"])}</div>', unsafe_allow_html=True)
                else:
                    st.warning("Provide both an image context and an answer to check.")
    else:
        # Clear stale session state when new image not yet uploaded
        st.session_state.pop("img_context", None)
        st.session_state.pop("img_gen_answer", None)
        st.markdown("""<div class="ab2-tile">
        <div class="ab2-tile-title">How it works</div>
        <ol class="ab2-steps" style="margin-top:0.5rem">
        <li class="ab2-step"><span class="ab2-step-num">01</span><span class="ab2-step-text">Upload any PNG/JPG — photo, screenshot, chart, document scan</span></li>
        <li class="ab2-step"><span class="ab2-step-num">02</span><span class="ab2-step-text">AI vision model describes objects, scene, colors, themes</span></li>
        <li class="ab2-step"><span class="ab2-step-num">03</span><span class="ab2-step-text">OCR extracts any text present in the image</span></li>
        <li class="ab2-step"><span class="ab2-step-num">04</span><span class="ab2-step-text">Combined rich description becomes retrieval context</span></li>
        <li class="ab2-step"><span class="ab2-step-num">05</span><span class="ab2-step-text">Ask a question → LLM answers → AB2DETECT checks for hallucinations</span></li>
        </ol></div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# AUTO-CORRECT
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Auto-Correct":
    st.markdown('<div class="ab2-h1">Auto-Correction</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ab2-sub">Three steps: <b>Ask a question</b> → <b>LLM generates answer</b> → '
        '<b>Paste context → detect + auto-correct hallucinations</b></div>',
        unsafe_allow_html=True,
    )

    # ── Session state ─────────────────────────────────────────────────────────
    if "ac_step" not in st.session_state:
        st.session_state["ac_step"] = 1
    if "ac_question" not in st.session_state:
        st.session_state["ac_question"] = ""
    if "ac_model" not in st.session_state:
        st.session_state["ac_model"] = "Mistral-7B"
    if "ac_answer" not in st.session_state:
        st.session_state["ac_answer"] = ""
    if "ac_gen_method" not in st.session_state:
        st.session_state["ac_gen_method"] = ""
    if "ac_result" not in st.session_state:
        st.session_state["ac_result"] = None
    if "ac_corrected" not in st.session_state:
        st.session_state["ac_corrected"] = ""

    ac_step = st.session_state["ac_step"]

    # Step indicator
    ac_step_cols = st.columns(3)
    ac_step_labels = ["1️⃣ Ask Question", "2️⃣ Review Answer", "3️⃣ Auto-Correct"]
    for i, (col, lbl) in enumerate(zip(ac_step_cols, ac_step_labels)):
        active = (i + 1 == ac_step)
        done = (i + 1 < ac_step)
        bg = "#1A7F4B" if done else ("#0A2540" if active else "#1C2A3A")
        border = "2px solid #5FCA8E" if active else ("2px solid #1A7F4B" if done else "2px solid #2A3A4A")
        col.markdown(
            f'<div style="text-align:center;padding:10px;border-radius:8px;background:{bg};border:{border};'
            f'font-size:0.85rem;font-weight:{"700" if active else "400"};color:{"#5FCA8E" if active else "#CDD6F4"}">'
            f'{lbl}</div>', unsafe_allow_html=True,
        )
    st.markdown('<hr class="ab2-rule">', unsafe_allow_html=True)

    # ── STEP 1 ────────────────────────────────────────────────────────────────
    if ac_step == 1:
        st.markdown('<div class="ab2-h2">Step 1 — Ask Your Question</div>', unsafe_allow_html=True)
        ac_question = st.text_input(
            "Your question",
            value=st.session_state.get("ac_question", "Who won the 2023 ICC Cricket World Cup?"),
            placeholder="Ask anything…",
        )
        ac_model = st.selectbox(
            "LLM Model",
            ["Mistral-7B", "Zephyr-7B", "Falcon-7B", "LLaMA-2-7B", "Phi-3-mini"],
            index=["Mistral-7B", "Zephyr-7B", "Falcon-7B", "LLaMA-2-7B", "Phi-3-mini"].index(
                st.session_state.get("ac_model", "Mistral-7B")
            ),
        )
        ac_token = st.text_input(
            "HuggingFace Token (hf_…)",
            value=st.session_state.get("shared_hf_token", ""),
            type="password",
            placeholder="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        )
        if ac_token:
            st.session_state["shared_hf_token"] = ac_token
        if ac_token and not ac_token.startswith("hf_"):
            st.error(f"❌ Token must start with `hf_` (yours starts with `{ac_token[:4]}…`). Get it from huggingface.co/settings/tokens → New token.")

        if st.button("🚀 Generate Answer", type="primary", use_container_width=True):
            if not ac_question.strip():
                st.warning("Please enter a question.")
            else:
                st.session_state["ac_question"] = ac_question
                st.session_state["ac_model"] = ac_model
                valid_token = ac_token if (ac_token and ac_token.startswith("hf_")) else ""
                with st.spinner(f"🤖 {ac_model} generating answer…"):
                    gen_result, gen_ok = call_api("/generate", {
                        "context": "", "question": ac_question,
                        "model_name": ac_model, "hf_token": valid_token or None,
                    })
                    if not gen_ok:
                        gen_result = generate_answer_frontend("", ac_question, ac_model, valid_token)
                st.session_state["ac_answer"] = gen_result.get("answer", "")
                st.session_state["ac_gen_method"] = gen_result.get("method", "unknown")
                if gen_result.get("method") == "hf_api":
                    st.success(f"✅ Answer generated by {ac_model} via HuggingFace API")
                st.session_state["ac_step"] = 2
                st.rerun()

    # ── STEP 2 ────────────────────────────────────────────────────────────────
    elif ac_step == 2:
        st.markdown('<div class="ab2-h2">Step 2 — Review Answer & Paste Context</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.7rem;color:#5C6E82;margin-bottom:8px">'
            f'question: {st.session_state["ac_question"]} &nbsp;·&nbsp; model: {st.session_state["ac_model"]} &nbsp;·&nbsp; method: {st.session_state["ac_gen_method"]}'
            f'</div>', unsafe_allow_html=True,
        )
        st.markdown(f'<div class="ab2-answer-box" style="margin-bottom:1rem">{st.session_state["ac_answer"]}</div>', unsafe_allow_html=True)

        edited_ac = st.text_area("✏️ Edit answer if needed (optional)", value=st.session_state["ac_answer"], height=90)

        st.markdown('<div class="ab2-h2" style="margin-top:1rem">Paste Context Document</div>', unsafe_allow_html=True)
        st.markdown('<div class="ab2-tile-body" style="margin-bottom:0.8rem">Paste the real ground-truth facts. AB2DETECT will detect hallucinations, then auto-correct them.</div>', unsafe_allow_html=True)

        ac_context = st.text_area(
            "Context (ground truth / knowledge base)",
            height=140,
            value="Australia won the 2023 ICC Cricket World Cup held in India. They defeated India in the final played at Narendra Modi Stadium in Ahmedabad on November 19, 2023. Travis Head was named Player of the Match.",
            placeholder="Paste the real facts here…",
        )
        col_b, col_d = st.columns([1, 3])
        with col_b:
            if st.button("← Back", use_container_width=True):
                st.session_state["ac_step"] = 1
                st.rerun()
        with col_d:
            if st.button("🔍 Detect & Auto-Correct", type="primary", use_container_width=True):
                if not ac_context.strip():
                    st.warning("Please paste a context document.")
                else:
                    final_ans = edited_ac.strip() if edited_ac.strip() else st.session_state["ac_answer"]
                    st.session_state["ac_answer"] = final_ans
                    st.session_state["ac_context"] = ac_context
                    with st.spinner("🔬 Detecting hallucinations…"):
                        det_result, det_ok = call_api("/detect", {"context": ac_context, "question": st.session_state["ac_question"], "answer": final_ans})
                        if not det_ok:
                            det_result = simulate_hallucination_detection(ac_context, final_ans)
                            det_result["sentence_scores"] = []
                    corrected = auto_correct_answer(final_ans, ac_context, det_result["spans"])
                    st.session_state["ac_result"] = det_result
                    st.session_state["ac_corrected"] = corrected
                    st.session_state["ac_step"] = 3
                    st.rerun()

    # ── STEP 3 ────────────────────────────────────────────────────────────────
    elif ac_step == 3:
        st.markdown('<div class="ab2-h2">Step 3 — Detection & Auto-Correction Results</div>', unsafe_allow_html=True)
        det_result = st.session_state["ac_result"]
        spans = det_result.get("spans", [])
        ac_answer = st.session_state["ac_answer"]
        ac_corrected = st.session_state["ac_corrected"]

        st.markdown(
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.7rem;color:#5C6E82;margin-bottom:12px">'
            f'question: {st.session_state["ac_question"]} &nbsp;·&nbsp; model: {st.session_state["ac_model"]} &nbsp;·&nbsp; '
            f'{len(spans)} hallucinated span(s) detected &nbsp;·&nbsp; detection: {det_result.get("method","simulation")}'
            f'</div>', unsafe_allow_html=True,
        )

        co, cc = st.columns(2)
        with co:
            st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.72rem;color:#DC3545;margin-bottom:4px">❌ original (hallucinations highlighted)</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="ab2-answer-box">{highlight_answer(ac_answer, spans)}</div>', unsafe_allow_html=True)
        with cc:
            st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.72rem;color:#1A7F4B;margin-bottom:4px">✅ auto-corrected (grounded in context)</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="ab2-answer-box" style="border-left-color:#1A7F4B">{ac_corrected}</div>', unsafe_allow_html=True)

        # Metrics
        hall_pct = round(det_result.get("hall_rate", 0) * 100, 1)
        sc = "#DC3545" if det_result.get("is_hallucinated") else "#1A7F4B"
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.markdown(f'<div class="ab2-met"><span class="ab2-met-val" style="color:{sc}">{"HALLUCINATED" if det_result.get("is_hallucinated") else "SUPPORTED"}</span><div class="ab2-met-lbl">verdict</div></div>', unsafe_allow_html=True)
        with m2: st.markdown(f'<div class="ab2-met"><span class="ab2-met-val" style="color:#DC3545">{hall_pct}%</span><div class="ab2-met-lbl">hallucinated</div></div>', unsafe_allow_html=True)
        with m3: st.markdown(f'<div class="ab2-met"><span class="ab2-met-val">{len(spans)}</span><div class="ab2-met-lbl">spans corrected</div></div>', unsafe_allow_html=True)
        with m4: st.markdown(f'<div class="ab2-met"><span class="ab2-met-val">{det_result.get("confidence",0):.0%}</span><div class="ab2-met-lbl">confidence</div></div>', unsafe_allow_html=True)

        if spans:
            st.markdown('<div class="ab2-h2" style="margin-top:0.5rem">Corrected Spans</div>', unsafe_allow_html=True)
            tags = " ".join(f'<span class="ab2-tag ab2-tag-red">{s}</span>' for s in spans)
            st.markdown(f'<div style="margin-bottom:1rem">{tags}</div>', unsafe_allow_html=True)
        else:
            st.success("No hallucinations detected — answer is fully grounded in context.")

        st.markdown('<hr class="ab2-rule">', unsafe_allow_html=True)
        if st.button("🔄 Start Over — Ask a New Question", use_container_width=True):
            for k in ["ac_step","ac_question","ac_model","ac_answer","ac_gen_method","ac_result","ac_corrected","ac_context"]:
                st.session_state.pop(k, None)
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Dashboard":
    st.markdown('<div class="ab2-h1">Model Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="ab2-sub">Hallucination metrics across four open-source models on the RAGTruth benchmark.</div>', unsafe_allow_html=True)

    models = ["Mistral-7B", "Zephyr-7B", "Falcon-7B", "LLaMA-2-7B"]
    f1 = [68.2, 61.4, 54.8, 58.6]
    prec = [72.1, 64.8, 58.3, 62.4]
    rec  = [64.6, 58.2, 51.6, 55.1]
    lat  = [148, 162, 195, 178]
    hrate= [0.12, 0.18, 0.24, 0.21]

    m1, m2, m3 = st.columns(3)
    with m1: st.markdown('<div class="ab2-met"><span class="ab2-met-val">Mistral-7B</span><div class="ab2-met-lbl">top model by F1</div></div>', unsafe_allow_html=True)
    with m2: st.markdown('<div class="ab2-met"><span class="ab2-met-val">68.2</span><div class="ab2-met-lbl">best F1 score</div></div>', unsafe_allow_html=True)
    with m3: st.markdown('<div class="ab2-met"><span class="ab2-met-val">148ms</span><div class="ab2-met-lbl">fastest latency</div></div>', unsafe_allow_html=True)
    st.markdown('<hr class="ab2-rule">', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        fig.add_trace(go.Bar(name="F1", x=models, y=f1, marker_color="#5B5FEF"))
        fig.add_trace(go.Bar(name="Precision", x=models, y=prec, marker_color="#1A7F4B"))
        fig.add_trace(go.Bar(name="Recall", x=models, y=rec, marker_color="#DC3545"))
        fig.update_layout(barmode="group", title="F1 / Precision / Recall")
        st.plotly_chart(plotly_dark(fig), use_container_width=True)
    with c2:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=models, y=lat, marker_color="#8892B0",
                              text=[f"{v}ms" for v in lat], textposition="outside"))
        fig2.update_layout(title="Inference latency (ms)")
        st.plotly_chart(plotly_dark(fig2), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig3 = go.Figure(go.Scatter(x=models, y=hrate, mode="lines+markers",
            line=dict(color="#5B5FEF", width=2), marker=dict(color="#DC3545", size=8)))
        fig3.update_layout(title="Hallucination rate per model")
        st.plotly_chart(plotly_dark(fig3), use_container_width=True)
    with c4:
        cats = ["QA", "Summarization", "Data-to-Text"]
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(name="Mistral", x=cats, y=[71.2, 66.8, 66.6], marker_color="#5B5FEF"))
        fig4.add_trace(go.Bar(name="Zephyr",  x=cats, y=[63.1, 60.4, 60.7], marker_color="#1A7F4B"))
        fig4.update_layout(barmode="group", title="F1 by RAGTruth task type")
        st.plotly_chart(plotly_dark(fig4), use_container_width=True)

    st.markdown('<hr class="ab2-rule">', unsafe_allow_html=True)
    df = pd.DataFrame({"Model": models, "F1": f1, "Precision": prec, "Recall": rec,
                        "Latency (ms)": lat, "Hall. Rate": hrate})
    st.dataframe(df.set_index("Model"), use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# INDIAN LANG
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Indian Lang":
    st.markdown('<div class="ab2-h1">Indian Language Detection</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ab2-sub">Three steps: <b>Ask a question in any Indian language</b> → <b>LLM generates answer</b> → '
        '<b>Paste context → detect hallucinations</b>. Supports Kannada, Hindi, Tamil, Telugu, Marathi, Bengali.</div>',
        unsafe_allow_html=True,
    )

    # ── Session state ─────────────────────────────────────────────────────────
    if "il_step" not in st.session_state:
        st.session_state["il_step"] = 1
    if "il_question" not in st.session_state:
        st.session_state["il_question"] = ""
    if "il_lang" not in st.session_state:
        st.session_state["il_lang"] = "Kannada"
    if "il_model" not in st.session_state:
        st.session_state["il_model"] = "Mistral-7B"
    if "il_answer" not in st.session_state:
        st.session_state["il_answer"] = ""
    if "il_gen_method" not in st.session_state:
        st.session_state["il_gen_method"] = ""
    if "il_result" not in st.session_state:
        st.session_state["il_result"] = None

    il_step = st.session_state["il_step"]

    # Step indicator
    il_cols = st.columns(3)
    il_labels = ["1️⃣ Ask Question", "2️⃣ Review Answer", "3️⃣ Detect Hallucination"]
    for i, (col, lbl) in enumerate(zip(il_cols, il_labels)):
        active = (i + 1 == il_step)
        done = (i + 1 < il_step)
        bg = "#1A7F4B" if done else ("#0A2540" if active else "#1C2A3A")
        border = "2px solid #5FCA8E" if active else ("2px solid #1A7F4B" if done else "2px solid #2A3A4A")
        col.markdown(
            f'<div style="text-align:center;padding:10px;border-radius:8px;background:{bg};border:{border};'
            f'font-size:0.85rem;font-weight:{"700" if active else "400"};color:{"#5FCA8E" if active else "#CDD6F4"}">'
            f'{lbl}</div>', unsafe_allow_html=True,
        )
    st.markdown('<hr class="ab2-rule">', unsafe_allow_html=True)

    # Sample questions per language for convenience
    LANG_SAMPLES = {
        "Kannada": "ಸಚಿನ್ ತೆಂಡೂಲ್ಕರ್ ಎಷ್ಟು ಟೆಸ್ಟ್ ರನ್ ಗಳಿಸಿದ್ದಾರೆ?",
        "Hindi":   "भारत की राजधानी क्या है?",
        "Tamil":   "2023 ICC உலகக் கோப்பையை யார் வென்றனர்?",
        "Telugu":  "సచిన్ టెండూల్కర్ ఎన్ని టెస్ట్ రన్లు చేశారు?",
        "Marathi": "2023 ICC विश्वचषक कोणी जिंकला?",
        "Bengali": "সাচিন টেন্ডুলকার কত টেস্ট রান করেছেন?",
    }

    # ── STEP 1 ────────────────────────────────────────────────────────────────
    if il_step == 1:
        st.markdown('<div class="ab2-h2">Step 1 — Ask Your Question</div>', unsafe_allow_html=True)

        il_lang = st.selectbox(
            "Language",
            ["Kannada", "Hindi", "Tamil", "Telugu", "Marathi", "Bengali"],
            index=["Kannada", "Hindi", "Tamil", "Telugu", "Marathi", "Bengali"].index(
                st.session_state.get("il_lang", "Kannada")
            ),
        )
        sample_q = LANG_SAMPLES.get(il_lang, "")
        st.markdown(f'<div class="ab2-tile-body" style="margin-bottom:0.5rem">Sample question in {il_lang}: <em>{sample_q}</em></div>', unsafe_allow_html=True)

        il_question = st.text_input(
            f"Your question (in {il_lang} or English)",
            value=st.session_state.get("il_question", sample_q),
            placeholder=sample_q,
        )
        il_model = st.selectbox(
            "LLM Model",
            ["Mistral-7B", "Zephyr-7B", "Falcon-7B", "LLaMA-2-7B", "Phi-3-mini"],
            index=["Mistral-7B", "Zephyr-7B", "Falcon-7B", "LLaMA-2-7B", "Phi-3-mini"].index(
                st.session_state.get("il_model", "Mistral-7B")
            ),
        )
        il_token = st.text_input(
            "HuggingFace Token (hf_…)",
            value=st.session_state.get("shared_hf_token", ""),
            type="password",
            placeholder="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        )
        if il_token:
            st.session_state["shared_hf_token"] = il_token
        if il_token and not il_token.startswith("hf_"):
            st.error(f"❌ Token must start with `hf_` (yours starts with `{il_token[:4]}…`).")

        if st.button("🚀 Generate Answer", type="primary", use_container_width=True):
            if not il_question.strip():
                st.warning("Please enter a question.")
            else:
                st.session_state["il_question"] = il_question
                st.session_state["il_lang"] = il_lang
                st.session_state["il_model"] = il_model
                valid_token = il_token if (il_token and il_token.startswith("hf_")) else ""
                with st.spinner(f"🤖 {il_model} generating answer…"):
                    gen_result, gen_ok = call_api("/generate", {
                        "context": "", "question": il_question,
                        "model_name": il_model, "hf_token": valid_token or None,
                    })
                    if not gen_ok:
                        gen_result = generate_answer_frontend("", il_question, il_model, valid_token)
                st.session_state["il_answer"] = gen_result.get("answer", "")
                st.session_state["il_gen_method"] = gen_result.get("method", "unknown")
                if gen_result.get("method") == "hf_api":
                    st.success(f"✅ Answer generated by {il_model} via HuggingFace API")
                st.session_state["il_step"] = 2
                st.rerun()

    # ── STEP 2 ────────────────────────────────────────────────────────────────
    elif il_step == 2:
        st.markdown('<div class="ab2-h2">Step 2 — LLM Answer Generated</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.7rem;color:#5C6E82;margin-bottom:8px">'
            f'lang: {st.session_state["il_lang"]} &nbsp;·&nbsp; question: {st.session_state["il_question"]} &nbsp;·&nbsp; '
            f'model: {st.session_state["il_model"]} &nbsp;·&nbsp; method: {st.session_state["il_gen_method"]}'
            f'</div>', unsafe_allow_html=True,
        )
        st.markdown(f'<div class="ab2-answer-box" style="margin-bottom:1rem">{st.session_state["il_answer"]}</div>', unsafe_allow_html=True)

        edited_il = st.text_area("✏️ Edit answer if needed (optional)", value=st.session_state["il_answer"], height=90)

        st.markdown('<div class="ab2-h2" style="margin-top:1rem">Paste Context Document</div>', unsafe_allow_html=True)
        lang = st.session_state["il_lang"]
        LANG_CONTEXT_SAMPLES = {
            "Kannada": "ಸಚಿನ್ ತೆಂಡೂಲ್ಕರ್ 200 ಟೆಸ್ಟ್ ಪಂದ್ಯಗಳಲ್ಲಿ 15,921 ರನ್ ಗಳಿಸಿದ್ದಾರೆ, ಸರಾಸರಿ 53.78.",
            "Hindi":   "भारत की राजधानी नई दिल्ली है। यह देश के उत्तरी भाग में स्थित है।",
            "Tamil":   "2023 ICC உலகக் கோப்பையில் ஆஸ்திரேலியா இந்தியாவை இறுதியில் தோற்கடித்து வென்றது. டிராவிஸ் ஹெட் மேட்ச் ஆஃப் தி மேட்ச் விருது பெற்றார்.",
            "Telugu":  "సచిన్ టెండూల్కర్ 200 టెస్ట్ మ్యాచ్‌లలో 15,921 రన్లు చేశారు, సగటు 53.78.",
            "Marathi": "2023 ICC विश्वचषक ऑस्ट्रेलियाने भारताला फायनलमध्ये हरवून जिंकला. ट्रॅव्हिस हेड सामनावीर ठरला.",
            "Bengali": "সাচিন টেন্ডুলকার ২০০ টেস্ট ম্যাচে ১৫,৯২১ রান করেছেন, গড় ৫৩.৭৮।",
        }
        il_context = st.text_area(
            f"Context in {lang} (knowledge base / source)",
            height=150,
            value=LANG_CONTEXT_SAMPLES.get(lang, ""),
            placeholder=f"Paste the ground-truth context in {lang} here…",
        )
        col_b, col_d = st.columns([1, 3])
        with col_b:
            if st.button("← Back", use_container_width=True):
                st.session_state["il_step"] = 1
                st.rerun()
        with col_d:
            if st.button("🔍 Detect Hallucinations", type="primary", use_container_width=True):
                if not il_context.strip():
                    st.warning("Please paste a context document.")
                else:
                    final_ans = edited_il.strip() if edited_il.strip() else st.session_state["il_answer"]
                    st.session_state["il_answer"] = final_ans
                    st.session_state["il_context"] = il_context
                    with st.spinner("🔬 Detecting hallucinations…"):
                        det_result, det_ok = call_api("/detect", {
                            "context": il_context,
                            "question": st.session_state["il_question"],
                            "answer": final_ans,
                        })
                        if not det_ok:
                            det_result = simulate_hallucination_detection(il_context, final_ans)
                            det_result["sentence_scores"] = []
                    st.session_state["il_result"] = det_result
                    st.session_state["il_step"] = 3
                    st.rerun()

    # ── STEP 3 ────────────────────────────────────────────────────────────────
    elif il_step == 3:
        st.markdown('<div class="ab2-h2">Step 3 — Detection Results</div>', unsafe_allow_html=True)
        det_result = st.session_state["il_result"]
        spans = det_result.get("spans", [])
        il_answer = st.session_state["il_answer"]
        lang = st.session_state["il_lang"]

        st.markdown(
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.7rem;color:#5C6E82;margin-bottom:12px">'
            f'lang: {lang} &nbsp;·&nbsp; model: {st.session_state["il_model"]} &nbsp;·&nbsp; '
            f'method: {det_result.get("method","simulation")} &nbsp;·&nbsp; '
            f'{len(spans)} hallucinated span(s)'
            f'</div>', unsafe_allow_html=True,
        )

        # Highlighted answer
        st.markdown('<div class="ab2-h2">Answer with Hallucinations Highlighted</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="ab2-answer-box">{highlight_answer(il_answer, spans)}</div>',
            unsafe_allow_html=True,
        )

        # Metrics
        is_hall = det_result.get("is_hallucinated", False)
        hall_pct = round(det_result.get("hall_rate", 0) * 100, 1)
        sc = "#DC3545" if is_hall else "#1A7F4B"
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.markdown(f'<div class="ab2-met"><span class="ab2-met-val" style="color:{sc}">{"HALLUCINATED" if is_hall else "SUPPORTED"}</span><div class="ab2-met-lbl">verdict</div></div>', unsafe_allow_html=True)
        with m2: st.markdown(f'<div class="ab2-met"><span class="ab2-met-val" style="color:#DC3545">{hall_pct}%</span><div class="ab2-met-lbl">hallucinated</div></div>', unsafe_allow_html=True)
        with m3: st.markdown(f'<div class="ab2-met"><span class="ab2-met-val">{len(spans)}</span><div class="ab2-met-lbl">flagged spans</div></div>', unsafe_allow_html=True)
        with m4: st.markdown(f'<div class="ab2-met"><span class="ab2-met-val">{det_result.get("confidence",0):.0%}</span><div class="ab2-met-lbl">confidence</div></div>', unsafe_allow_html=True)

        if spans:
            st.markdown('<div class="ab2-h2">Hallucinated Spans</div>', unsafe_allow_html=True)
            tags = " ".join(f'<span class="ab2-tag ab2-tag-red">{s}</span>' for s in spans)
            st.markdown(f'<div style="margin-bottom:1rem">{tags}</div>', unsafe_allow_html=True)
        else:
            st.success("No hallucinations detected — answer is fully grounded in context.")

        # Show the pre-annotated examples for this language below
        st.markdown('<hr class="ab2-rule">', unsafe_allow_html=True)
        st.markdown(f'<div class="ab2-h2">Annotated Examples — {lang}</div>', unsafe_allow_html=True)
        lang_examples = [d for d in INDIAN_LANG_DATA if d["lang"] == lang]
        if lang_examples:
            for item in lang_examples:
                with st.expander(f'📖 {item["question"]}'):
                    st.markdown(f'<div class="ab2-tile"><div class="ab2-tile-title">Context</div><div class="ab2-tile-body">{item["context"]}</div></div>', unsafe_allow_html=True)
                    co, ch = st.columns(2)
                    with co:
                        st.markdown('<div style="color:#1A7F4B;font-size:0.72rem;margin-bottom:4px">✅ correct</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="ab2-answer-box" style="border-left-color:#1A7F4B">{item["correct_answer"]}</div>', unsafe_allow_html=True)
                    with ch:
                        st.markdown('<div style="color:#DC3545;font-size:0.72rem;margin-bottom:4px">❌ hallucinated</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="ab2-answer-box">{highlight_answer(item["hallucinated_answer"], item["hallucinated_spans"])}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="ab2-tile-body" style="color:#5C6E82;font-style:italic;margin-top:4px">{item["translation"]}</div>', unsafe_allow_html=True)

        st.markdown('<hr class="ab2-rule">', unsafe_allow_html=True)
        if st.button("🔄 Start Over — Ask a New Question", use_container_width=True):
            for k in ["il_step","il_question","il_lang","il_model","il_answer","il_gen_method","il_result","il_context"]:
                st.session_state.pop(k, None)
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# CRICKET
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Cricket":
    st.markdown('<div class="ab2-h1">Cricket Dataset</div>', unsafe_allow_html=True)
    st.markdown('<div class="ab2-sub">Original cricket Q&amp;A evaluation dataset with annotated hallucination spans — a custom domain contribution beyond RAGTruth.</div>', unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    for col, (v, l) in zip([c1,c2,c3,c4], [("5","samples"),("4","hallucination types"),("cricket","domain"),("span","annotation")]):
        with col: st.markdown(f'<div class="ab2-met"><span class="ab2-met-val">{v}</span><div class="ab2-met-lbl">{l}</div></div>', unsafe_allow_html=True)

    idx = st.selectbox("Sample", range(len(CRICKET_DATA)), format_func=lambda i: f"{i+1}. {CRICKET_DATA[i]['question']}")
    item = CRICKET_DATA[idx]
    st.markdown(f'<div class="ab2-tile"><div class="ab2-tile-title">Context</div><div class="ab2-tile-body">{item["context"]}</div></div>', unsafe_allow_html=True)
    co, ch = st.columns(2)
    with co:
        st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.72rem;color:#1A7F4B;margin-bottom:4px">correct</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="ab2-answer-box" style="border-left-color:#1A7F4B">{item["correct_answer"]}</div>', unsafe_allow_html=True)
    with ch:
        st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.72rem;color:#DC3545;margin-bottom:4px">hallucinated</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="ab2-answer-box">{highlight_answer(item["hallucinated_answer"], item["hallucinated_spans"])}</div>', unsafe_allow_html=True)
    tags = " ".join(f'<span class="ab2-tag ab2-tag-red">{s}</span>' for s in item["hallucinated_spans"])
    st.markdown(f'Annotated spans: {tags}', unsafe_allow_html=True)

    if st.button("Run live detection on this sample"):
        with st.spinner("Detecting…"):
            result = run_detection(item["context"], item["hallucinated_answer"])
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f'<div class="ab2-met"><span class="ab2-met-val" style="color:#DC3545">{"Hallucinated" if result["is_hallucinated"] else "Supported"}</span><div class="ab2-met-lbl">verdict</div></div>', unsafe_allow_html=True)
        with m2: st.markdown(f'<div class="ab2-met"><span class="ab2-met-val">{result["confidence"]:.2f}</span><div class="ab2-met-lbl">confidence</div></div>', unsafe_allow_html=True)
        with m3: st.markdown(f'<div class="ab2-met"><span class="ab2-met-val">{result["hall_count"]}/{result["token_count"]}</span><div class="ab2-met-lbl">flagged / total</div></div>', unsafe_allow_html=True)

    st.markdown('<hr class="ab2-rule">', unsafe_allow_html=True)
    rows = [{"#": i+1, "Question": d["question"], "Correct Answer": d["correct_answer"],
             "Hallucinated Answer": d["hallucinated_answer"],
             "Hallucinated spans": ", ".join(d["hallucinated_spans"])} for i, d in enumerate(CRICKET_DATA)]
    df_cricket = pd.DataFrame(rows).set_index("#")
    st.dataframe(df_cricket, use_container_width=True)

    # ── Download options ─────────────────────────────────────────────────────
    st.markdown('<div class="ab2-h2">Download dataset</div>', unsafe_allow_html=True)
    dc1, dc2, dc3 = st.columns(3)

    # CSV
    csv_bytes = df_cricket.reset_index().to_csv(index=False).encode("utf-8")
    with dc1:
        st.download_button(
            label="⬇ Download CSV",
            data=csv_bytes,
            file_name="ab2detect_cricket_dataset.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # Excel
    from io import BytesIO
    excel_buf = BytesIO()
    with pd.ExcelWriter(excel_buf, engine="openpyxl") as writer:
        df_cricket.reset_index().to_excel(writer, index=False, sheet_name="CricketDataset")
    excel_bytes = excel_buf.getvalue()
    with dc2:
        st.download_button(
            label="⬇ Download Excel",
            data=excel_bytes,
            file_name="ab2detect_cricket_dataset.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    # PDF (HTML-rendered via reportlab or simple HTML fallback)
    def make_pdf_bytes(df):
        try:
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
            buf_pdf = BytesIO()
            doc = SimpleDocTemplate(buf_pdf, pagesize=landscape(A4), topMargin=30, bottomMargin=30)
            styles = getSampleStyleSheet()
            elems = []
            elems.append(Paragraph("AB2DETECT — Cricket Hallucination Dataset", styles["Title"]))
            elems.append(Spacer(1, 12))
            data_rows = [list(df.columns)] + [list(map(str, row)) for row in df.values]
            tbl = Table(data_rows, repeatRows=1)
            tbl.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0F1520")),
                ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
                ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE",   (0,0), (-1,-1), 7),
                ("GRID",       (0,0), (-1,-1), 0.5, colors.HexColor("#1A2535")),
                ("BACKGROUND", (0,1), (-1,-1), colors.HexColor("#060A10")),
                ("TEXTCOLOR",  (0,1), (-1,-1), colors.HexColor("#EEF2F8")),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#080C14"), colors.HexColor("#0F1520")]),
                ("VALIGN",     (0,0), (-1,-1), "TOP"),
                ("WORDWRAP",   (0,0), (-1,-1), True),
            ]))
            elems.append(tbl)
            doc.build(elems)
            return buf_pdf.getvalue()
        except Exception:
            # Fallback: simple HTML as PDF-ish download
            html = "<html><body><h2>AB2DETECT Cricket Dataset</h2>" + df.reset_index().to_html(index=False) + "</body></html>"
            return html.encode("utf-8")

    pdf_bytes = make_pdf_bytes(df_cricket)
    pdf_mime = "application/pdf" if pdf_bytes[:4] == b"%PDF" else "text/html"
    pdf_ext  = "pdf" if pdf_mime == "application/pdf" else "html"
    with dc3:
        st.download_button(
            label="⬇ Download PDF",
            data=pdf_bytes,
            file_name=f"ab2detect_cricket_dataset.{pdf_ext}",
            mime=pdf_mime,
            use_container_width=True,
        )

# ─────────────────────────────────────────────────────────────────────────────
# EXTENSION
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Extension":
    st.markdown('<div class="ab2-h1">Chrome Extension</div>', unsafe_allow_html=True)
    st.markdown('<div class="ab2-sub">Install the AB2DETECT extension to detect hallucinations directly in your browser on any AI-generated response.</div>', unsafe_allow_html=True)
    st.markdown('<div class="ab2-h2">Setup</div>', unsafe_allow_html=True)
    st.markdown("""<ol class="ab2-steps">
    <li class="ab2-step"><span class="ab2-step-num">01</span><span class="ab2-step-text">Start the backend: <code style="font-family:'IBM Plex Mono',monospace;font-size:0.8rem;background:#080C14;padding:2px 6px;border-radius:2px">uvicorn api:app --host 0.0.0.0 --port 8000</code></span></li>
    <li class="ab2-step"><span class="ab2-step-num">02</span><span class="ab2-step-text">Open Chrome → Settings → Extensions → Enable developer mode</span></li>
    <li class="ab2-step"><span class="ab2-step-num">03</span><span class="ab2-step-text">Click "Load unpacked" → select the <code style="font-family:'IBM Plex Mono',monospace;font-size:0.8rem;background:#080C14;padding:2px 6px;border-radius:2px">extension/</code> folder</span></li>
    <li class="ab2-step"><span class="ab2-step-num">04</span><span class="ab2-step-text">Click the AB2DETECT icon on any page with AI-generated text</span></li>
    </ol>""", unsafe_allow_html=True)
    st.markdown('<div class="ab2-h2">API endpoints</div>', unsafe_allow_html=True)
    for method, path, inp, out in [("POST","/detect","context, question, answer","spans, confidence, hall_rate"),("POST","/detect/batch","list of samples","list of results"),("GET","/health","—","status: ok")]:
        mc = "#5B5FEF" if method == "POST" else "#1A7F4B"
        st.markdown(f'<div style="display:flex;gap:1rem;padding:0.5rem 0;border-bottom:1px solid #1A2535;font-family:\'IBM Plex Mono\',monospace;font-size:0.8rem"><span style="color:{mc};min-width:3rem">{method}</span><span style="color:#EEF2F8;min-width:10rem">{path}</span><span style="color:#8892B0;font-family:\'IBM Plex Sans\',sans-serif">{inp} → {out}</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="ab2-h2">manifest.json</div>', unsafe_allow_html=True)
    st.code('{\n  "manifest_version": 3,\n  "name": "AB2DETECT",\n  "version": "1.0.0",\n  "description": "Token-level hallucination detection for LLM outputs",\n  "permissions": ["activeTab", "scripting", "storage"],\n  "action": { "default_popup": "popup.html" },\n  "background": { "service_worker": "background.js" },\n  "content_scripts": [{ "matches": ["<all_urls>"], "js": ["content.js"] }]\n}', language="json")

# ─────────────────────────────────────────────────────────────────────────────
# FAQ
# ─────────────────────────────────────────────────────────────────────────────
elif page == "FAQ":
    st.markdown('<div class="ab2-h1">FAQ</div>', unsafe_allow_html=True)
    st.markdown('<div class="ab2-sub">20 viva preparation questions covering hallucination detection, RAG, ModernBERT, and AB2DETECT.</div>', unsafe_allow_html=True)

    sq = st.text_input("Search", placeholder="e.g. ModernBERT, token, RAGTruth…")
    cf = st.selectbox("Category", ["All"] + sorted(set(f["cat"] for f in FAQ_DATA)))

    filtered = [f for f in FAQ_DATA
                if (not sq or sq.lower() in f["q"].lower() or sq.lower() in f["a"].lower())
                and (cf == "All" or f["cat"] == cf)]
    st.markdown(f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.75rem;color:#5C6E82;margin-bottom:0.75rem">{len(filtered)} question(s)</div>', unsafe_allow_html=True)

    TAG_COLORS = {"Basic":"#5B5FEF","Technical":"#8892B0","Models":"#1A7F4B","Dataset":"#5FCA8E","Results":"#F4A0A8","Tricky":"#DC3545","Future":"#9EA1F5"}
    for item in filtered:
        with st.expander(item["q"]):
            tc = TAG_COLORS.get(item["cat"], "#5C6E82")
            st.markdown(f'<span class="ab2-tag" style="border-color:{tc};color:{tc}">{item["cat"]}</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="ab2-answer-box" style="margin-top:0.5rem">{item["a"]}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="ab2-footer">
AB2DETECT &nbsp;·&nbsp; Abubakar Khan (1RUA24CSE0010) &amp; Abhishek D Nagoor (1RUA24CSE0009)
&nbsp;·&nbsp; SoCSE, RV University Bengaluru &nbsp;·&nbsp; Summer Internship 2025 &nbsp;·&nbsp; &copy; {date.today().year}
</div>
""", unsafe_allow_html=True)
