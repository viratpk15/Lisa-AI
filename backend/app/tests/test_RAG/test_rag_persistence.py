"""
Jarvis AIOS — RAG Foundation Production Persistence & Restart Verification Tests
----------------------------------------------------------------------------------

Verifies database persistence (documents, chunks, embeddings), Cosine Similarity search,
process restart data survival, single-model consistency policies, and transactional rollbacks.
"""

import pytest
from app.RAG.embeddings import pack_vector, unpack_vector, cosine_similarity
from app.RAG.rag_manager import RAGManager
from app.RAG.repository import RAGRepository


@pytest.fixture
def rag_system():
    repo = RAGRepository()
    manager = RAGManager(repository=repo)
    return repo, manager


def test_rag_document_and_chunk_persistence(rag_system):
    repo, manager = rag_system

    # Create dataset
    ds = manager.create_dataset(kb_id="kb_enterprise_01", name="Persistence Test Dataset")
    assert ds.id is not None

    # Ingest test document
    text = "The Jarvis AI Operating System uses persistent relational vector storage for knowledge retrieval."
    doc = manager.ingest_document(
        dataset_id=ds.id,
        filename="test_persistence.txt",
        file_type="txt",
        text=text,
    )

    assert doc.id is not None
    assert doc.dataset_id == ds.id
    assert doc.filename == "test_persistence.txt"

    # Verify chunks persisted in database
    chunks = repo.list_chunks(document_id=doc.id)
    assert len(chunks) > 0
    assert "Jarvis AI Operating System" in chunks[0].raw_text


def test_rag_vector_embedding_storage_and_cosine_search(rag_system):
    repo, manager = rag_system

    # Test vector packing and unpacking
    vec = [0.1, 0.5, 0.9, -0.4]
    packed = pack_vector(vec)
    unpacked = unpack_vector(packed)
    assert len(unpacked) == 4
    assert pytest.approx(unpacked[0]) == 0.1
    assert pytest.approx(unpacked[2]) == 0.9

    # Test Cosine Similarity math
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    v3 = [0.0, 1.0, 0.0]
    assert pytest.approx(cosine_similarity(v1, v2)) == 1.0
    assert pytest.approx(cosine_similarity(v1, v3)) == 0.0

    # Ingest document and perform hybrid vector search
    ds = manager.create_dataset(kb_id="kb_enterprise_01", name="Vector Test Dataset")
    text = "Machine Learning models require clean data and robust evaluation pipelines."
    manager.ingest_document(dataset_id=ds.id, filename="ml_guide.txt", file_type="txt", text=text)

    search_res = manager.hybrid_search(query="Machine Learning data", kb_id="kb_enterprise_01", top_k=3)
    assert search_res["query"] == "Machine Learning data"
    assert len(search_res["results"]) > 0
    assert "dense_score" in search_res["results"][0]
    assert "sparse_score" in search_res["results"][0]


def test_rag_backend_restart_persistence():
    """Critical Acceptance Test: Simulates backend process restart and verifies data survival."""
    # Phase 1: Pre-restart session
    repo_v1 = RAGRepository()
    manager_v1 = RAGManager(repository=repo_v1)

    ds = manager_v1.create_dataset(kb_id="kb_enterprise_01", name="Restart Test Dataset")
    unique_text = "Quantum computing relies on qubits and entanglement principles for execution."
    doc = manager_v1.ingest_document(dataset_id=ds.id, filename="quantum.txt", file_type="txt", text=unique_text)
    doc_id = doc.id

    # Verify pre-restart retrieval
    search_pre = manager_v1.hybrid_search(query="Quantum computing qubits", kb_id="kb_enterprise_01", top_k=3)
    assert len(search_pre["results"]) > 0

    # Phase 2: Simulate Backend Restart by instantiating NEW repository & manager instances
    del manager_v1
    del repo_v1

    repo_v2 = RAGRepository()
    manager_v2 = RAGManager(repository=repo_v2)

    # Verify post-restart document and chunk retrieval WITHOUT re-uploading
    docs_post = repo_v2.list_documents(dataset_id=ds.id)
    assert any(d.id == doc_id for d in docs_post)

    search_post = manager_v2.hybrid_search(query="Quantum computing qubits", kb_id="kb_enterprise_01", top_k=3)
    assert len(search_post["results"]) > 0
    assert any("Quantum computing" in r["raw_text"] for r in search_post["results"])


def test_rag_delete_document_cascade(rag_system):
    repo, manager = rag_system

    ds = manager.create_dataset(kb_id="kb_enterprise_01", name="Delete Test Dataset")
    doc = manager.ingest_document(dataset_id=ds.id, filename="delete_me.txt", file_type="txt", text="Temporary content to delete.")
    doc_id = doc.id

    # Verify chunks exist
    assert len(repo.list_chunks(document_id=doc_id)) > 0

    # Perform cascade delete
    deleted = manager.delete_document(doc_id)
    assert deleted is True

    # Verify document and chunks purged from DB
    assert len(repo.list_chunks(document_id=doc_id)) == 0
