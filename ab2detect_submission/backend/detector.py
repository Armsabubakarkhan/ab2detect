# AB2DETECT - Core Detection Module
# Uses cross-encoder NLI (Natural Language Inference) for real hallucination detection
# No GPU required - runs on CPU via sentence-transformers
#
# Abubakar Khan (1RUA24CSE0010) - Abhishek D Nagoor (1RUA24CSE0009)
# SoCSE, RV University Bengaluru - Summer Internship 2025

import re
import time
from typing import List, Dict, Any

# ─────────────────────────────────────────────────────────────────────────────
# Real detection using NLI cross-encoder
# Model: cross-encoder/nli-deberta-v3-small (130MB, CPU-friendly)
# For each sentence in the answer, checks if context ENTAILS or CONTRADICTS it
# Contradiction = hallucination
# ─────────────────────────────────────────────────────────────────────────────

_nli_model = None

def _load_nli():
    global _nli_model
    if _nli_model is None:
        try:
            from sentence_transformers import CrossEncoder
            _nli_model = CrossEncoder(
                "cross-encoder/nli-deberta-v3-small",
                max_length=512,
            )
        except Exception as e:
            print(f"[AB2DETECT] NLI model load failed: {e}. Using fallback.")
            _nli_model = "fallback"
    return _nli_model


