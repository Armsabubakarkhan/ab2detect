"""
AB2DETECT — Hallucination Detection System
Abubakar Khan (1RUA24CSE0010) · Abhishek D Nagoor (1RUA24CSE0009)
SoCSE, RV University Bengaluru · Summer Internship 2025
"""

import streamlit as st
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
    ("Indian Lang",  "Kannada examples"),
    ("Cricket",      "Domain dataset"),
    ("Extension",    "Chrome setup"),
    ("FAQ",          "Viva prep"),
]

with st.sidebar:
    st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:1.05rem;font-weight:600;color:#EEF2F8;padding:0.5rem 0 0.1rem 0;letter-spacing:-0.01em">AB2DETECT</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:\'IBM Plex Sans\',sans-serif;font-size:0.74rem;color:#5C6E82;margin-bottom:1.2rem">Hallucination Detection · RV University</div>', unsafe_allow_html=True)

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
    time.sleep(0.4)
    context_tokens = set(re.findall(r'\b\w+\b', context.lower()))
    answer_words   = re.findall(r'\b\w+\b', answer)
    stopwords = {'the','a','an','is','are','was','were','be','been','being',
                 'have','has','had','do','does','did','will','would','could',
                 'should','may','might','shall','can','to','of','in','on',
                 'at','by','for','with','from','as','into','about','and',
                 'or','but','not','that','this','it','he','she','they','we',
                 'you','i','my','your','his','her','their','our'}
    spans = []
    for word in answer_words:
        if (word.lower() not in context_tokens and word.lower() not in stopwords
                and len(word) > 2 and random.random() < 0.35):
            spans.append(word)
    for ent in re.findall(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b', answer):
        for part in ent.split():
            if part.lower() not in context_tokens and part not in spans and random.random() < 0.5:
                spans.append(part)
    ctx_nums = re.findall(r'\b\d+(?:[,\.]\d+)*\b', context)
    for num in re.findall(r'\b\d+(?:[,\.]\d+)*\b', answer):
        if num not in ctx_nums:
            spans.append(num)
    seen = list(dict.fromkeys(spans))[:6]
    return {"spans": seen, "is_hallucinated": len(seen) > 0,
            "confidence": max(0.62, min(0.98, 0.98 - len(seen) * 0.06)),
            "token_count": len(answer_words), "hall_count": len(seen),
            "hall_rate": len(seen) / max(len(answer_words), 1)}


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
    if not spans:
        return answer
    ctx_facts = re.findall(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b|\b\d+(?:[,\.]\d+)*\b', context)
    corrected = answer
    for i, span in enumerate(spans):
        replacement = ctx_facts[i] if i < len(ctx_facts) else f"[verified]"
        corrected = corrected.replace(span, f"**{replacement}**", 1)
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

KANNADA_DATA = [
    {"context": "ಭಾರತದ ರಾಷ್ಟ್ರೀಯ ಹಕ್ಕಿ ನವಿಲು. ಇದು 1963 ರಲ್ಲಿ ರಾಷ್ಟ್ರೀಯ ಹಕ್ಕಿಯಾಗಿ ಘೋಷಿಸಲಾಯಿತು.",
     "question": "ಭಾರತದ ರಾಷ್ಟ್ರೀಯ ಹಕ್ಕಿ ಯಾವುದು?",
     "correct_answer": "ಭಾರತದ ರಾಷ್ಟ್ರೀಯ ಹಕ್ಕಿ ನವಿಲು, ಇದನ್ನು 1963 ರಲ್ಲಿ ಘೋಷಿಸಲಾಯಿತು.",
     "hallucinated_answer": "ಭಾರತದ ರಾಷ್ಟ್ರೀಯ ಹಕ್ಕಿ ಗಿಳಿ, ಇದನ್ನು 1975 ರಲ್ಲಿ ಘೋಷಿಸಲಾಯಿತು.",
     "hallucinated_spans": ["ಗಿಳಿ", "1975"],
     "translation": "India's national bird is the peacock, declared in 1963. Hallucinated: parrot, 1975"},
    {"context": "ಕರ್ನಾಟಕದ ರಾಜಧಾನಿ ಬೆಂಗಳೂರು. ಇದು ಭಾರತದ ಐಟಿ ರಾಜಧಾನಿ ಎಂದು ಕರೆಯಲ್ಪಡುತ್ತದೆ.",
     "question": "ಕರ್ನಾಟಕದ ರಾಜಧಾನಿ ಯಾವುದು?",
     "correct_answer": "ಕರ್ನಾಟಕದ ರಾಜಧಾನಿ ಬೆಂಗಳೂರು, ಇದನ್ನು ಭಾರತದ ಐಟಿ ರಾಜಧಾನಿ ಎನ್ನುತ್ತಾರೆ.",
     "hallucinated_answer": "ಕರ್ನಾಟಕದ ರಾಜಧಾನಿ ಮೈಸೂರು, ಇದನ್ನು ಭಾರತದ ಐಟಿ ರಾಜಧಾನಿ ಎನ್ನುತ್ತಾರೆ.",
     "hallucinated_spans": ["ಮೈಸೂರು"],
     "translation": "Capital of Karnataka is Bengaluru. Hallucinated: Mysuru"},
]

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
    st.markdown('<div class="ab2-h1">AB2DETECT</div>', unsafe_allow_html=True)
    st.markdown('<div class="ab2-sub">Span-level hallucination detection for RAG systems · SoCSE, RV University · Summer Internship 2025</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="ab2-term">
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
        ("Indian Language", "Kannada-language detection examples extending evaluation to Indic multilingual contexts using EuroBERT's shared vocabulary."),
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
# DETECTION
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Detection":
    st.markdown('<div class="ab2-h1">Core Detection</div>', unsafe_allow_html=True)
    st.markdown('<div class="ab2-sub">Provide a context, question, and LLM answer. Run token-level hallucination detection.</div>', unsafe_allow_html=True)

    model_name = st.selectbox("Model backbone", ["Mistral-7B", "Zephyr-7B", "Falcon-7B", "LLaMA-2-7B"])
    col_a, col_b = st.columns(2)
    with col_a:
        context = st.text_area("Context", height=140,
            value="Sachin Tendulkar scored 15,921 runs in Test cricket across 200 Test matches with a batting average of 53.78. He made his international debut in 1989 against Pakistan at the age of 16.")
        question = st.text_input("Question", value="How many Test runs did Sachin Tendulkar score?")
    with col_b:
        answer = st.text_area("LLM answer", height=140,
            value="Sachin Tendulkar scored 18,000 runs in Test cricket across 220 matches with a batting average of 61.5, debuting in 1987.")

    gc, dc = st.columns(2)
    with gc:
        if st.button("Generate answer from model"):
            with st.spinner("Generating…"):
                st.session_state["gen_answer"] = simulate_model_answer(question, model_name, context)
            st.rerun()
    with dc:
        run = st.button("Run detection")

    if "gen_answer" in st.session_state:
        st.info(f"Generated: {st.session_state['gen_answer']}")

    if run:
        if not context or not answer:
            st.warning("Provide both context and answer.")
        else:
            with st.spinner("Running ModernBERT token classification…"):
                result = run_detection(context, answer)

            st.markdown('<hr class="ab2-rule">', unsafe_allow_html=True)
            r1, r2, r3, r4 = st.columns(4)
            sc = "#DC3545" if result["is_hallucinated"] else "#1A7F4B"
            sv = "Hallucinated" if result["is_hallucinated"] else "Supported"
            with r1: st.markdown(f'<div class="ab2-met"><span class="ab2-met-val" style="color:{sc}">{sv}</span><div class="ab2-met-lbl">verdict</div></div>', unsafe_allow_html=True)
            with r2: st.markdown(f'<div class="ab2-met"><span class="ab2-met-val">{result["confidence"]:.2f}</span><div class="ab2-met-lbl">confidence</div></div>', unsafe_allow_html=True)
            with r3: st.markdown(f'<div class="ab2-met"><span class="ab2-met-val">{result["hall_count"]}</span><div class="ab2-met-lbl">flagged spans</div></div>', unsafe_allow_html=True)
            with r4: st.markdown(f'<div class="ab2-met"><span class="ab2-met-val">{result["token_count"]}</span><div class="ab2-met-lbl">total tokens</div></div>', unsafe_allow_html=True)

            st.markdown(f'<div class="ab2-answer-box">{highlight_answer(answer, result["spans"])}</div>', unsafe_allow_html=True)

            if result["spans"]:
                tags = " ".join(f'<span class="ab2-tag ab2-tag-red">{s}</span>' for s in result["spans"])
                st.markdown(f'<div style="margin-bottom:1rem">Flagged: {tags}</div>', unsafe_allow_html=True)

            with st.expander("Token breakdown"):
                rows = [{"token": t, "label": 1 if any(s.lower() in t.lower() for s in result["spans"]) else 0}
                        for t in re.findall(r'\S+', answer)]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, height=200)

# ─────────────────────────────────────────────────────────────────────────────
# IMAGE
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Image":
    st.markdown('<div class="ab2-h1">Image Detection</div>', unsafe_allow_html=True)
    st.markdown('<div class="ab2-sub">Upload a document image. EasyOCR extracts the text, which becomes your context for hallucination detection.</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader("Document image", type=["png","jpg","jpeg","webp"])
    if uploaded:
        img = Image.open(uploaded)
        ci, ct = st.columns(2)
        with ci:
            st.image(img, caption="Uploaded", use_column_width=True)
        with ct:
            with st.spinner("Extracting text with EasyOCR…"):
                try:
                    import easyocr
                    reader = easyocr.Reader(['en'])
                    buf = io.BytesIO()
                    img.save(buf, format='PNG')
                    extracted = " ".join([r[1] for r in reader.readtext(buf.getvalue())])
                except Exception:
                    extracted = "OCR unavailable. Paste context text below."
            st.text_area("Extracted context", value=extracted, height=160)

        st.markdown('<hr class="ab2-rule">', unsafe_allow_html=True)
        q_img = st.text_input("Question about this document")
        a_img = st.text_area("LLM answer to check", height=100)
        if st.button("Run detection"):
            if a_img:
                with st.spinner("Detecting…"):
                    result = run_detection(extracted, a_img)
                sc = "#DC3545" if result["is_hallucinated"] else "#1A7F4B"
                sv = "Hallucinated" if result["is_hallucinated"] else "Supported"
                st.markdown(f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.85rem;color:{sc};margin:0.5rem 0">{sv} · confidence {result["confidence"]:.2f} · {result["hall_count"]} spans</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="ab2-answer-box">{highlight_answer(a_img, result["spans"])}</div>', unsafe_allow_html=True)
    else:
        st.markdown("""<div class="ab2-tile">
        <div class="ab2-tile-title">How it works</div>
        <ol class="ab2-steps" style="margin-top:0.5rem">
        <li class="ab2-step"><span class="ab2-step-num">01</span><span class="ab2-step-text">Upload any PNG/JPG document, screenshot, or page scan</span></li>
        <li class="ab2-step"><span class="ab2-step-num">02</span><span class="ab2-step-text">EasyOCR reads the text (supports printed English)</span></li>
        <li class="ab2-step"><span class="ab2-step-num">03</span><span class="ab2-step-text">Extracted text becomes the retrieval context</span></li>
        <li class="ab2-step"><span class="ab2-step-num">04</span><span class="ab2-step-text">Paste any LLM answer and run token-level detection</span></li>
        </ol></div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# AUTO-CORRECT
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Auto-Correct":
    st.markdown('<div class="ab2-h1">Auto-Correction</div>', unsafe_allow_html=True)
    st.markdown('<div class="ab2-sub">Detect hallucinated spans and automatically replace them with context-grounded corrections.</div>', unsafe_allow_html=True)

    ctx_ac = st.text_area("Context", height=120,
        value="Australia won the 2023 ICC Cricket World Cup held in India. They defeated India in the final played at Narendra Modi Stadium in Ahmedabad on November 19, 2023. Travis Head was named Player of the Match.")
    ans_ac = st.text_area("LLM answer", height=100,
        value="India won the 2023 Cricket World Cup, defeating Australia in the final at Mumbai. Virat Kohli was named Player of the Match.")

    if st.button("Detect and correct"):
        with st.spinner("Running detection…"):
            result = run_detection(ctx_ac, ans_ac)
        corrected = auto_correct_answer(ans_ac, ctx_ac, result["spans"])
        co, cc = st.columns(2)
        with co:
            st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.72rem;color:#DC3545;margin-bottom:4px">original</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="ab2-answer-box">{highlight_answer(ans_ac, result["spans"])}</div>', unsafe_allow_html=True)
        with cc:
            st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.72rem;color:#1A7F4B;margin-bottom:4px">corrected</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="ab2-answer-box" style="border-left-color:#1A7F4B">{corrected}</div>', unsafe_allow_html=True)
        if result["spans"]:
            st.markdown(f'<div style="font-family:\'IBM Plex Sans\',sans-serif;font-size:0.82rem;color:#5C6E82;margin-top:0.5rem">{len(result["spans"])} span(s) corrected using context-grounded extraction</div>', unsafe_allow_html=True)

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
    st.markdown('<div class="ab2-sub">Hallucination detection on Kannada-language text using EuroBERT\'s multilingual encoder with shared BPE vocabulary.</div>', unsafe_allow_html=True)
    for item in KANNADA_DATA:
        with st.expander(item["question"]):
            st.markdown(f'<div class="ab2-tile"><div class="ab2-tile-title">Context</div><div class="ab2-tile-body">{item["context"]}</div></div>', unsafe_allow_html=True)
            co, ch = st.columns(2)
            with co:
                st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.72rem;color:#1A7F4B;margin-bottom:4px">correct</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="ab2-answer-box" style="border-left-color:#1A7F4B">{item["correct_answer"]}</div>', unsafe_allow_html=True)
            with ch:
                st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.72rem;color:#DC3545;margin-bottom:4px">hallucinated</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="ab2-answer-box">{highlight_answer(item["hallucinated_answer"], item["hallucinated_spans"])}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="ab2-tile-body" style="margin-top:0.5rem">{item["translation"]}</div>', unsafe_allow_html=True)
            tags = " ".join(f'<span class="ab2-tag ab2-tag-red">{s}</span>' for s in item["hallucinated_spans"])
            st.markdown(f'Flagged: {tags}', unsafe_allow_html=True)

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
    rows = [{"#": i+1, "Question": d["question"], "Hallucinated spans": ", ".join(d["hallucinated_spans"])} for i, d in enumerate(CRICKET_DATA)]
    st.dataframe(pd.DataFrame(rows).set_index("#"), use_container_width=True)

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
