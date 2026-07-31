import sys
import os
import importlib.util

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)


def load_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = mod
        spec.loader.exec_module(mod)
# Import modules after path setup
from app.RAG.repository import RAGRepository
from app.RAG.rag_manager import RAGManager
from app.main import app
from fastapi.testclient import TestClient
import unittest


class RAGStudioUnitTest(unittest.TestCase):
    def setUp(self):
        self.mgr = RAGManager(repository=RAGRepository())

    def test_list_kbs_and_datasets(self):
        kbs = self.mgr.list_knowledge_bases()
        self.assertGreaterEqual(len(kbs), 1)
        self.assertEqual(kbs[0].name, "Enterprise Architecture KB")

        datasets = self.mgr.list_datasets(kb_id=kbs[0].id)
        self.assertGreaterEqual(len(datasets), 1)
        self.assertEqual(datasets[0].name, "Core Architecture Docs")

    def test_chunking_preview(self):
        sample_text = "Jarvis AIOS is a high performance AI Operating System built with FastAPI, LangGraph, and ChromaDB."
        chunks = self.mgr.preview_chunking(sample_text, chunk_size=5, overlap=1)
        self.assertGreaterEqual(len(chunks), 2)
        self.assertEqual(chunks[0]["chunk_index"], 0)
        self.assertIn("Jarvis", chunks[0]["raw_text"])

    def test_hybrid_search(self):
        res = self.mgr.hybrid_search(query="LangGraph ToolEngine vector", top_k=3, alpha=0.50)
        self.assertIn("query", res)
        self.assertEqual(res["alpha"], 0.50)
        self.assertGreater(len(res["results"]), 0)
        self.assertIn("rerank_score", res["results"][0])

    def test_evaluate_trace(self):
        eval_res = self.mgr.evaluate_rag_trace(
            trace_id="tr_123",
            query="What is Jarvis?",
            response="Jarvis is an AI Operating System.",
            context="Jarvis AIOS orchestrates tools and agents.",
        )
        self.assertGreaterEqual(eval_res.context_recall, 0.90)
        self.assertGreaterEqual(eval_res.faithfulness, 0.90)


class RAGStudioApiTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_api_list_kbs(self):
        res = self.client.get("/api/v1/rag/knowledge-bases")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)

    def test_api_list_datasets(self):
        res = self.client.get("/api/v1/rag/datasets")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)

    def test_api_chunk_preview(self):
        payload = {
            "text": "Jarvis AIOS RAG engine integrates dense vectors and sparse BM25 keywords.",
            "chunk_size": 5,
            "overlap": 1,
            "strategy": "recursive",
        }
        res = self.client.post("/api/v1/rag/chunk-preview", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 2)

    def test_api_hybrid_search(self):
        payload = {
            "query": "LangGraph execution vector index",
            "top_k": 3,
            "alpha": 0.60,
            "use_reranker": True,
        }
        res = self.client.post("/api/v1/rag/hybrid-search", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("results", data)
        self.assertEqual(data["alpha"], 0.60)

    def test_api_analytics(self):
        res = self.client.get("/api/v1/rag/analytics")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_queries", data)

    def test_api_graph(self):
        res = self.client.get("/api/v1/rag/graph?kb_id=kb_enterprise_01")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("nodes", data)
        self.assertIn("edges", data)


class ApiIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "ok")

    def test_file_upload_endpoint(self):
        files = {"file": ("test_doc.pdf", b"PDF dummy content", "application/pdf")}
        # Requires auth header or bypass in test environment
        res = self.client.post("/files/upload", files=files, headers={"Authorization": "Bearer test_token"})
        # Should return 201 or 401 depending on JWT validation
        self.assertIn(res.status_code, [201, 401])


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(RAGStudioUnitTest))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(RAGStudioApiTest))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(ApiIntegrationTest))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
