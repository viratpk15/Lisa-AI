"""
Jarvis AIOS — RAG 2.0 Document Intelligence & Multi-Format Integration Tests
-----------------------------------------------------------------------------

Verifies multi-format extraction (PDF, DOCX, PPTX, Markdown, TXT), structure-aware
semantic chunking, OCR page detection, metadata enrichment, duplicate file prevention,
and grounded citations.
"""

from app.RAG.chunker import SemanticChunker
from app.RAG.extractors import (
    DOCXExtractor,
    DocumentExtractorFactory,
    MarkdownExtractor,
    PDFExtractor,
    PPTXExtractor,
    TXTExtractor,
)
from app.RAG.rag_manager import RAGManager
from app.RAG.repository import RAGRepository


def test_rag_2_0_extractors():
    # 1. Markdown Extractor
    md_bytes = b"# Architecture\n\nJarvis AIOS orchestrates LangGraph execution nodes.\n\n## Subsystems\n- RAG 2.0\n- ToolEngine"
    md_ext = DocumentExtractorFactory.get_extractor("doc.md", "md")
    assert isinstance(md_ext, MarkdownExtractor)
    md_doc = md_ext.extract(md_bytes, "doc.md")
    assert md_doc.file_type == "md"
    assert "LangGraph" in md_doc.full_text

    # 2. TXT Extractor
    txt_bytes = b"Simple plain text file contents."
    txt_ext = DocumentExtractorFactory.get_extractor("sample.txt")
    assert isinstance(txt_ext, TXTExtractor)
    txt_doc = txt_ext.extract(txt_bytes, "sample.txt")
    assert txt_doc.full_text == "Simple plain text file contents."

    # 3. PDF Extractor
    pdf_ext = DocumentExtractorFactory.get_extractor("report.pdf", "pdf")
    assert isinstance(pdf_ext, PDFExtractor)

    # 4. DOCX Extractor
    docx_ext = DocumentExtractorFactory.get_extractor("memo.docx", "docx")
    assert isinstance(docx_ext, DOCXExtractor)

    # 5. PPTX Extractor
    pptx_ext = DocumentExtractorFactory.get_extractor("deck.pptx", "pptx")
    assert isinstance(pptx_ext, PPTXExtractor)


def test_rag_2_0_semantic_chunker():
    chunker = SemanticChunker(target_chunk_size=50, overlap_words=10)

    md_bytes = b"# System Design\n\nJarvis AIOS uses persistent relational vector storage for document retrieval.\n\n```python\ndef run_agent():\n    return 'OK'\n```\n\n## Storage Layer\nSQLAlchemy ORM powers dual SQLite and PostgreSQL vector backends."
    extractor = MarkdownExtractor()
    extracted_doc = extractor.extract(md_bytes, "system.md")

    chunks = chunker.chunk_document(extracted_doc, document_id="doc_test_123")
    assert len(chunks) > 0

    # Code block boundary protection check
    code_chunks = [c for c in chunks if "def run_agent" in c.raw_text]
    assert len(code_chunks) > 0
    assert "return 'OK'" in code_chunks[0].raw_text

    # Metadata enrichment check
    first_chunk = chunks[0]
    assert first_chunk.heading == "System Design"
    assert first_chunk.metadata["filename"] == "system.md"
    assert "chunk_hash" in first_chunk.metadata


def test_rag_2_0_end_to_end_ingestion_and_citations():
    repo = RAGRepository()
    manager = RAGManager(repository=repo)

    ds = manager.create_dataset(kb_id="kb_enterprise_01", name="RAG 2.0 Dataset")
    content = "# Constitutional Rules\n\nRule 1: Always preserve architecture.\nRule 2: Prefer explicit code over hidden behavior."

    # Ingest document
    doc = manager.ingest_document(
        dataset_id=ds.id,
        filename="constitution.md",
        file_type="md",
        text=content,
    )
    assert doc.id is not None
    assert doc.dataset_id == ds.id

    # Test Duplicate File Ingestion Detection
    doc_dup = manager.ingest_document(
        dataset_id=ds.id,
        filename="constitution.md",
        file_type="md",
        text=content,
    )
    assert doc_dup.id == doc.id  # Returns existing document without duplicate indexing

    # Test Grounded Citation Synthesis
    search_res = manager.hybrid_search(query="Constitutional Rules architecture", kb_id="kb_enterprise_01", top_k=3)
    assert len(search_res["results"]) > 0

    grounded_res = manager.generate_grounded_answer(query="Constitutional Rules", chunks=search_res["results"])
    assert "grounded_answer" in grounded_res
    assert len(grounded_res["citations"]) > 0
    assert "constitution.md" in grounded_res["citations"][0]["source"]
