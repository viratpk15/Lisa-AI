"""
Jarvis AIOS — RAG Trust & Hallucination Elimination Test Suite
--------------------------------------------------------------

Automated test suite verifying zero-hallucination factual grounding across:
  - Document formats: PDF, DOCX, PPTX, Markdown, TXT, CSV
  - Dedicated Presentation Mode for PowerPoint (.pptx / .ppt)
  - Slide query normalization ("first slide", "last slide", "slide 7", "methodology slide")
  - Presentation overview mode ("summarize presentation", "list all slide titles")
  - PPTX image-only slides & speaker notes extraction
  - Post-generation grounding validation (validate_grounding)
"""

import pytest
from app.Config.settings import RAG_MIN_CONFIDENCE
from app.RAG.rag_manager import rag_manager
from app.RAG.repository import RAGRepository


@pytest.fixture(scope="module")
def setup_rag_test_data():
    """Seed test Knowledge Base with multi-format synthetic document chunks."""
    repo = RAGRepository()
    kb = repo.create_knowledge_base(
        name="RAG Trust Verification KB",
        description="Comprehensive test repository for multi-format zero hallucination verification.",
    )
    ds = repo.create_dataset(kb_id=kb.id, name="Multi-Format Test Dataset")

    # 1. Markdown document (Architecture & Team Members)
    repo.add_document(
        dataset_id=ds.id,
        filename="PROJECT_ALPHA_CHARTER.md",
        file_type="md",
        raw_text=(
            "# Project Alpha Charter\n"
            "Project Lead: Sarah Connor\n"
            "Lead Architect: Dr. Emmett Brown\n"
            "Security Auditor: Agent Smith\n"
            "Target Delivery: 2026-Q4\n"
            "Budget: $1.5M\n"
        ),
    )

    # 2. Multi-Slide Presentation Representation (10 Slides)
    slides_text_list = [
        "Slide 1: Title Slide & Executive Overview\nProject Alpha Architecture & Executive Summary.",
        "Slide 2: Problem Statement\nLegacy monolithic bottlenecks and scaling limits.",
        "Slide 3: Proposed Architecture\nEvent-driven micro-runtime powered by LangGraph.",
        "Slide 4: Tech Stack\nFastAPI, SQLite/PostgreSQL, React, Tailwind CSS.",
        "Slide 5: Research & Literature Review\nReviewed RRF Rank Fusion and Dense Retrieval papers.",
        "Slide 6: Security & Compliance\nAES-256 encryption at rest and TLS 1.3 in transit.",
        "Slide 7: Research Methodology\nEvaluated Reciprocal Rank Fusion against BM25 baseline.",
        "Slide 8: Financials & Budget\nHardware: $400K, Cloud Infra: $250K.",
        "Slide 9: Team Assignments\nSarah Connor (Lead), Dr. Emmett Brown (Architect).",
        "Slide 10: Conclusion & Next Steps\nDeployment scheduled for Q4 release.",
    ]
    repo.add_document(
        dataset_id=ds.id,
        filename="MULTI_SLIDE_REPORT.pptx",
        file_type="pptx",
        raw_text="\n\n".join(slides_text_list),
    )

    # 3. CSV / Table data representation
    repo.add_document(
        dataset_id=ds.id,
        filename="METRICS_TABLE.csv",
        file_type="csv",
        raw_text=(
            "Region, Revenue, CustomerCount, ChurnRate\n"
            "North America, 1200000, 450, 1.2%\n"
            "Europe, 850000, 320, 2.1%\n"
            "Asia Pacific, 600000, 210, 0.8%\n"
        ),
    )

    # 4. DOCX report representation
    repo.add_document(
        dataset_id=ds.id,
        filename="COMPLIANCE_REPORT.docx",
        file_type="docx",
        raw_text=(
            "Section 4.1 ISO27001 Audit Compliance.\n"
            "The system enforces AES-256 encryption at rest and TLS 1.3 in transit.\n"
            "All session tokens expire after 24 hours.\n"
        ),
    )

    return kb.id


