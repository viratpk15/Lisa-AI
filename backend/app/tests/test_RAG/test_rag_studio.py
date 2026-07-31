"""
Unit Tests for RAG Studio Subsystem (RAGManager & RAGRepository)
"""

import pytest
from app.RAG.rag_manager import RAGManager
from app.RAG.repository import RAGRepository


@pytest.fixture
def rag_manager():
    return RAGManager(repository=RAGRepository())


def test_list_knowledge_bases_and_datasets(rag_manager):
    kbs = rag_manager.list_knowledge_bases()
    assert len(kbs) >= 1
    assert kbs[0].name == "Enterprise Architecture KB"

    datasets = rag_manager.list_datasets(kb_id=kbs[0].id)
    assert len(datasets) >= 1
    assert datasets[0].name == "Core Architecture Docs"


def test_chunking_preview(rag_manager):
    sample_text = "Jarvis AIOS is a high performance AI Operating System built with FastAPI, LangGraph, and ChromaDB."
    chunks = rag_manager.preview_chunking(sample_text, chunk_size=5, overlap=1)
    assert len(chunks) >= 2
    assert chunks[0]["chunk_index"] == 0
    assert "Jarvis" in chunks[0]["raw_text"]


def test_hybrid_search_fusion(rag_manager):
    res = rag_manager.hybrid_search(query="LangGraph ToolEngine vector", top_k=3, alpha=0.50)
    assert "query" in res
    assert res["alpha"] == 0.50
    assert len(res["results"]) > 0
    assert "rerank_score" in res["results"][0]


def test_evaluate_rag_trace(rag_manager):
    eval_res = rag_manager.evaluate_rag_trace(
        trace_id="tr_123",
        query="What is Jarvis?",
        response="Jarvis is an AI Operating System.",
        context="Jarvis AIOS orchestrates tools and agents.",
    )
    assert eval_res.context_recall >= 0.90
    assert eval_res.faithfulness >= 0.90
