"""
AB2DETECT — Core Detection Module
Simulates ModernBERT token-level hallucination classification.
Replace simulate() with real HuggingFace inference when deploying with GPU.

Abubakar Khan (1RUA24CSE0010) · Abhishek D Nagoor (1RUA24CSE0009)
SoCSE, RV University Bengaluru · Summer Internship 2025
"""

import re
import random
from typing import List, Dict, Any


# ─────────────────────────────────────────────────────────────────────────────
# Real ModernBERT inference (uncomment when GPU available)
# ─────────────────────────────────────────────────────────────────────────────
# from transformers import AutoTokenizer, AutoModelForTokenClassification
# import torch
#
# MODEL_NAME = "answerdotai/ModernBERT-base"  # replace with fine-tuned checkpoint
# tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
# model = AutoModelForTokenClassification.from_pretrained(MODEL_NAME)
# model.eval()
#
# def model_predict(context: str, question: str, answer: str) -> List[int]:
#     """Returns per-token labels: 0=supported, 1=hallucinated"""
#     text = f"{context} [SEP] {question} [SEP] {answer}"
#     inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=4096)
#     with torch.no_grad():
#         outputs = model(**inputs)
#     labels = outputs.logits.argmax(dim=-1).squeeze().tolist()
#     return labels


class HallucinationDetector:
    """
    Hallucination detection pipeline.

    Input:  context (str), question (str), answer (str)
    Output: dict with spans, confidence, hall_rate, is_hallucinated

    Architecture:
        [CLS] context [SEP] question [SEP] answer [SEP]
        → ModernBERT encoder
        → Token classification head (label 0: supported, label 1: hallucinated)
        → Span grouping (contiguous label-1 tokens)
    """

    STOPWORDS = {
        'the','a','an','is','are','was','were','be','been','being',
        'have','has','had','do','does','did','will','would','could',
        'should','may','might','shall','can','to','of','in','on',
        'at','by','for','with','from','as','into','about','and',
        'or','but','not','that','this','it','he','she','they',
        'we','you','i','my','your','his','her','their','our',
        'its','s','t','re','ve','ll','d','m',
    }

    def detect(self, context: str, question: str, answer: str) -> Dict[str, Any]:
        """
        Run hallucination detection.

        Returns:
            spans: list of hallucinated span strings
            is_hallucinated: bool
            confidence: float [0, 1]
            token_count: int
            hall_count: int
            hall_rate: float
        """
        spans = self._find_hallucinated_spans(context, answer)
        token_count = len(re.findall(r'\S+', answer))
        hall_count  = len(spans)
        confidence  = max(0.62, min(0.98, 0.98 - hall_count * 0.06))

        return {
            "spans": spans,
            "is_hallucinated": hall_count > 0,
            "confidence": round(confidence, 4),
            "token_count": token_count,
            "hall_count": hall_count,
            "hall_rate": round(hall_count / max(token_count, 1), 4),
        }

    def _find_hallucinated_spans(self, context: str, answer: str) -> List[str]:
        context_tokens = set(re.findall(r'\b\w+\b', context.lower()))
        answer_words   = re.findall(r'\b\w+\b', answer)
        spans = []

        # Word-level context grounding check
        for word in answer_words:
            if (word.lower() not in context_tokens
                    and word.lower() not in self.STOPWORDS
                    and len(word) > 2
                    and random.random() < 0.35):
                spans.append(word)

        # Named entity grounding check
        for ent in re.findall(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b', answer):
            for part in ent.split():
                if (part.lower() not in context_tokens
                        and part not in spans
                        and random.random() < 0.5):
                    spans.append(part)

        # Numerical fact grounding check
        ctx_nums = set(re.findall(r'\b\d+(?:[,\.]\d+)*\b', context))
        for num in re.findall(r'\b\d+(?:[,\.]\d+)*\b', answer):
            if num not in ctx_nums and num not in spans:
                spans.append(num)

        # Deduplicate while preserving order, cap at 6
        seen = list(dict.fromkeys(spans))
        return seen[:6]

    def get_token_labels(self, context: str, answer: str) -> List[Dict]:
        """Returns per-token classification results for debugging."""
        spans = self._find_hallucinated_spans(context, answer)
        tokens = re.findall(r'\S+', answer)
        return [
            {
                "token": tok,
                "label": 1 if any(s.lower() in tok.lower() for s in spans) else 0,
                "status": "hallucinated" if any(s.lower() in tok.lower() for s in spans) else "supported",
            }
            for tok in tokens
        ]
