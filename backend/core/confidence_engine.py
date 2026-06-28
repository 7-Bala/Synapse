"""Confidence Engine for deterministic LLM confidence derivation."""


def compute_confidence(confidence_reason: str, finding: str) -> float:
    """Deterministically computes a confidence score (0.0 to 1.0) based on qualitative LLM output.

    Rules for weighting:
    - Official sources / Direct corroboration (+0.9)
    - Ambiguous or partial corroboration (+0.6)
    - Contradictory evidence or 'uncertain' phrasing (+0.3)
    - Default baseline (0.5)

    These rules ensure deterministic reproducibility across runs since the LLM
    text will be constrained by temperature=0.0.
    """

    reason = confidence_reason.lower()

    if "official" in reason or "verified" in reason or "direct" in reason:
        return 0.95
    if "contradict" in reason or "conflict" in reason or "uncertain" in reason:
        return 0.35
    if "partial" in reason or "rumor" in reason or "unverified" in reason:
        return 0.55

    return 0.70
