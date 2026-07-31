# backend/app/tests/test_Memory/test_memory_studio.py
"""
Jarvis AIOS — Memory Studio Unit Tests (Sprint 6.5B).

Tests cover:
- Working Memory operations
- Timeline stream generation
- Semantic Knowledge Graph entity-relation creation
- Hybrid RRF recall calculation
- Context Window token budget breakdown
- Memory compression strategy
- Analytics & data export/import
"""

import pytest
from unittest.mock import MagicMock

from app.Memory.manager import MemoryManager


@pytest.fixture
def memory_mgr():
    return MemoryManager()


@pytest.fixture
def mock_db():
    return MagicMock()


class TestWorkingMemory:
    def test_get_working_memory_default(self, memory_mgr):
        wm = memory_mgr.get_working_memory("sess_test_1")
        assert "scratchpad" in wm
        assert wm["active_tool"] is None

    def test_update_and_flush_working_memory(self, memory_mgr):
        memory_mgr.update_working_memory("sess_test_1", {"active_tool": "chroma_search"})
        wm = memory_mgr.get_working_memory("sess_test_1")
        assert wm["active_tool"] == "chroma_search"

        memory_mgr.flush_working_memory("sess_test_1")
        wm_flushed = memory_mgr.get_working_memory("sess_test_1")
        assert wm_flushed["active_tool"] is None


class TestTimelineAndInspector:
    def test_get_timeline_includes_working_memory(self, memory_mgr, mock_db):
        mock_db.scalars.return_value.all.return_value = []
        timeline = memory_mgr.get_timeline(mock_db, session_id="sess_test_2", tier_filter="all")
        assert isinstance(timeline, list)
        assert len(timeline) >= 1
        assert timeline[0]["tier"] == "working"


class TestKnowledgeGraph:
    def test_get_knowledge_graph_fallback(self, memory_mgr, mock_db):
        mock_db.scalars.return_value.all.return_value = []
        graph = memory_mgr.get_knowledge_graph(mock_db)
        assert "nodes" in graph
        assert "edges" in graph
        assert len(graph["nodes"]) >= 3


class TestVectorProjectionAndRecall:
    def test_get_vector_projections(self, memory_mgr, mock_db):
        mock_db.scalars.return_value.all.return_value = []
        points = memory_mgr.get_vector_projections(mock_db, session_id="sess_test_3")
        assert isinstance(points, list)
        assert len(points) >= 1

    def test_recall_hybrid_calculation(self, memory_mgr, mock_db):
        mock_db.scalars.return_value.all.return_value = []
        res = memory_mgr.recall_hybrid(mock_db, session_id="sess_test_4", query="vector search", top_k=3, alpha=0.5)
        assert res["query"] == "vector search"
        assert "results" in res


class TestContextWindowAndCompression:
    def test_get_context_window_budget(self, memory_mgr, mock_db):
        mock_db.scalars.return_value.all.return_value = []
        ctx = memory_mgr.get_context_window(mock_db, session_id="sess_test_5", max_tokens=8192)
        assert ctx["max_tokens"] == 8192
        assert "breakdown" in ctx
        assert "assembled_prompt" in ctx

    def test_compress_memory(self, memory_mgr, mock_db):
        mock_db.scalars.return_value.all.return_value = []
        status = memory_mgr.compress_memory(mock_db, session_id="sess_test_6", strategy="summarize")
        assert status["status"] == "success"
        assert status["compressed_tokens"] < status["original_tokens"]


class TestAnalyticsAndDataOps:
    def test_get_analytics(self, memory_mgr, mock_db):
        mock_db.scalars.return_value.all.return_value = []
        analytics = memory_mgr.get_analytics(mock_db, session_id="sess_test_7")
        assert "total_items" in analytics
        assert "cache_hit_rate" in analytics

    def test_export_and_import(self, memory_mgr, mock_db):
        mock_db.scalars.return_value.all.return_value = []
        exp = memory_mgr.export_memory(mock_db, session_id="sess_test_8")
        assert "version" in exp

        imp = memory_mgr.import_memory(mock_db, session_id="sess_test_8", payload=exp)
        assert imp["status"] == "success"
