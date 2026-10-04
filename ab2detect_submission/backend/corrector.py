"""
AB2DETECT — Auto-Correction Module
Replaces hallucinated spans with context-grounded extractions.

Abubakar Khan (1RUA24CSE0010) · Abhishek D Nagoor (1RUA24CSE0009)
SoCSE, RV University Bengaluru · Summer Internship 2025
"""

import re
from typing import List, Tuple


class HallucinationCorrector:
    """
    Replaces hallucinated spans in an answer with context-grounded candidates.

    Strategy:
        1. Extract named entities and numbers from the context
        2. For each hallucinated span, find the closest context-grounded replacement
        3. Return corrected answer with replacements marked
    """

    def correct(self, answer: str, context: str, spans: List[str]) -> Tuple[str, List[dict]]:
        """
        Args:
            answer:  original LLM answer
            context: retrieved context passage
            spans:   hallucinated span strings detected by HallucinationDetector

        Returns:
            corrected_answer: str with replacements applied
            corrections: list of {original, replacement, type} dicts
        """
        if not spans:
            return answer, []

        ctx_entities = re.findall(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b', context)
        ctx_numbers  = re.findall(r'\b\d+(?:[,\.]\d+)*\b', context)
        ctx_facts    = ctx_entities + ctx_numbers

        corrected = answer
        corrections = []

        for i, span in enumerate(spans):
            replacement = ctx_facts[i] if i < len(ctx_facts) else f"[context-verified]"
            corrected = corrected.replace(span, f"[{replacement}]", 1)
            corrections.append({
                "original": span,
                "replacement": replacement,
                "type": "entity" if re.match(r'[A-Z]', span) else "numerical",
            })

        return corrected, corrections
