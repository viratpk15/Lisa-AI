"""
Jarvis AIOS — Memory Scoring, Decay, and Explainability Engine
--------------------------------------------------------------

Calculates multi-factor memory scores, applies recency decay over time,
gates extracted candidate memories before storage, and generates explainability traces.
"""

import math
from typing import Any, Dict, List, Tuple


CANDIDATE_SCORE_GATE_THRESHOLD = 0.50
LAMBDA_DECAY = 0.01  # Decay rate per hour


def calculate_recency_decay(hours_elapsed: float) -> float:
    """Calculate exponential recency decay multiplier: e^(-lambda * hours)."""
    return round(math.exp(-LAMBDA_DECAY * max(0.0, hours_elapsed)), 4)


def calculate_memory_score(
    similarity: float,
    importance: float,
    confidence: float,
    hours_elapsed: float = 0.0,
    alpha: float = 0.40,
    beta: float = 0.30,
    gamma: float = 0.20,
    delta: float = 0.10,
) -> float:
    """Calculate composite memory score:
    score = (alpha * similarity) + (beta * importance) + (gamma * confidence) + (delta * recency_decay)
    """
    decay = calculate_recency_decay(hours_elapsed)
    raw_score = (alpha * similarity) + (beta * importance) + (gamma * confidence) + (delta * decay)
    return round(min(1.0, max(0.0, raw_score)), 4)


def evaluate_candidate_memory(
    memory_type: str,
    content: str,
    importance: float,
    confidence: float,
) -> Tuple[bool, str]:
    """Evaluate whether an extracted candidate memory passes the candidate storage gate.

    Returns:
        Tuple of (passes_gate_boolean, explanation_reason).
    """
    composite = (0.6 * importance) + (0.4 * confidence)
    if composite >= CANDIDATE_SCORE_GATE_THRESHOLD:
        return True, f"Passed gate (score {composite:.2f} >= threshold {CANDIDATE_SCORE_GATE_THRESHOLD})"
    return False, f"Rejected: Low importance/confidence score ({composite:.2f} < threshold {CANDIDATE_SCORE_GATE_THRESHOLD})"


def generate_explainability_trace(
    item_id: str,
    tier: str,
    content: str,
    score: float,
    similarity: float,
    importance: float,
    confidence: float,
    hours_elapsed: float,
    status: str = "active",
) -> Dict[str, Any]:
    """Generate structured explainability trace for a retrieved memory."""
    decay = calculate_recency_decay(hours_elapsed)
    reasons: List[str] = []

    if similarity >= 0.70:
        reasons.append("✓ High semantic relevance to query")
    elif similarity >= 0.50:
        reasons.append("✓ Moderate semantic relevance")

    if importance >= 0.80:
        reasons.append("✓ High user priority/importance")

    if decay >= 0.85:
        reasons.append("✓ Recently created or accessed")
    else:
        reasons.append("⏳ Decayed over time")

    if status == "active":
        reasons.append("✓ Active memory status")

    return {
        "memory_id": item_id,
        "tier": tier,
        "content": content,
        "final_score": score,
        "status": status,
        "metrics": {
            "similarity": round(similarity, 4),
            "importance": round(importance, 4),
            "confidence": round(confidence, 4),
            "recency_decay": decay,
        },
        "explanations": reasons,
    }
