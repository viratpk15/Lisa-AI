"""
Jarvis AIOS — Intelligent Memory Engine Integration Tests
---------------------------------------------------------

Verifies candidate scoring gate, recency decay formula, candidate fact extraction,
threshold-filtered memory recall, explainability traces, and lifecycle state management.
"""

from unittest.mock import MagicMock
from langchain_core.messages import HumanMessage, AIMessage

from app.Memory.scoring import (
    calculate_recency_decay,
    calculate_memory_score,
    evaluate_candidate_memory,
)
from app.Memory.extractor import MemoryExtractor
from app.Memory.manager import MemoryManager
from app.Memory import repository


def test_recency_decay_and_scoring_formula():
    decay_0h = calculate_recency_decay(0.0)
    assert decay_0h == 1.0

    decay_10h = calculate_recency_decay(10.0)
    assert 0.85 < decay_10h < 1.0

    decay_100h = calculate_recency_decay(100.0)
    assert decay_100h < decay_10h

    score = calculate_memory_score(
        similarity=0.90,
        importance=0.80,
        confidence=1.0,
        hours_elapsed=2.0,
    )
    assert 0.80 <= score <= 1.0


def test_candidate_scoring_gate():
    # Valid high-value candidate -> Passes gate
    passes, reason = evaluate_candidate_memory("semantic", "Python prefer", 0.90, 0.95)
    assert passes is True
    assert "Passed gate" in reason

    # Low-value small talk candidate -> Fails gate
    passes_low, reason_low = evaluate_candidate_memory("semantic", "Hi", 0.10, 0.20)
    assert passes_low is False
    assert "Rejected" in reason_low


def test_memory_extractor_mock_llm():
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(
        content='''```json
{
  "extracted_memories": [
    {
      "category": "Preference",
      "entity_name": "Primary Language",
      "attribute": "Python 3.12 with FastAPI",
      "importance": 0.95,
      "confidence": 0.98
    },
    {
      "category": "Fact",
      "entity_name": "Temporary Joke",
      "attribute": "Funny meme",
      "importance": 0.10,
      "confidence": 0.20
    }
  ]
}
```'''
    )

    extractor = MemoryExtractor(llm_client=mock_llm)
    messages = [
        HumanMessage(content="I build AI systems in Python using FastAPI."),
        AIMessage(content="Got it! Python and FastAPI are great tools."),
    ]

    candidates = extractor.extract_from_messages(messages)
    assert len(candidates) == 1
    assert candidates[0]["entity_name"] == "Primary Language"
    assert candidates[0]["status"] == "validated"


from app.Data.database import SessionLocal


def test_intelligent_memory_recall_and_explainability():
    db = SessionLocal()
    try:
        manager = MemoryManager()
        user_id = None

        e1 = repository.get_or_create_entity(
            session=db,
            user_id=user_id,
            name="Jarvis Framework",
            category="Architecture",
            attributes_json='{"details": "FastAPI + LangGraph + Tool Engine"}',
        )
        e1.importance_score = 0.95
        e1.confidence_score = 1.0
        e1.status = "active"

        e2 = repository.get_or_create_entity(
            session=db,
            user_id=user_id,
            name="Unrelated Hobby",
            category="Hobby",
            attributes_json='{"details": "Playing guitar"}',
        )
        e2.importance_score = 0.40
        e2.status = "active"
        db.commit()

        # Query matching Jarvis Framework with threshold filtering
        recalled = manager.retrieve_intelligent_memories(
            db=db,
            user_id=user_id,
            query="Jarvis Framework FastAPI LangGraph",
            similarity_threshold=0.20,
            top_k=5,
        )

        assert len(recalled) >= 1
        top_hit = recalled[0]
        assert "Jarvis Framework" in top_hit["content"]
        assert top_hit["final_score"] > 0.50
        assert "explanations" in top_hit
        assert len(top_hit["explanations"]) >= 1
    finally:
        db.close()
