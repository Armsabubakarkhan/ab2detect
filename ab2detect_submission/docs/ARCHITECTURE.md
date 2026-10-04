# AB2DETECT — System Architecture

## Overview

AB2DETECT is a three-tier system: a Streamlit frontend, a FastAPI backend, and a Chrome browser extension. All three components communicate through the same REST API.

```
┌─────────────────────────────────────────────────────────┐
│                    User Interfaces                        │
│                                                           │
│  ┌──────────────────┐    ┌─────────────────────────────┐ │
│  │  Streamlit App   │    │    Chrome Extension         │ │
│  │  (frontend/)     │    │    (extension/)             │ │
│  │  port 8501       │    │    popup.html + popup.js    │ │
│  └────────┬─────────┘    └──────────────┬──────────────┘ │
└───────────┼──────────────────────────────┼───────────────┘
            │  HTTP POST /detect           │
            ▼                              ▼
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                         │
│                   (backend/api.py)                        │
│                   port 8000                               │
│                                                           │
│   POST /detect      POST /detect/batch    GET /health    │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Detection Pipeline                           │
│              (backend/detector.py)                        │
│                                                           │
│  Input: [CLS] context [SEP] question [SEP] answer [SEP] │
│                         │                                 │
│              ModernBERT Encoder                           │
│         (4,096 tokens · Flash Attention 2 · RoPE)        │
│                         │                                 │
│        Token Classification Head                          │
│    label 0: supported   │   label 1: hallucinated         │
│                         │                                 │
│           Span Grouping (contiguous label-1 tokens)       │
│                         │                                 │
│  Output: spans, confidence, hall_rate, token_count        │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Auto-Correction (optional)                   │
│              (backend/corrector.py)                       │
│                                                           │
│  Extract entities and numbers from context               │
│  Replace hallucinated spans with context-grounded values │
└─────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend (`frontend/app.py`)
- Streamlit single-file app with 9 pages
- Tries the FastAPI backend first, falls back to local simulation
- IBM Plex Mono + IBM Plex Sans typography
- Plotly charts for model comparison dashboard
- EasyOCR integration for image-based detection

### Backend (`backend/`)
- `api.py` — FastAPI routes with CORS, Pydantic validation
- `detector.py` — `HallucinationDetector` class; replace `simulate()` with real HuggingFace inference
- `corrector.py` — `HallucinationCorrector` class for auto-correction

### Chrome Extension (`extension/`)
- Manifest v3
- `popup.html/js` — detection UI; calls backend, falls back to JS simulation
- `content.js` — injects floating button on AI chat pages
- `background.js` — service worker

## Model Architecture: ModernBERT

| Property | Value |
|---|---|
| Base architecture | BERT-style encoder |
| Parameters | 149M (base) / 395M (large) |
| Context window | 4,096 tokens |
| Positional encoding | Rotary Positional Embeddings (RoPE) |
| Attention | Flash Attention 2 |
| Pre-training data | 2 trillion tokens |
| Fine-tuning | RAGTruth dataset, AdamW lr=1e-5, 6 epochs |
| Output | Per-token logits → argmax → label 0/1 |

## Input Format

```
[CLS] {context} [SEP] {question} [SEP] {answer} [SEP]
                                        ↑
                              only these tokens
                              receive labels 0/1
                              (others masked with -100)
```

## Evaluation Metric

**Span-level F1** (primary): A predicted span counts as correct if it overlaps with a gold span at IoU ≥ 0.5.

This is stricter than token-level F1 and more meaningful for user-facing applications where exact span boundaries matter.