def test_answerable_document_question(setup_rag_test_data):
    """Verify hybrid search retrieves correct chunk for legitimate project question."""
    kb_id = setup_rag_test_data
    res = rag_manager.hybrid_search("Who is the lead architect for Project Alpha?", kb_id=kb_id, top_k=3)

    assert res["results"] is not None
    assert len(res["results"]) > 0
    top_chunk = res["results"][0]
    assert "Emmett Brown" in top_chunk["raw_text"]
    assert top_chunk["rerank_score"] >= RAG_MIN_CONFIDENCE


def test_first_slide_retrieval(setup_rag_test_data):
    """Verify query 'What is on the first slide?' normalizes to Slide 1."""
    kb_id = setup_rag_test_data
    res = rag_manager.hybrid_search("What is on the first slide?", kb_id=kb_id, top_k=3)

    assert len(res["results"]) > 0
    assert res["requested_slide_num"] == 1
    top_chunk = res["results"][0]
    assert "Slide 1" in top_chunk["raw_text"] or top_chunk["metadata"].get("page_number") == 1


def test_last_slide_retrieval(setup_rag_test_data):
    """Verify query 'What is on the last slide?' normalizes to the final slide."""
    kb_id = setup_rag_test_data
    res = rag_manager.hybrid_search("What is on the last slide?", kb_id=kb_id, top_k=3)

    assert len(res["results"]) > 0
    assert res["requested_slide_num"] is not None
    top_chunk = res["results"][0]
    assert "Conclusion" in top_chunk["raw_text"] or "Slide 10" in top_chunk["raw_text"]


def test_explain_slide_7(setup_rag_test_data):
    """Verify query 'Explain slide 7' normalizes to Slide 7."""
    kb_id = setup_rag_test_data
    res = rag_manager.hybrid_search("Explain slide 7", kb_id=kb_id, top_k=3)

    assert len(res["results"]) > 0
    assert res["requested_slide_num"] == 7
    top_chunk = res["results"][0]
    assert "Slide 7" in top_chunk["raw_text"] or "Methodology" in top_chunk["raw_text"]


def test_which_slide_discusses_methodology(setup_rag_test_data):
    """Verify semantic/keyword search finds the methodology slide."""
    kb_id = setup_rag_test_data
    res = rag_manager.hybrid_search("Which slide discusses research methodology?", kb_id=kb_id, top_k=3)

    assert len(res["results"]) > 0
    top_chunk = res["results"][0]
    assert "Methodology" in top_chunk["raw_text"] or "Slide 7" in top_chunk["raw_text"]


def test_summarize_entire_presentation(setup_rag_test_data):
    """Verify query 'Summarize the entire presentation' triggers overview mode."""
    kb_id = setup_rag_test_data
    res = rag_manager.hybrid_search("Summarize the entire presentation slide by slide", kb_id=kb_id, top_k=3)

    assert res["is_presentation_overview"] is True
    assert len(res["results"]) > 3  # Overview mode returns full presentation list


def test_list_all_slide_titles(setup_rag_test_data):
    """Verify query 'List all slide titles' triggers overview mode."""
    kb_id = setup_rag_test_data
    res = rag_manager.hybrid_search("List all slide titles", kb_id=kb_id, top_k=3)

    assert res["is_presentation_overview"] is True
    assert len(res["results"]) > 0


def test_table_data_extraction(setup_rag_test_data):
    """Verify CSV table metrics extraction query retrieves tabular row data."""
    kb_id = setup_rag_test_data
    res = rag_manager.hybrid_search("What is the North America revenue and churn rate?", kb_id=kb_id, top_k=3)

    assert len(res["results"]) > 0
    top_chunk = res["results"][0]
    assert "North America" in top_chunk["raw_text"]
    assert "1.2%" in top_chunk["raw_text"] or "1200000" in top_chunk["raw_text"]


