# AB2DETECT - FastAPI Backend
# Real hallucination detection using NLI + Real LLM answer generation
#
# Abubakar Khan (1RUA24CSE0010) - Abhishek D Nagoor (1RUA24CSE0009)
# SoCSE, RV University Bengaluru - Summer Internship 2025

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import time

from detector import HallucinationDetector
from generator import generate_answer, MODELS

app = FastAPI(
    title="AB2DETECT API",
    description="Span-level hallucination detection for RAG systems",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = HallucinationDetector()


# ── Request / Response Models ──────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    context: str
    question: str
    model_name: str = "Mistral-7B"
    hf_token: Optional[str] = None  # optional HuggingFace token for real LLM

class GenerateResponse(BaseModel):
    answer: str
    model_used: str
    method: str
    latency_ms: float

class DetectRequest(BaseModel):
    context: str
    question: str = ""
    answer: str

class DetectResponse(BaseModel):
    is_hallucinated: bool
    confidence: float
    spans: List[str]
    hall_rate: float
    token_count: int
    hall_count: int
    latency_ms: float
    method: str = "nli"
    sentence_scores: List[dict] = []

class FullPipelineRequest(BaseModel):
    """One-shot: give context + question, get LLM answer + hallucination analysis."""
    context: str
    question: str
    model_name: str = "Mistral-7B"
    hf_token: Optional[str] = None

class FullPipelineResponse(BaseModel):
    question: str
    context: str
    answer: str
    model_used: str
    generation_method: str
    is_hallucinated: bool
    confidence: float
    spans: List[str]
    hall_rate: float
    token_count: int
    hall_count: int
    hallucination_percent: float
    detection_method: str
    sentence_scores: List[dict] = []
    total_latency_ms: float

class BatchRequest(BaseModel):
    samples: List[DetectRequest]

class BatchResponse(BaseModel):
    results: List[DetectResponse]
    total: int
    hallucinated_count: int


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": "2.0.0",
        "detection_model": "cross-encoder/nli-deberta-v3-small",
        "available_llm_models": list(MODELS.keys()),
    }


@app.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    """Step 1: Generate an LLM answer from context + question."""
    if not req.context or not req.question:
        raise HTTPException(status_code=400, detail="context and question required")

    result = generate_answer(
        context=req.context,
        question=req.question,
        model_name=req.model_name,
        hf_token=req.hf_token,
    )
    return GenerateResponse(**result)


@app.post("/detect", response_model=DetectResponse)
async def detect(req: DetectRequest):
    """Step 2: Detect hallucinations in an answer given context."""
    if not req.context or not req.answer:
        raise HTTPException(status_code=400, detail="context and answer required")

    t0 = time.time()
    result = detector.detect(req.context, req.question, req.answer)
    result["latency_ms"] = round((time.time() - t0) * 1000, 2)

    return DetectResponse(
        is_hallucinated=result["is_hallucinated"],
        confidence=result["confidence"],
        spans=result["spans"],
        hall_rate=result["hall_rate"],
        token_count=result["token_count"],
        hall_count=result["hall_count"],
        latency_ms=result["latency_ms"],
        method=result.get("method", "nli"),
        sentence_scores=result.get("sentence_scores", []),
    )


@app.post("/pipeline", response_model=FullPipelineResponse)
async def full_pipeline(req: FullPipelineRequest):
    """
    FULL PIPELINE: context + question → LLM generates answer → detect hallucinations.
    This is the main endpoint for the complete RAG hallucination detection workflow.
    """
    if not req.context or not req.question:
        raise HTTPException(status_code=400, detail="context and question required")

    t0 = time.time()

    # Step 1: Generate answer from LLM
    gen = generate_answer(
        context=req.context,
        question=req.question,
        model_name=req.model_name,
        hf_token=req.hf_token,
    )

    # Step 2: Detect hallucinations in the generated answer
    det = detector.detect(req.context, req.question, gen["answer"])

    total_ms = round((time.time() - t0) * 1000, 2)

    hall_pct = round(det["hall_count"] / max(det["token_count"], 1) * 100, 2)

    return FullPipelineResponse(
        question=req.question,
        context=req.context,
        answer=gen["answer"],
        model_used=gen["model_used"],
        generation_method=gen["method"],
        is_hallucinated=det["is_hallucinated"],
        confidence=det["confidence"],
        spans=det["spans"],
        hall_rate=det["hall_rate"],
        token_count=det["token_count"],
        hall_count=det["hall_count"],
        hallucination_percent=hall_pct,
        detection_method=det.get("method", "nli"),
        sentence_scores=det.get("sentence_scores", []),
        total_latency_ms=total_ms,
    )


@app.post("/detect/batch", response_model=BatchResponse)
async def detect_batch(req: BatchRequest):
    if not req.samples:
        raise HTTPException(status_code=400, detail="samples list is empty")

    results = []
    for sample in req.samples:
        result = detector.detect(sample.context, sample.question, sample.answer)
        results.append(DetectResponse(
            is_hallucinated=result["is_hallucinated"],
            confidence=result["confidence"],
            spans=result["spans"],
            hall_rate=result["hall_rate"],
            token_count=result["token_count"],
            hall_count=result["hall_count"],
            latency_ms=result.get("latency_ms", 0.0),
            method=result.get("method", "nli"),
            sentence_scores=result.get("sentence_scores", []),
        ))

    hall_count = sum(1 for r in results if r.is_hallucinated)
    return BatchResponse(results=results, total=len(results), hallucinated_count=hall_count)


@app.get("/models")
async def list_models():
    return {"models": list(MODELS.keys())}


@app.get("/")
async def root():
    return {
        "name": "AB2DETECT API v2",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "POST /generate": "Step 1 - Generate LLM answer from context + question",
            "POST /detect":   "Step 2 - Detect hallucinations in an answer",
            "POST /pipeline": "Full pipeline - context + question → answer + detection",
            "POST /detect/batch": "Batch detection",
            "GET  /models":   "List available LLM models",
        }
    }