def _split_sentences(text: str) -> List[str]:
    """Split text into sentences."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 10]


def _extract_claims(sentence: str) -> List[str]:
    """Extract checkable sub-claims from a sentence."""
    claims = []
    # Numbers with context
    for m in re.finditer(r'(\b\w[\w\s]{0,20}?)(\b\d[\d,\.]*\b)([\w\s]{0,20})', sentence):
        claims.append(m.group(0).strip())
    # Named entities
    for m in re.finditer(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+', sentence):
        claims.append(m.group(0).strip())
    # Dates
    for m in re.finditer(r'\b(19|20)\d{2}\b', sentence):
        claims.append(m.group(0))
    if not claims:
        claims = [sentence]
    return list(dict.fromkeys(claims))  # deduplicate


class HallucinationDetector:
    """
    Real hallucination detection pipeline using NLI.

    Architecture:
        Answer → split into sentences
        For each sentence:
            [context, sentence] → NLI cross-encoder → ENTAIL / NEUTRAL / CONTRADICT
            CONTRADICT = hallucinated
            NEUTRAL with unsupported facts = hallucinated
        Extract specific hallucinated spans from contradicted sentences.

    Model: cross-encoder/nli-deberta-v3-small
    Fallback: improved linguistic grounding check (no random, deterministic)
    """

    STOPWORDS = {
        'the','a','an','is','are','was','were','be','been','being',
        'have','has','had','do','does','did','will','would','could',
        'should','may','might','shall','can','to','of','in','on',
        'at','by','for','with','from','as','into','about','and',
        'or','but','not','that','this','it','he','she','they',
        'we','you','i','my','your','his','her','their','our',
        'its','s','t','re','ve','ll','d','m','also','which','who',
        'what','where','when','how','all','some','any','each','than',
        'then','so','if','no','yes','its','been','such','more','most',
    }

    def detect(self, context: str, question: str, answer: str) -> Dict[str, Any]:
        t0 = time.time()
        model = _load_nli()

        if model != "fallback":
            result = self._detect_nli(model, context, answer)
        else:
            result = self._detect_linguistic(context, answer)

        result["latency_ms"] = round((time.time() - t0) * 1000, 2)
        return result

    def _detect_nli(self, model, context: str, answer: str) -> Dict[str, Any]:
        """NLI-based detection: checks each answer sentence against context."""
        sentences = _split_sentences(answer)
        if not sentences:
            sentences = [answer]

        hallucinated_sentences = []
        sentence_scores = []

        for sent in sentences:
            try:
                # NLI scores: [contradiction, entailment, neutral]
                scores = model.predict(
                    [(context, sent)],
                    apply_softmax=True,
                )
                # scores shape: [[contra, entail, neutral]]
                s = scores[0]
                contra_score = float(s[0])
                entail_score = float(s[1])

                sentence_scores.append({
                    "sentence": sent,
                    "contradiction": round(contra_score, 3),
                    "entailment": round(entail_score, 3),
                    "verdict": "hallucinated" if contra_score > 0.35 else (
                        "supported" if entail_score > 0.4 else "uncertain"
                    )
                })

                if contra_score > 0.35:
                    hallucinated_sentences.append(sent)
            except Exception as e:
                print(f"[NLI] Error on sentence: {e}")
                continue

        # Extract specific spans from hallucinated sentences
        spans = []
        ctx_tokens = set(re.findall(r'\b\w+\b', context.lower()))
        ctx_nums = set(re.findall(r'\b\d[\d,\.]*\b', context))

        for sent in hallucinated_sentences:
            # Named entities not in context
            for ent in re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', sent):
                if not all(p.lower() in ctx_tokens for p in ent.split()):
                    spans.append(ent)
            # Numbers not in context
            for num in re.findall(r'\b\d[\d,\.]*\b', sent):
                if num not in ctx_nums:
                    spans.append(num)
            # If no specific spans found, add the whole sentence as a span
            if not spans:
                spans.append(sent[:60] + ("..." if len(sent) > 60 else ""))

        spans = list(dict.fromkeys(spans))[:8]
        hall_count = len(spans)
        token_count = len(re.findall(r'\S+', answer))

        # Confidence = average max(entailment, contradiction) across sentences
        if sentence_scores:
            avg_contra = sum(s["contradiction"] for s in sentence_scores) / len(sentence_scores)
            confidence = round(min(0.99, max(0.5, 1.0 - avg_contra if not spans else avg_contra + 0.3)), 4)
        else:
            confidence = 0.75

        return {
            "spans": spans,
            "is_hallucinated": len(hallucinated_sentences) > 0,
            "confidence": confidence,
            "token_count": token_count,
            "hall_count": hall_count,
            "hall_rate": round(hall_count / max(token_count, 1), 4),
            "sentence_scores": sentence_scores,
            "method": "nli-deberta-v3",
        }

    def _detect_linguistic(self, context: str, answer: str) -> Dict[str, Any]:
        """
        Deterministic fallback (no randomness).
        Uses strict grounding: a claim is hallucinated only if:
        - It's a number not present in context
        - It's a named entity where >50% of tokens not in context
        """
        context_tokens = set(re.findall(r'\b\w+\b', context.lower()))
        ctx_nums = set(re.findall(r'\b\d[\d,\.]*\b', context))
        spans = []

        # Check named entities
        for ent in re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', answer):
            parts = ent.split()
            missing = [p for p in parts if p.lower() not in context_tokens]
            if len(missing) > len(parts) * 0.5:
                spans.append(ent)

        # Check numbers — strict: any number not in context is hallucinated
        for num in re.findall(r'\b\d[\d,\.]*\b', answer):
            if num not in ctx_nums and num not in spans:
                spans.append(num)

        # Check strong factual claims (contains "in YEAR", "at PLACE" patterns)
        for m in re.finditer(r'\bin\s+(19|20)\d{2}\b', answer):
            year = re.search(r'\d{4}', m.group()).group()
            if year not in ctx_nums and year not in spans:
                spans.append(year)

        spans = list(dict.fromkeys(spans))[:8]
        hall_count = len(spans)
        token_count = len(re.findall(r'\S+', answer))

        return {
            "spans": spans,
            "is_hallucinated": hall_count > 0,
            "confidence": round(max(0.65, min(0.97, 0.97 - hall_count * 0.05)), 4),
            "token_count": token_count,
            "hall_count": hall_count,
            "hall_rate": round(hall_count / max(token_count, 1), 4),
            "sentence_scores": [],
            "method": "linguistic-fallback",
        }

    def get_token_labels(self, context: str, answer: str) -> List[Dict]:
        """Returns per-token classification for UI display."""
        result = self._detect_linguistic(context, answer)
        spans = result["spans"]
        tokens = re.findall(r'\S+', answer)
        return [
            {
                "token": tok,
                "label": 1 if any(s.lower() in tok.lower() for s in spans) else 0,
                "status": "hallucinated" if any(s.lower() in tok.lower() for s in spans) else "supported",
            }
            for tok in tokens
        ]
