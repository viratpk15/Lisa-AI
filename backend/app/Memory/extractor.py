"""
Jarvis AIOS — Automated LLM Memory Extractor
--------------------------------------------

Analyzes completed conversation turns via LLM to extract structured
candidate facts, user preferences, and goals while filtering out greetings,
jokes, and temporary small talk.
"""

import json
import logging
from typing import Any, Dict, List

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from app.LLM.client import llm
from app.Memory.scoring import evaluate_candidate_memory

logger = logging.getLogger(__name__)


EXTRACTION_SYSTEM_PROMPT = """
You are Jarvis Memory Extractor.
Analyze the following conversation turn between a User and AI Assistant.
Extract permanent user facts, tech stack preferences, framework choices, and project goals.

Filter OUT:
- Greetings ("hi", "hello", "good morning")
- Jokes, small talk, and temporary pleasantries
- Transient code debugging snippets

Return a JSON object with key "extracted_memories":
[
  {
    "category": "Preference" | "Goal" | "Fact" | "Project",
    "entity_name": "Short entity name",
    "attribute": "Key details",
    "importance": 0.0 to 1.0 score,
    "confidence": 0.0 to 1.0 score
  }
]
If nothing important is present, return {"extracted_memories": []}.
"""


class MemoryExtractor:
    """LLM-powered memory extraction engine."""

    def __init__(self, llm_client: Any = None):
        self.llm = llm_client or llm

    def extract_from_messages(self, messages: List[BaseMessage]) -> List[Dict[str, Any]]:
        """Extract candidate facts from conversation messages.

        Args:
            messages: List of conversation BaseMessage objects.

        Returns:
            List of validated memory candidate dictionaries that pass the candidate storage gate.
        """
        if not messages:
            return []

        conv_text = "\n".join([f"{msg.type}: {msg.content}" for msg in messages[-6:]])

        try:
            response = self.llm.invoke([
                SystemMessage(content=EXTRACTION_SYSTEM_PROMPT),
                HumanMessage(content=f"Conversation Turn:\n{conv_text}"),
            ])

            content_str = str(response.content).strip()
            # Clean possible markdown wrapping ```json ... ```
            if content_str.startswith("```"):
                content_str = content_str.split("```")[1]
                if content_str.startswith("json"):
                    content_str = content_str[4:].strip()

            parsed = json.loads(content_str)
            raw_memories = parsed.get("extracted_memories", [])

            validated_candidates: List[Dict[str, Any]] = []
            for item in raw_memories:
                name = item.get("entity_name", "Unknown")
                attr = item.get("attribute", "")
                category = item.get("category", "Fact")
                importance = float(item.get("importance", 0.80))
                confidence = float(item.get("confidence", 0.90))

                content_preview = f"{name}: {attr}"
                passes_gate, reason = evaluate_candidate_memory("semantic", content_preview, importance, confidence)

                if passes_gate:
                    validated_candidates.append({
                        "entity_name": name,
                        "category": category,
                        "attribute": attr,
                        "importance_score": importance,
                        "confidence_score": confidence,
                        "status": "validated",
                        "gate_reason": reason,
                    })

            return validated_candidates

        except Exception as exc:
            logger.warning("[MEMORY-EXTRACTOR] LLM extraction error: %s", exc)
            return []


# Global instance
memory_extractor = MemoryExtractor()