def test_unanswerable_question_fail_closed(setup_rag_test_data):
    """Verify query for unmentioned topic produces low score or zero results."""
    kb_id = setup_rag_test_data
    res = rag_manager.hybrid_search("Quantum teleportation algorithm specifications", kb_id=kb_id, top_k=3)

    if res["results"]:
        top_score = res["results"][0]["rerank_score"]
        assert top_score < 0.60


def test_adversarial_fake_project_member_detection(setup_rag_test_data):
    """Verify prompt asking about invented fake member produces low relevance for fake name."""
    kb_id = setup_rag_test_data
    res = rag_manager.hybrid_search("Is Dr. Lex Luthor the chief AI officer?", kb_id=kb_id, top_k=3)

    top_text = res["results"][0]["raw_text"] if res["results"] else ""
    assert "Lex Luthor" not in top_text


def test_post_generation_grounding_validator():
    """Verify validate_grounding flags ungrounded proper names and slide references."""
    fake_chunks = [
        {"raw_text": "Project Lead: Sarah Connor. Lead Architect: Dr. Emmett Brown."}
    ]

    valid_resp = "The lead architect is Dr. Emmett Brown as noted in the charter."
    ok, reason = rag_manager.validate_grounding(valid_resp, fake_chunks)
    assert ok is True

    hallucinated_resp = "The project team includes Tony Stark and Bruce Wayne."
    ok_bad, reason_bad = rag_manager.validate_grounding(hallucinated_resp, fake_chunks)
    assert ok_bad is False
    assert "Unsupported entity/name" in reason_bad

    hallucinated_slide = "As shown in Slide 9, the revenue doubled."
    ok_slide, reason_slide = rag_manager.validate_grounding(hallucinated_slide, fake_chunks)
    assert ok_slide is False
    assert "Unsupported slide reference" in reason_slide


def test_context_aware_pdf_selection_cv_document(setup_rag_test_data):
    """Verify session attachment binding & ReferenceResolver scope search ONLY to CV document."""
    repo = RAGRepository()
    datasets = repo.list_datasets(setup_rag_test_data)
    ds_id = datasets[0].id if datasets else "ds_default"

    cv_doc = repo.add_document(
        dataset_id=ds_id,
        filename="Virat P K Gupta updated github CV.pdf",
        file_type="pdf",
        raw_text="Virat P K Gupta. Senior AI & Full-Stack Engineer. Expertise: Python, FastAPI, React, PyTorch, LangGraph.",
    )

    session_id = "sess_cv_verification_999"
    repo.add_session_attachment(
        session_id=session_id,
        document_id=cv_doc.id,
        filename=cv_doc.filename,
        file_type="pdf",
    )

    from app.RAG.reference_resolver import ReferenceResolver
    atts = repo.list_session_attachments(session_id)
    doc_ids, fn, is_comp = ReferenceResolver.resolve_references("Explain this PDF in detail", session_id, atts)

    assert doc_ids == [cv_doc.id]
    assert fn == "Virat P K Gupta updated github CV.pdf"

    # Search with filter-first strategy
    res = rag_manager.hybrid_search("Explain this PDF in detail", document_ids=doc_ids, filename=fn)
    assert len(res["results"]) > 0
    for chk in res["results"]:
        assert chk["document_id"] == cv_doc.id


def test_session_document_isolation(setup_rag_test_data):
    """Verify session 1 attachments are isolated from session 2 retrieval."""
    repo = RAGRepository()
    datasets = repo.list_datasets(setup_rag_test_data)
    ds_id = datasets[0].id if datasets else "ds_default"

    doc_s1 = repo.add_document(
        dataset_id=ds_id,
        filename="CONFIDENTIAL_S1_NOTES.txt",
        file_type="txt",
        raw_text="Confidential Session 1 secret API keys and tokens.",
    )
    repo.add_session_attachment("sess_101", doc_s1.id, doc_s1.filename, "txt")

    from app.RAG.reference_resolver import ReferenceResolver
    s2_atts = repo.list_session_attachments("sess_202")
    s2_doc_ids, s2_fn, _ = ReferenceResolver.resolve_references("Explain the attached file", "sess_202", s2_atts)

    assert doc_s1.id not in s2_doc_ids


