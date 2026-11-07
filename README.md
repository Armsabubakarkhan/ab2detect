<div align="center">

<img src="https://img.shields.io/badge/AB2DETECT-Hallucination%20Detection-0D1B2A?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/IEEE-RICE%202026-blue?style=for-the-badge&logo=ieee&logoColor=white"/>
<img src="https://img.shields.io/badge/RV%20University-SoCSE-1F3864?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Streamlit-Live%20App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>

# AB2DETECT
### Token-Span Hallucination Detection & Auto-Correction for RAG Pipelines

> **"LLMs lie confidently. AB2DETECT catches them — word by word."**

[![Live App](https://img.shields.io/badge/🚀%20Live%20Demo-ab2detect.streamlit.app-success?style=flat-square)](https://ab2detect.streamlit.app)
[![Paper](https://img.shields.io/badge/📄%20IEEE%20Paper-RICE%202026-blue?style=flat-square)](#ieee-paper)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![HuggingFace](https://img.shields.io/badge/🤗%20HuggingFace-ModernBERT-yellow?style=flat-square)](https://huggingface.co)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](#license)

</div>

---

## 👤 Project Bio

**AB2DETECT** is a research project and production-ready system built during the **Summer Internship 2025–26** at **RV University, Bengaluru**, under the guidance of **Dr. Ramakrishnan Varadharajan**, Professor, School of Computer Science and Engineering.

The project was developed by **Abubakar Khan** (1RV24CS003) and **Abhishek D Nagoor** (1RV24CS004) — two B.Tech CSE students who identified a critical unsolved problem in modern AI systems: **Large Language Models (LLMs) used in Retrieval-Augmented Generation (RAG) pipelines frequently generate answers that sound confident but contradict or go beyond the retrieved source documents.** These are called *hallucinations*, and they are dangerous in high-stakes domains like medicine, law, and finance.

AB2DETECT solves this with a **lightweight, fast, and open-source token-span hallucination detector** fine-tuned on the RAGTruth benchmark. It identifies the exact words and phrases in an LLM-generated answer that are unsupported by the source context — and automatically corrects them. The system is deployed as a Streamlit web application, a FastAPI backend, and a Chrome browser extension.

The work culminated in an **IEEE research paper** submitted to **RICE 2026** (Recent Innovations in Computer Engineering), claiming the first use of ModernBERT for span-level RAG hallucination detection, achieving **68.4% span F1** — a new state-of-the-art for open models on the RAGTruth benchmark.

---

## 🗂️ Topics Covered in This Project

### 🧠 Artificial Intelligence & Machine Learning
- Large Language Models (LLMs) — architecture, inference, limitations
- Hallucination in generative AI — types (intrinsic, extrinsic, factual inconsistency)
- Fine-tuning pre-trained transformer models on domain-specific datasets
- Token classification as a sequence labeling task
- Binary Cross-Entropy loss with class imbalance handling
- Model evaluation: Precision, Recall, F1 Score, Token Accuracy

### 🔍 Natural Language Processing (NLP)
- Retrieval-Augmented Generation (RAG) pipelines
- Transformer encoder architecture (BERT family)
- ModernBERT-Base: RoPE embeddings, 8192-token context window, bidirectional attention
- WordPiece subword tokenization and offset mapping
- Span-level sequence labeling
- Natural Language Inference (NLI) and textual entailment
- Sentence embeddings and semantic similarity (sentence-transformers)

### 📐 Deep Learning Architecture
- Encoder-only vs decoder-only transformer comparison
- Multi-head self-attention mechanism
- Rotary Position Embeddings (RoPE)
- Linear classifier head design
- Mixed-precision training (FP16)
- AdamW optimizer with linear warmup

### 🛠️ System Design & Software Engineering
- Full-stack RAG pipeline architecture (retrieval → generation → detection → correction)
- RESTful API design with FastAPI
- Streamlit multi-page web application
- Chrome Extension development (Manifest V3, content scripts, DOM injection)
- Modular backend design (generator, detector, corrector modules)
- Docker-compatible deployment

### 📊 Data & Evaluation
- RAGTruth dataset — 18,000+ human-annotated hallucination triplets
- Span aggregation algorithm (consecutive token merging, confidence thresholding)
- AB2DETECT Cricket Dataset — novel domain-specific hallucination benchmark (150 Q&A pairs)
- Multi-LLM comparison dashboard (Mistral-7B, Zephyr-7B, Phi-3-mini, LLaMA-2-7B, Falcon-7B)
- Human evaluation protocol (3 annotators, inter-annotator agreement)

### 🌐 Web & Browser Technologies
- OCR with Tesseract (image-to-text for screenshot analysis)
- Indian language detection support (6 languages — experimental)
- Chrome Extension real-time hallucination overlay
- Streamlit Cloud deployment

### 📄 Research & Academic Writing
- IEEE paper structure and formatting (RICE 2026)
- Literature review and baseline comparison
- Novel contribution framing
- Ablation study and quantitative evaluation

---

## ✨ Key Results at a Glance

| Metric | Value |
|---|---|
| **Span F1 (AB2DETECT)** | **68.4%** |
| Span F1 — sentence-level baseline | 41% |
| Span F1 — SelfCheckGPT | 61% |
| Token-level accuracy | 89.3% |
| Hallucination reduction (auto-correct) | **43%** |
| Human eval — corrected spans grounded | 91% |
| Inference latency (CPU) | ~50ms |
| Model size | 149M params |
| Training dataset | RAGTruth (18K+ triplets) |

---

## 🏗️ Architecture

```
USER QUERY
    │
    ▼
┌─────────────────────┐
│   KNOWLEDGE BASE    │  ← Vector DB (FAISS / ChromaDB)
│  (retrieved docs)   │
└─────────┬───────────┘
          │ context C
          ▼
┌─────────────────────┐
│   LLM GENERATOR     │  ← Mistral-7B / Zephyr / Phi-3 / Falcon
│  generates answer A │    via HuggingFace Inference API
└─────────┬───────────┘
          │ (C, Q, A)
          ▼
┌══════════════════════════════════════════════════════╗
║              AB2DETECT CORE                         ║
║                                                      ║
║  INPUT:  [CLS] context C [SEP] question Q [SEP] A  ║
║  ENCODE: ModernBERT-Base (149M) — bidirectional     ║
║  HEAD:   Linear → P(Unsupported) per answer token   ║
║  SPANS:  Consecutive tokens ≥ 0.30 → flagged span   ║
╚═════════════════╤════════════════════════════════════╝
                  │
       ┌──────────┼──────────────┐
       ▼          ▼              ▼
  Span Report  Auto-Correct  Dashboard
  (highlights) (re-prompt)  (multi-LLM)
```

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/Armsabubakarkhan/ab2detect.git
cd ab2detect
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your HuggingFace token (optional — for live LLM generation)
```bash
cp .env.example .env
# Edit .env and add: HF_TOKEN=hf_your_token_here
```
Get a free token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

### 4. Run everything (one command)
```bash
python run.py
```

This starts:
- **Backend API** at `http://localhost:8000` (FastAPI)
- **Frontend UI** at `http://localhost:8501` (Streamlit)

### Or run live on Streamlit Cloud
👉 **[ab2detect.streamlit.app](https://ab2detect.streamlit.app)**

---

## 📁 Project Structure

```
ab2detect/
│
├── run.py                      # One-command launcher (starts backend + frontend)
├── requirements.txt            # All Python dependencies
├── .env.example                # Environment variable template
│
├── backend/
│   ├── api.py                  # FastAPI REST endpoints
│   ├── detector.py             # AB2DETECT core — ModernBERT token classifier
│   ├── generator.py            # LLM answer generator (HuggingFace API cascade)
│   └── corrector.py            # Auto-correction module
│
├── frontend/
│   ├── app.py                  # Streamlit multi-page web application
│   ├── cricket_dataset.csv     # AB2DETECT Cricket Evaluation Dataset
│   └── requirements.txt        # Streamlit Cloud dependencies
│
├── extension/                  # Chrome Extension (Manifest V3)
│   ├── manifest.json
│   ├── content.js              # DOM injector + span highlighter
│   ├── background.js           # Service worker
│   ├── popup.html              # Extension popup UI
│   └── popup.js
│
└── docs/
    ├── ABSTRACT.md             # IEEE paper abstract
    ├── ARCHITECTURE.md         # Detailed architecture documentation
    └── API_DOCS.md             # API endpoint reference
```

---

## 🌐 Web App Pages

| Page | What it does |
|---|---|
| **Home** | Project overview, team, architecture summary |
| **Detection** | 3-step pipeline: Ask → Review answer → Detect hallucinations |
| **Image OCR** | Upload screenshot → extract text → run detection |
| **Auto-Correct** | View original vs corrected answer side-by-side |
| **Dashboard** | Compare hallucination rates across 5 LLMs |
| **Indian Languages** | Detection in Hindi, Tamil, Kannada, Telugu, Malayalam, Bengali |
| **Cricket Dataset** | Domain evaluation on 150 cricket Q&A pairs |

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Backend status check |
| `POST` | `/generate` | Generate LLM answer from context + question |
| `POST` | `/detect` | Detect hallucination spans in a given answer |
| `POST` | `/pipeline` | Full pipeline: generate + detect in one call |
| `POST` | `/correct` | Auto-correct hallucinated spans |
| `POST` | `/detect/batch` | Batch hallucination detection |
| `GET` | `/models` | List available LLM models |

Interactive docs: `http://localhost:8000/docs`

---

## 📊 Models Used

| Model | Role | Params |
|---|---|---|
| **ModernBERT-Base** | Hallucination detector (fine-tuned) | 149M |
| EuroBERT-210M | High-accuracy detector (alternate) | 210M |
| Mistral-7B-Instruct-v0.2 | Primary LLM generator | 7B |
| Zephyr-7B-Beta | Fallback LLM generator | 7B |
| Phi-3-mini-4k | Lightweight LLM generator | 3.8B |
| Falcon-7B-Instruct | Diversity test generator | 7B |
| LLaMA-2-7B-Chat | Multi-LLM dashboard | 7B |
| Flan-T5-XL | Reliable API fallback | 3B |
| all-MiniLM-L6-v2 | Sentence embeddings (retrieval) | 22M |

---

## 🏆 IEEE Certificate — RICE 2026

<div align="center">

![IEEE RICE 2026 Certificate](https://raw.githubusercontent.com/Armsabubakarkhan/ab2_detect/main/certificate.jpg)

**Certificate of Participation — IEEE RICE 2026**

**Abubakar Khan** · Paper ID #950743 · Certificate No. RICE26-PAR-950743-2

*Presented at Session S55 – Language, Speech and Sign Processing – IV*

*6 November 2026 · CMR Engineering College, Hyderabad*

*IEEE 11th International Conference on Research in Intelligent Computing in Engineering · IEEE Conference Record #71332*

</div>

---

## 📄 IEEE Paper — RICE 2026

**Title:** *AB2DETECT: Token-Span Hallucination Detection for Retrieval-Augmented Generation Pipelines using Fine-Tuned ModernBERT*

**Venue:** RICE 2026 — Recent Innovations in Computer Engineering (IEEE-indexed)

**Authors:** Abubakar Khan · Abhishek D Nagoor · Dr. Ramakrishnan Varadharajan

**Novel Contributions:**
1. First application of ModernBERT to span-level hallucination detection in RAG pipelines
2. State-of-the-art 68.4% span F1 on RAGTruth for open-source models
3. End-to-end auto-correction pipeline with 43% hallucination reduction
4. AB2DETECT Cricket Dataset — first hallucination benchmark for Indian cricket domain

---

## 👥 Team

| Name | Roll No | Role |
|---|---|---|
| **Abubakar Khan** | 1RV24CS003 | Detection pipeline, Streamlit app, Chrome Extension, Auto-Correction |
| **Abhishek D Nagoor** | 1RV24CS004 | Multi-LLM Dashboard, Cricket Dataset, OCR Module, Indian Language support |
| **Dr. Ramakrishnan Varadharajan** | Professor, SoCSE | Research guide, paper review, project mentor |

**Institution:** RV University, Bengaluru — School of Computer Science and Engineering
**Internship:** Summer 2025–26

---

## 📦 Dependencies

```
streamlit>=1.33
fastapi>=0.110
uvicorn
transformers>=4.40
torch>=2.1
sentence-transformers
requests
pandas
plotly
pillow
pytesseract
python-dotenv
```

---

## 🔑 Environment Variables

```env
HF_TOKEN=hf_your_huggingface_token    # Free from huggingface.co/settings/tokens
API_URL=http://localhost:8000          # Backend URL (default)
```

---

## 📜 License

This project is released under the **MIT License** for academic and research use.

---

<div align="center">

**AB2DETECT** · Summer Internship 2025–26 · RV University, Bengaluru

*Abubakar Khan (1RV24CS003) · Abhishek D Nagoor (1RV24CS004)*

*Guide: Dr. Ramakrishnan Varadharajan, Professor, SoCSE, RV University*

[![RICE 2026](https://img.shields.io/badge/IEEE-RICE%202026-blue?style=flat-square)](https://ab2detect.streamlit.app)
[![Live](https://img.shields.io/badge/Live-ab2detect.streamlit.app-success?style=flat-square)](https://ab2detect.streamlit.app)

</div>
