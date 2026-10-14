# AB2DETECT — Hallucination Detection System

**Abubakar Khan (1RUA24CSE0010) · Abhishek D Nagoor (1RUA24CSE0009)**  
SoCSE, RV University Bengaluru · Summer Internship 2025

---

## What it does

Full RAG hallucination detection pipeline:

1. You give a **context** (retrieved document) and a **question**
2. The selected **LLM generates an answer** from the context
3. **AB2DETECT analyses** every sentence using NLI (Natural Language Inference)
4. Shows exactly **which % is hallucinated** and which specific spans are wrong

---

## How to run locally

### Step 1 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 2 — Start everything (one command)

```bash
python run.py
```

This starts:
- **Backend** at `http://localhost:8000` (FastAPI + NLI detection)
- **Frontend** at `http://localhost:8501` (Streamlit UI)

### Or run separately

**Backend:**
```bash
cd backend
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
cd frontend
streamlit run app.py
```

---

## How the detection works

```
User: context + question
        ↓
LLM generates answer  (Mistral / Zephyr / Falcon / LLaMA)
        ↓
NLI cross-encoder checks each sentence:
  context + sentence → ENTAIL / NEUTRAL / CONTRADICT
        ↓
CONTRADICT = hallucinated span
        ↓
Result: % hallucinated, flagged spans, sentence-level scores
```

**Model used:** `cross-encoder/nli-deberta-v3-small`  
- 130MB, runs on CPU  
- No GPU required  
- Downloads automatically on first run  

---

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check backend status |
| POST | `/generate` | Generate LLM answer from context + question |
| POST | `/detect` | Detect hallucinations in a given answer |
| POST | `/pipeline` | Full pipeline: generate + detect in one call |
| POST | `/detect/batch` | Batch detection |
| GET | `/models` | List available LLM models |

Interactive docs: `http://localhost:8000/docs`

---

## Project structure

```
ab2detect_submission/
├── run.py                  # One-click launcher
├── requirements.txt
├── backend/
│   ├── api.py              # FastAPI endpoints
│   ├── detector.py         # NLI hallucination detection
│   ├── generator.py        # LLM answer generation
│   └── corrector.py        # Auto-correction
├── frontend/
│   └── app.py              # Streamlit UI
└── extension/              # Chrome extension
```

---

## For the jury — live demo flow

1. Run `python run.py`
2. Open `http://localhost:8501`
3. Go to **Detection** page
4. Paste any context (e.g. a Wikipedia paragraph)
5. Type a question
6. Click **Run Full Pipeline**
7. See: generated answer + hallucination % + flagged spans
