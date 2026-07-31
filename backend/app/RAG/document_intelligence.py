"""
Jarvis AIOS — Document Intelligence Engine & Performance Tracker
----------------------------------------------------------------

Provides Document Outline Building, Neighbor Chunk Expansion [-1, 0, +1],
Hierarchical Map-Reduce Synthesizer for large documents, and performance metrics tracking.
"""

from dataclasses import dataclass
import logging
from typing import Any, Dict, List, Set

logger = logging.getLogger(__name__)


@dataclass
class DocIntelMetrics:
    intent: str
    strategy: str
    retrieval_time_ms: float = 0.0
    chunks_retrieved_count: int = 0
    prompt_tokens_est: int = 0
    total_response_time_ms: float = 0.0


class DocumentOutlineBuilder:
    """Extracts structural outline (sections, headings, slides) from document chunks."""

    @staticmethod
    def build_outline(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        outline: List[Dict[str, Any]] = []
        seen_sections: Set[str] = set()

        for chk in chunks:
            meta = chk.get("metadata", {})
            sec = meta.get("section") or meta.get("heading") or meta.get("slide_title") or "General"
            pg = meta.get("page_number") or meta.get("slide_number") or 1
            if sec not in seen_sections:
                seen_sections.add(sec)
                outline.append({
                    "title": sec,
                    "page": pg,
                    "first_chunk_id": chk.get("chunk_id"),
                })
        return outline


class NeighborChunkExpander:
    """Expands target retrieved chunk indices to include neighbor chunks [-1, 0, +1]."""

    @staticmethod
    def expand_chunks(
        retrieved_chunks: List[Dict[str, Any]],
        all_doc_chunks: List[Dict[str, Any]],
        window_size: int = 1,
    ) -> List[Dict[str, Any]]:
        if not window_size or not all_doc_chunks or not retrieved_chunks:
            return retrieved_chunks

        # Index all_doc_chunks by sequence, ensuring rerank_score exists
        seq_map: Dict[int, Dict[str, Any]] = {}
        for idx, chk in enumerate(all_doc_chunks):
            seq = chk.get("metadata", {}).get("chunk_sequence", idx)
            item_copy = dict(chk)
            if "rerank_score" not in item_copy:
                item_copy["rerank_score"] = 0.80
            seq_map[seq] = item_copy

        # Overlay scored_results to retain original rerank_scores
        for chk in retrieved_chunks:
            seq = chk.get("metadata", {}).get("chunk_sequence", 0)
            seq_map[seq] = chk

        target_sequences: Set[int] = set()
        for chk in retrieved_chunks:
            seq = chk.get("metadata", {}).get("chunk_sequence", 0)
            for offset in range(-window_size, window_size + 1):
                if (seq + offset) in seq_map:
                    target_sequences.add(seq + offset)

        expanded = [seq_map[s] for s in sorted(target_sequences)]
        logger.info(
            "[NEIGHBOR-EXPANDER] OriginalChunks=%d ExpandedChunks=%d (window=%d)",
            len(retrieved_chunks), len(expanded), window_size
        )
        return expanded


class HierarchicalSynthesizer:
    """Map-reduce chunk aggregator for large documents exceeding context limits."""

    @staticmethod
    def synthesize_outline_context(chunks: List[Dict[str, Any]]) -> str:
        outline = DocumentOutlineBuilder.build_outline(chunks)
        outline_str = "DOCUMENT OUTLINE / STRUCTURE:\n" + "\n".join(
            f"- Section: {o['title']} (Page {o['page']})" for o in outline
        ) + "\n\n"

        evidence_blocks = []
        for idx, r in enumerate(chunks, start=1):
            meta = r.get("metadata", {})
            fn = meta.get("filename", "Document")
            pg = meta.get("page_number") or meta.get("slide_number") or 1
            sec = meta.get("section") or meta.get("heading") or "General"
            evidence_blocks.append(
                f"[Section Chunk {idx}] Source: {fn} | Page: {pg} | Section: {sec}\n"
                f"{r.get('raw_text', '')}"
            )

        return outline_str + "SECTION EVIDENCE DETAILS:\n" + "\n\n".join(evidence_blocks)