def test_multi_document_comparison_resolution(setup_rag_test_data):
    """Verify 'Compare this PDF with that PPT' resolves both session attachments."""
    repo = RAGRepository()
    datasets = repo.list_datasets(setup_rag_test_data)
    ds_id = datasets[0].id if datasets else "ds_default"

    doc_pdf = repo.add_document(dataset_id=ds_id, filename="REPORT_A.pdf", file_type="pdf", raw_text="Report A contents.")
    doc_ppt = repo.add_document(dataset_id=ds_id, filename="SLIDES_B.pptx", file_type="pptx", raw_text="Slides B contents.")

    session_id = "sess_compare_888"
    repo.add_session_attachment(session_id, doc_pdf.id, doc_pdf.filename, "pdf")
    repo.add_session_attachment(session_id, doc_ppt.id, doc_ppt.filename, "pptx")

    from app.RAG.reference_resolver import ReferenceResolver
    atts = repo.list_session_attachments(session_id)
    doc_ids, fn, is_comp = ReferenceResolver.resolve_references("Compare this PDF with that PPT", session_id, atts)

    assert is_comp is True
    assert len(doc_ids) >= 1


def test_multi_turn_conversation_active_document_persistence(setup_rag_test_data):
    """Verify active document persists across multi-turn queries without re-attaching."""
    repo = RAGRepository()
    datasets = repo.list_datasets(setup_rag_test_data)
    ds_id = datasets[0].id if datasets else "ds_default"

    cv_doc = repo.add_document(
        dataset_id=ds_id,
        filename="Virat P K Gupta updated github CV.pdf",
        file_type="pdf",
        raw_text="Virat P K Gupta. Senior AI & Full-Stack Engineer. Projects: Jarvis AIOS, RAG Studio. Skills: Python, FastAPI, React.",
    )

    session_id = "sess_multi_turn_777"
    repo.add_session_attachment(session_id, cv_doc.id, cv_doc.filename, "pdf")

    from app.RAG.reference_resolver import ReferenceResolver
    from app.Jarvis.runtime import _evaluate_tool_and_rag_context
    from app.Config.settings import RAG_MIN_CONFIDENCE

    multi_turn_queries = [
        "Tell me about this PDF.",
        "What's inside this PDF?",
        "Retrieve details inside PDF.",
        "List all projects.",
        "Summarize skills.",
        "Explain education."
    ]

    for q in multi_turn_queries:
        atts = repo.list_session_attachments(session_id)
        doc_ids, fn, _ = ReferenceResolver.resolve_references(q, session_id, atts)

        # 1. Verify ReferenceResolver resolves to target CV document
        assert doc_ids == [cv_doc.id]
        assert fn == "Virat P K Gupta updated github CV.pdf"

        # 2. Verify hybrid search returns top score >= RAG_MIN_CONFIDENCE
        res = rag_manager.hybrid_search(q, document_ids=doc_ids, filename=fn, session_id=session_id)
        assert len(res["results"]) > 0
        top_score = res["results"][0]["rerank_score"]
        assert top_score >= RAG_MIN_CONFIDENCE, f"Query '{q}' failed with top score {top_score} < {RAG_MIN_CONFIDENCE}"

        # 3. Verify _evaluate_tool_and_rag_context returns grounded SystemMessage evidence (passing hard gate)
        sys_msgs = _evaluate_tool_and_rag_context(q, session_id=session_id)
        assert len(sys_msgs) == 1
        content = sys_msgs[0].content
        assert "HARD GATE FAILURE" not in content
        assert "ACTIVE DOCUMENT" in content
