"""
Jarvis AIOS — Document Intelligence Test Suite
----------------------------------------------

Automated test suite verifying Document Intent Classification, Adaptive Retrieval Planning,
Document Type Detection, Response Planning, Neighbor Chunk Expansion, and Document Intelligence.
"""

from app.RAG.intent_classifier import DocumentIntentClassifier, DocumentIntent
from app.RAG.retrieval_planner import AdaptiveRetrievalPlanner
from app.RAG.response_planner import ResponsePlanner
from app.RAG.document_intelligence import NeighborChunkExpander
from app.RAG.chunker import detect_document_type
from app.RAG.extractors import ExtractedDocument
from app.RAG.repository import RAGRepository


def test_intent_classifier_stage1_rules():
    """Verify Stage 1 Rule Signal Intent Classification."""
    assert DocumentIntentClassifier.classify("What is this PDF about?") == DocumentIntent.OVERVIEW
    assert DocumentIntentClassifier.classify("Summarize this document") == DocumentIntent.SUMMARIZATION
    assert DocumentIntentClassifier.classify("Compare this PDF with that PPT") == DocumentIntent.COMPARISON
    assert DocumentIntentClassifier.classify("Explain slide 5") == DocumentIntent.PRESENTATION
    assert DocumentIntentClassifier.classify("Explain education section") == DocumentIntent.SECTION
    assert DocumentIntentClassifier.classify("What is FastAPI?", has_active_doc=False) == DocumentIntent.Q_AND_A


def test_intent_classifier_stage2_semantic_matching():
    """Verify Stage 2 Semantic Similarity Matching for queries without exact phrases."""
    assert DocumentIntentClassifier.classify("Can you break this down?", has_active_doc=True) == DocumentIntent.OVERVIEW
    assert DocumentIntentClassifier.classify("Give me a deep dive", has_active_doc=True) == DocumentIntent.OVERVIEW
    assert DocumentIntentClassifier.classify("Walk me through the document", has_active_doc=True) == DocumentIntent.OVERVIEW
    assert DocumentIntentClassifier.classify("Explain everything in here", has_active_doc=True) == DocumentIntent.OVERVIEW


def test_adaptive_retrieval_planner_strategies():
    """Verify Adaptive Retrieval Planner generates correct strategy plans."""
    p_ov = AdaptiveRetrievalPlanner.create_plan(DocumentIntent.OVERVIEW, "What is this PDF about?", total_chunks_in_doc=20)
    assert p_ov.strategy == "HIERARCHICAL_OUTLINE"
    assert p_ov.neighbor_window == 1
    assert p_ov.include_all_sections is True

    p_qa = AdaptiveRetrievalPlanner.create_plan(DocumentIntent.Q_AND_A, "What is FastAPI?")
    assert p_qa.strategy == "TOP_K"
    assert p_qa.top_k == 5
    assert p_qa.neighbor_window == 0

    p_sec = AdaptiveRetrievalPlanner.create_plan(DocumentIntent.SECTION, "Explain education section")
    assert p_sec.strategy == "SECTION_FILTER"
    assert "education" in p_sec.target_sections


def test_document_type_detection():
    """Verify Document Type Detection for resume, paper, slides, report."""
    doc_resume = ExtractedDocument(filename="cv.pdf", file_type="pdf", full_text="Virat P K Gupta. Education: B.Tech. Experience: Lead AI Engineer. Skills: Python.", page_count=1)
    assert detect_document_type(doc_resume) == "resume"

    doc_paper = ExtractedDocument(filename="paper.pdf", file_type="pdf", full_text="Abstract: Novel RAG Fusion. Introduction. Methodology. Experiments. Conclusion.", page_count=1)
    assert detect_document_type(doc_paper) == "paper"

    doc_slides = ExtractedDocument(filename="deck.pptx", file_type="pptx", full_text="Slide 1: Overview", page_count=1)
    assert detect_document_type(doc_slides) == "slides"


def test_neighbor_chunk_expander():
    """Verify Neighbor Chunk Expansion expands target indices with [-1, 0, +1] window."""
    all_chunks = [
        {"chunk_id": f"c_{i}", "metadata": {"chunk_sequence": i}, "raw_text": f"Chunk {i}"}
        for i in range(10)
    ]
    target_chunks = [all_chunks[3]]  # Chunk 3

    expanded = NeighborChunkExpander.expand_chunks(target_chunks, all_chunks, window_size=1)
    seqs = [c["metadata"]["chunk_sequence"] for c in expanded]
    assert seqs == [2, 3, 4]


def test_response_planner_layouts():
    """Verify ResponsePlanner generates structured layouts for resume, paper, slides, overview."""
    rp_res = ResponsePlanner.create_response_plan(DocumentIntent.OVERVIEW, document_type="resume")
    assert rp_res.layout_name == "RESUME_LAYOUT"
    assert "Work Experience & Projects" in rp_res.headings

    rp_paper = ResponsePlanner.create_response_plan(DocumentIntent.OVERVIEW, document_type="paper")
    assert rp_paper.layout_name == "RESEARCH_PAPER_LAYOUT"
    assert "Methodology & Architecture" in rp_paper.headings


def test_end_to_end_document_intelligence():
    """Verify end-to-end Document Intelligence pipeline generates structured evidence."""
    repo = RAGRepository()
    kb = repo.create_knowledge_base(name="Intel Test KB", description="Test KB for document intelligence")
    ds = repo.create_dataset(kb_id=kb.id, name="Intel Test Dataset")

    doc = repo.add_document(
        dataset_id=ds.id,
        filename="SYSTEM_ARCHITECTURE.pdf",
        file_type="pdf",
        raw_text="System Architecture Manual. Introduction: Scalable FastAPI microservices. Section 2: Security & Encryption.",
    )
    session_id = "sess_intel_555"
    repo.add_session_attachment(session_id, doc.id, doc.filename, "pdf")

    from app.Jarvis.runtime import _evaluate_tool_and_rag_context
    sys_msgs = _evaluate_tool_and_rag_context("Can you break this down?", session_id=session_id)
    assert len(sys_msgs) == 1
    content = sys_msgs[0].content
    assert "Mode: OVERVIEW" in content
    assert "DOCUMENT INTEL CONTEXT" in content
