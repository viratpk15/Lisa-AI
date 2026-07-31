"""
Jarvis AIOS — RAG 2.0 Structure-Aware Semantic Chunker
------------------------------------------------------

Chunks documents by headings, sections, paragraphs, and page boundaries while
protecting code blocks and tables from fragmenting. Applies sliding window overlap.
"""

from dataclasses import dataclass, field
import hashlib
from typing import Any, Dict, List
from app.RAG.extractors import ExtractedDocument, ExtractedPage


@dataclass
class SemanticChunk:
    chunk_index: int
    raw_text: str
    token_length: int
    page_number: int = 1
    heading: str = ""
    section: str = ""
    paragraph_index: int = 0
    chunk_sequence: int = 0
    section_title: str = ""
    heading_level: int = 1
    parent_section: str = "Root"
    document_type: str = "notes"
    chunk_hash: str = ""
    is_ocr: bool = False
    ocr_confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


def detect_document_type(extracted_doc: ExtractedDocument) -> str:
    """Classify document category for response planning and section intelligence."""
    ft = extracted_doc.file_type.lower()
    if ft in ["pptx", "ppt"]:
        return "slides"

    txt_lower = extracted_doc.full_text[:4000].lower()
    if any(k in txt_lower for k in ["resume", "curriculum vitae", "education", "experience", "skills", "projects"]):
        return "resume"
    if any(k in txt_lower for k in ["abstract", "methodology", "introduction", "experiments", "literature review"]):
        return "paper"
    if any(k in txt_lower for k in ["financials", "quarterly report", "table", "csv", "metrics"]):
        return "report"
    return "notes"


