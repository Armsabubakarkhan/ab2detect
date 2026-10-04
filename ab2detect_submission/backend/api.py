"""
AB2DETECT — FastAPI Backend
Abubakar Khan (1RUA24CSE0010) · Abhishek D Nagoor (1RUA24CSE0009)
SoCSE, RV University Bengaluru · Summer Internship 2025
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import time

from detector import HallucinationDetector

app = FastAPI(
    title="AB2DETECT API",
    description="Span-level hallucination detection for RAG systems using ModernBERT",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = HallucinationDetector()


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


class BatchRequest(BaseModel):
    samples: List[DetectRequest]


class BatchResponse(BaseModel):
    results: List[DetectResponse]
    total: int
    hallucinated_count: int


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model": "ModernBERT-base (simulated)",
        "version": "1.0.0",
    }


@app.post("/detect", response_model=DetectResponse)
async def detect(req: DetectRequest):
    if not req.context or not req.answer:
        raise HTTPException(status_code=400, detail="context and answer are required")

    t0 = time.time()
    result = detector.detect(req.context, req.question, req.answer)
    latency_ms = (time.time() - t0) * 1000

    return DetectResponse(
        is_hallucinated=result["is_hallucinated"],
        confidence=result["confidence"],
        spans=result["spans"],
        hall_rate=result["hall_rate"],
        token_count=result["token_count"],
        hall_count=result["hall_count"],
        latency_ms=round(latency_ms, 2),
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
            latency_ms=0.0,
        ))

    hall_count = sum(1 for r in results if r.is_hallucinated)
    return BatchResponse(results=results, total=len(results), hallucinated_count=hall_count)


@app.get("/")
async def root():
    return {
        "name": "AB2DETECT API",
        "docs": "/docs",
        "health": "/health",
        "endpoints": ["/detect", "/detect/batch"],
    }
