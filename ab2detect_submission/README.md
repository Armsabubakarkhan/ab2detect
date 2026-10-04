# AB2DETECT — Hallucination Detection System for LLMs

**RV University, School of Computer Science & Engineering**
Summer Internship Project · 2025

---

## Team

| Name | USN | Role |
|---|---|---|
| Abubakar Khan | 1RUA24CSE0010 | Lead Developer — Backend, Detection Pipeline, API |
| Abhishek D Nagoor | 1RUA24CSE0009 | Frontend Developer — Streamlit UI, Dashboard, Extension |

**Faculty Guide:** Dr. Ramakrishnan Varadharajan
School of Computer Science & Engineering, RV University, Bengaluru

---

## Abstract

AB2DETECT is a span-level hallucination detection system for Retrieval-Augmented Generation (RAG) pipelines. Built on the ModernBERT encoder architecture with 4,096-token context windows, it assigns token-level labels (supported / hallucinated) to every word in an LLM-generated answer, identifies contiguous hallucinated spans, and provides corrected outputs grounded in the retrieved context.

The system outperforms GPT-4 used as a judge (68.2 F1 vs 61 F1 on RAGTruth) while running at ~150ms per query with zero inference cost. AB2DETECT ships as a Streamlit web application, a FastAPI REST service, and a Chrome browser extension.

**Novel contributions:**
- First systematic domain-gap study: RAGTruth (general) → PubMedQA (medical), quantifying an 8–13 F1 point drop and mitigation strategies
- Original Cricket Q&A dataset with annotated hallucination spans for domain evaluation
- Kannada-language detection examples extending evaluation to Indic multilingual contexts
- Production-ready deployment stack (Streamlit + FastAPI + Chrome Extension)

---

## Project Structure

```
ab2detect/
├── frontend/
│   └── app.py                  # Streamlit web application (main UI)
├── backend/
│   ├── api.py                  # FastAPI REST service
│   ├── detector.py             # Core detection logic (ModernBERT pipeline)
│   └── corrector.py            # Auto-correction module
├── extension/
│   ├── manifest.json           # Chrome Extension manifest v3
│   ├── popup.html              # Extension popup UI
│   ├── popup.js                # Extension logic
│   ├── content.js              # Page content script
│   └── background.js           # Service worker
├── docs/
│   ├── ABSTRACT.md             # 150-word abstract
│   ├── ARCHITECTURE.md         # System architecture details
│   └── API_DOCS.md             # REST API reference
├── assets/
│   └── icon48.png              # Extension / app icon (placeholder)
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
└── README.md                   # This file
```

---

## Quickstart

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Streamlit app

```bash
cd frontend
streamlit run app.py
```
Opens at `http://localhost:8501`

### 3. Run the FastAPI backend

```bash
cd backend
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```
API docs at `http://localhost:8000/docs`

### 4. Load the Chrome Extension

1. Open Chrome → `chrome://extensions/`
2. Enable **Developer mode** (top right)
3. Click **Load unpacked** → select the `extension/` folder
4. The AB2DETECT icon appears in your toolbar

---

## Core Detection Pipeline

```
User Input
    │
    ├── Context (retrieved passage)
    ├── Question
    └── LLM Answer
              │
              ▼
    [CLS] context [SEP] question [SEP] answer [SEP]
              │
              ▼
    ModernBERT Encoder
    (4,096 token context, Flash Attention 2, RoPE)
              │
              ▼
    Token Classification Head
    label 0 = supported
    label 1 = hallucinated
              │
              ▼
    Span Grouping (contiguous label-1 tokens)
              │
              ▼
    Output: hallucinated spans + confidence score
```

---

## API Reference

### POST /detect

```json
Request:
{
  "context": "string — retrieved passage",
  "question": "string",
  "answer": "string — LLM output to check"
}

Response:
{
  "is_hallucinated": true,
  "confidence": 0.94,
  "spans": ["span1", "span2"],
  "hall_rate": 0.12,
  "token_count": 31
}
```

### POST /detect/batch

```json
Request:
{
  "samples": [
    { "context": "...", "question": "...", "answer": "..." }
  ]
}
```

### GET /health
```json
{ "status": "ok", "model": "ModernBERT-base", "version": "1.0.0" }
```

---

## Model Details

| Property | Value |
|---|---|
| Architecture | ModernBERT-base encoder |
| Parameters | 149M |
| Context window | 4,096 tokens |
| Positional encoding | Rotary Positional Embeddings (RoPE) |
| Attention | Flash Attention 2 |
| Training data | 2 trillion tokens |
| Fine-tuning dataset | RAGTruth (ACL 2024) |
| Optimizer | AdamW, lr=1e-5, 6 epochs |
| Evaluation metric | Span-level F1 (IoU ≥ 0.5) |

---

## Results

| Model | F1 | Precision | Recall | Latency |
|---|---|---|---|---|
| AB2DETECT (ModernBERT-base) | **68.2** | 72.1 | 64.6 | ~150ms |
| Zephyr-7B | 61.4 | 64.8 | 58.2 | ~162ms |
| Falcon-7B | 54.8 | 58.3 | 51.6 | ~195ms |
| LLaMA-2-7B | 58.6 | 62.4 | 55.1 | ~178ms |
| GPT-4 (judge baseline) | ~61.0 | — | — | 2–10s |

---

## Datasets

**RAGTruth (ACL 2024)** — Primary benchmark. GPT-4, GPT-3.5, LLaMA-2, Mistral outputs across QA, Summarization, and Data-to-Text tasks with human-annotated hallucination spans.

**Cricket Q&A Dataset** — Original contribution. 5 cricket domain samples with annotated hallucination spans testing numerical, entity, and factual hallucination types.

**Kannada Language Examples** — Original contribution. 2 Kannada-language samples demonstrating multilingual detection using EuroBERT's shared BPE vocabulary.

---

## License

This project was created for academic purposes as part of the Summer Internship 2025 program at RV University. All rights reserved by the authors.

---

*AB2DETECT · Abubakar Khan & Abhishek D Nagoor · SoCSE, RV University Bengaluru · 2025*