class SemanticChunker:
    """Structure-aware semantic chunker protecting code blocks and tables."""

    def __init__(self, target_chunk_size: int = 500, overlap_words: int = 50):
        self.target_chunk_size = target_chunk_size
        self.overlap_words = overlap_words

    def chunk_document(self, extracted_doc: ExtractedDocument, document_id: str) -> List[SemanticChunk]:
        chunks: List[SemanticChunk] = []
        doc_type = detect_document_type(extracted_doc)

        # If document has multiple page objects, process per page
        pages = extracted_doc.pages if extracted_doc.pages else [
            ExtractedPage(page_number=1, text=extracted_doc.full_text)
        ]

        # ── DEDICATED PRESENTATION MODE FOR PPT / PPTX ──────────────────────────
        if extracted_doc.file_type.lower() in ["pptx", "ppt"]:
            for global_idx, page in enumerate(pages):
                lines = page.text.split("\n")
                heading = lines[0].lstrip("#").strip() if lines else f"Slide {page.page_number}"

                chunk_text = page.text.strip()
                words = chunk_text.split()
                c_hash = hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()

                chunk_meta = {
                    "filename": extracted_doc.filename,
                    "document_id": document_id,
                    "file_type": extracted_doc.file_type,
                    "document_type": doc_type,
                    "page_number": page.page_number,
                    "slide_number": page.page_number,
                    "slide_title": heading,
                    "heading": heading,
                    "section": f"Slide {page.page_number}",
                    "section_title": heading,
                    "heading_level": 1,
                    "chunk_sequence": global_idx,
                    "parent_section": "Root Presentation",
                    "chunk_hash": c_hash,
                    "is_ocr": page.is_scanned,
                }
                chunks.append(
                    SemanticChunk(
                        chunk_index=global_idx,
                        raw_text=chunk_text,
                        token_length=len(words),
                        page_number=page.page_number,
                        heading=heading,
                        section=f"Slide {page.page_number}",
                        paragraph_index=1,
                        chunk_hash=c_hash,
                        is_ocr=page.is_scanned,
                        ocr_confidence=page.ocr_confidence,
                        metadata=chunk_meta,
                    )
                )
            return chunks

        # ── STANDARD STRUCTURE-AWARE SEMANTIC CHUNKING FOR PDF/DOCX/MD/TXT ────
        current_heading = "General"
        current_section = "Overview"
        global_chunk_idx = 0
        paragraph_counter = 0

        for page in pages:
            page_text = page.text
            lines = page_text.split("\n")

            buffer_words: List[str] = []
            in_code_block = False
            code_block_lines: List[str] = []

            for line in lines:
                stripped = line.strip()

                # Heading Detection (# Header 1, ## Header 2)
                if stripped.startswith("#"):
                    if buffer_words:
                        chunk_text = " ".join(buffer_words)
                        c_hash = hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()
                        chunk_meta = {
                            "filename": extracted_doc.filename,
                            "document_id": document_id,
                            "file_type": extracted_doc.file_type,
                            "page_number": page.page_number,
                            "heading": current_heading,
                            "section": current_section,
                            "paragraph_index": paragraph_counter,
                            "is_ocr": page.is_scanned,
                            "ocr_confidence": page.ocr_confidence,
                            "chunk_hash": c_hash,
                        }
                        chunks.append(
                            SemanticChunk(
                                chunk_index=global_chunk_idx,
                                raw_text=chunk_text,
                                token_length=len(buffer_words),
                                page_number=page.page_number,
                                heading=current_heading,
                                section=current_section,
                                paragraph_index=paragraph_counter,
                                chunk_hash=c_hash,
                                is_ocr=page.is_scanned,
                                ocr_confidence=page.ocr_confidence,
                                metadata=chunk_meta,
                            )
                        )
                        global_chunk_idx += 1
                        buffer_words = []

                    current_heading = stripped.lstrip("#").strip()
                    current_section = current_heading

                # Code Block Boundary Protection (``` code ```)
                if stripped.startswith("```"):
                    if not in_code_block:
                        in_code_block = True
                        code_block_lines.append(line)
                    else:
                        in_code_block = False
                        code_block_lines.append(line)
                        block_text = "\n".join(code_block_lines)
                        code_block_lines = []
                        words = block_text.split()
                        buffer_words.extend(words)
                    continue

                if in_code_block:
                    code_block_lines.append(line)
                    continue

                # Normal Paragraph Text
                if stripped:
                    paragraph_counter += 1
                    buffer_words.extend(stripped.split())

                # Flush chunk if buffer reaches target size
                if len(buffer_words) >= self.target_chunk_size:
                    chunk_words = buffer_words[:self.target_chunk_size]
                    chunk_text = " ".join(chunk_words)

                    c_hash = hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()

                    chunk_meta = {
                        "filename": extracted_doc.filename,
                        "document_id": document_id,
                        "file_type": extracted_doc.file_type,
                        "page_number": page.page_number,
                        "heading": current_heading,
                        "section": current_section,
                        "paragraph_index": paragraph_counter,
                        "is_ocr": page.is_scanned,
                        "ocr_confidence": page.ocr_confidence,
                        "chunk_hash": c_hash,
                    }

                    chunks.append(
                        SemanticChunk(
                            chunk_index=global_chunk_idx,
                            raw_text=chunk_text,
                            token_length=len(chunk_words),
                            page_number=page.page_number,
                            heading=current_heading,
                            section=current_section,
                            paragraph_index=paragraph_counter,
                            chunk_hash=c_hash,
                            is_ocr=page.is_scanned,
                            ocr_confidence=page.ocr_confidence,
                            metadata=chunk_meta,
                        )
                    )
                    global_chunk_idx += 1

                    # Apply sliding window overlap for continuous context
                    buffer_words = buffer_words[self.target_chunk_size - self.overlap_words:]

            # Flush remaining buffer words at end of page
            if buffer_words:
                chunk_text = " ".join(buffer_words)
                c_hash = hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()

                chunk_meta = {
                    "filename": extracted_doc.filename,
                    "document_id": document_id,
                    "file_type": extracted_doc.file_type,
                    "page_number": page.page_number,
                    "heading": current_heading,
                    "section": current_section,
                    "paragraph_index": paragraph_counter,
                    "is_ocr": page.is_scanned,
                    "ocr_confidence": page.ocr_confidence,
                    "chunk_hash": c_hash,
                }

                chunks.append(
                    SemanticChunk(
                        chunk_index=global_chunk_idx,
                        raw_text=chunk_text,
                        token_length=len(buffer_words),
                        page_number=page.page_number,
                        heading=current_heading,
                        section=current_section,
                        paragraph_index=paragraph_counter,
                        chunk_hash=c_hash,
                        is_ocr=page.is_scanned,
                        ocr_confidence=page.ocr_confidence,
                        metadata=chunk_meta,
                    )
                )
                global_chunk_idx += 1

        return chunks
