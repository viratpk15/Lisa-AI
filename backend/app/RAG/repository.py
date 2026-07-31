"""
Jarvis AIOS — Production Persistent RAG Studio Repository Layer
----------------------------------------------------------------

Provides SQL database persistence (SQLite / PostgreSQL) for Knowledge Bases,
Datasets, Documents, Chunks, Vector Embeddings, Traces, and Quality Evaluations.
"""

from datetime import datetime, timezone
import hashlib
import json
import logging
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.Data.base import Base
from app.Data.database import SessionLocal, engine
from app.Data.models import (
    ChunkModel,
    DatasetModel,
    DocumentModel,
    KnowledgeBaseModel,
    RAGEvaluationModel,
    RAGEmbeddingModel,
    RetrievalTraceModel,
    SessionAttachmentModel,
)
from app.RAG.chunker import SemanticChunker
from app.RAG.embeddings import EmbeddingProviderFactory, pack_vector, unpack_vector
from app.RAG.extractors import DocumentExtractorFactory
from app.RAG.models import (
    Chunk,
    Dataset,
    Document,
    KnowledgeBase,
    KnowledgeGraphData,
    RAGEvaluation,
    RetrievalTrace,
)

logger = logging.getLogger(__name__)


class RAGRepository:
    def __init__(self):
        # Create database tables if they do not exist
        try:
            Base.metadata.create_all(bind=engine)
        except Exception as exc:
            logger.warning("[RAG-REPO] Base table creation error: %s", exc)

        self._seed_default_data()

    def _get_session(self) -> Session:
        return SessionLocal()

    def _seed_default_data(self):
        """Idempotently seed default Knowledge Base and documents if database is empty."""
        with self._get_session() as db:
            existing_kb = db.query(KnowledgeBaseModel).filter_by(id="kb_enterprise_01").first()
            if existing_kb:
                return

            kb = KnowledgeBaseModel(
                id="kb_enterprise_01",
                name="Enterprise Architecture KB",
                description="Production documentation and architectural constitutional rules.",
                embedding_provider="local",
                embedding_model="text-embedding-3-small",
                dimensions=1536,
                vector_version=1,
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            db.add(kb)

            ds = DatasetModel(
                id="ds_core_docs",
                kb_id=kb.id,
                name="Core Architecture Docs",
                document_count=2,
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            db.add(ds)

            doc1 = DocumentModel(
                id="doc_arch_01",
                dataset_id=ds.id,
                filename="02_ARCHITECTURE.md",
                file_type="md",
                file_size_bytes=14200,
                storage_path="docs/02_ARCHITECTURE.md",
                checksum="seed_hash_doc1",
                ingested_at=datetime.now(timezone.utc).isoformat(),
            )
            doc2 = DocumentModel(
                id="doc_tools_02",
                dataset_id=ds.id,
                filename="05_TOOL_ENGINE.md",
                file_type="md",
                file_size_bytes=9800,
                storage_path="docs/05_TOOL_ENGINE.md",
                checksum="seed_hash_doc2",
                ingested_at=datetime.now(timezone.utc).isoformat(),
            )
            db.add_all([doc1, doc2])

            provider = EmbeddingProviderFactory.get_provider("local", "text-embedding-3-small", 1536)

            chunks_data = [
                ("chk_arch_01", doc1.id, 0, "Jarvis AIOS runtime orchestrates LangGraph execution nodes and ToolEngine tool invocations.", 18, {"section": "Core Topology"}),
                ("chk_arch_02", doc1.id, 1, "Vector embeddings are stored in persistent relational tables for sub-10ms similarity search.", 22, {"section": "Vector Storage"}),
                ("chk_tools_01", doc2.id, 0, "ToolEngine validates tool parameters against JSON schema before execution.", 15, {"section": "Tool Execution"}),
            ]

            for chk_id, doc_id, idx, text, tokens, meta in chunks_data:
                chk = ChunkModel(
                    id=chk_id,
                    document_id=doc_id,
                    chunk_index=idx,
                    raw_text=text,
                    token_length=tokens,
                    metadata_payload=json.dumps(meta),
                )
                db.add(chk)

                vec = provider.embed_query(text)
                emb = RAGEmbeddingModel(
                    id=f"emb_{chk_id}",
                    chunk_id=chk_id,
                    provider="local",
                    model="text-embedding-3-small",
                    dimensions=1536,
                    version=1,
                    vector_data=pack_vector(vec),
                    vector_store_id="sqlite_vector",
                    created_at=datetime.now(timezone.utc).isoformat(),
                )
                db.add(emb)

            db.commit()

    def list_knowledge_bases(self) -> List[KnowledgeBase]:
        with self._get_session() as db:
            rows = db.query(KnowledgeBaseModel).all()
            return [
                KnowledgeBase(
                    id=r.id,
                    name=r.name,
                    description=r.description or "",
                    default_embedding_model=r.embedding_model,
                    embedding_provider=r.embedding_provider,
                    dimensions=r.dimensions,
                    vector_version=r.vector_version,
                )
                for r in rows
            ]

    def get_knowledge_base(self, kb_id: str) -> Optional[KnowledgeBase]:
        with self._get_session() as db:
            r = db.query(KnowledgeBaseModel).filter_by(id=kb_id).first()
            if not r:
                return None
            return KnowledgeBase(
                id=r.id,
                name=r.name,
                description=r.description or "",
                default_embedding_model=r.embedding_model,
                embedding_provider=r.embedding_provider,
                dimensions=r.dimensions,
                vector_version=r.vector_version,
            )

    def create_knowledge_base(
        self,
        name: str,
        description: str = "",
        default_embedding_model: str = "text-embedding-3-small",
        embedding_provider: str = "local",
        dimensions: int = 1536,
    ) -> KnowledgeBase:
        kb_obj = KnowledgeBase(
            name=name,
            description=description,
            default_embedding_model=default_embedding_model,
            embedding_provider=embedding_provider,
            dimensions=dimensions,
            vector_version=1,
        )
        with self._get_session() as db:
            record = KnowledgeBaseModel(
                id=kb_obj.id,
                name=kb_obj.name,
                description=kb_obj.description,
                embedding_provider=kb_obj.embedding_provider,
                embedding_model=kb_obj.default_embedding_model,
                dimensions=kb_obj.dimensions,
                vector_version=kb_obj.vector_version,
                created_at=kb_obj.created_at.isoformat(),
            )
            db.add(record)
            db.commit()
        return kb_obj

    def list_datasets(self, kb_id: Optional[str] = None) -> List[Dataset]:
        with self._get_session() as db:
            query = db.query(DatasetModel)
            if kb_id:
                query = query.filter_by(kb_id=kb_id)
            rows = query.all()
            return [
                Dataset(
                    id=r.id,
                    kb_id=r.kb_id,
                    name=r.name,
                    document_count=r.document_count,
                )
                for r in rows
            ]

    def create_dataset(self, kb_id: str, name: str) -> Dataset:
        ds_obj = Dataset(kb_id=kb_id, name=name)
        with self._get_session() as db:
            record = DatasetModel(
                id=ds_obj.id,
                kb_id=ds_obj.kb_id,
                name=ds_obj.name,
                document_count=0,
                created_at=ds_obj.created_at.isoformat(),
            )
            db.add(record)
            db.commit()
        return ds_obj

    def list_documents(self, dataset_id: Optional[str] = None) -> List[Document]:
        with self._get_session() as db:
            query = db.query(DocumentModel)
            if dataset_id:
                query = query.filter_by(dataset_id=dataset_id)
            rows = query.all()
            return [
                Document(
                    id=r.id,
                    dataset_id=r.dataset_id,
                    filename=r.filename,
                    file_type=r.file_type,
                    file_size_bytes=r.file_size_bytes,
                    storage_path=r.storage_path,
                    checksum=r.checksum,
                )
                for r in rows
            ]

    def add_document(
        self,
        dataset_id: str,
        filename: str,
        file_type: str,
        raw_text: str,
        checksum: Optional[str] = None,
        file_bytes: Optional[bytes] = None,
    ) -> Document:
        content_bytes = file_bytes or raw_text.encode("utf-8")
        calc_checksum = checksum or hashlib.sha256(content_bytes).hexdigest()

        extractor = DocumentExtractorFactory.get_extractor(filename=filename, file_type=file_type)
        extracted_doc = extractor.extract(file_bytes=content_bytes, filename=filename)

        doc_obj = Document(
            dataset_id=dataset_id,
            filename=filename,
            file_type=file_type,
            file_size_bytes=len(content_bytes),
            checksum=calc_checksum,
            page_count=extracted_doc.page_count,
            is_scanned_pdf=extracted_doc.is_ocr,
        )

        with self._get_session() as db:
            # Check for existing duplicate document in dataset
            existing_doc = db.query(DocumentModel).filter_by(dataset_id=dataset_id, checksum=calc_checksum).first()
            if existing_doc:
                return Document(
                    id=existing_doc.id,
                    dataset_id=existing_doc.dataset_id,
                    filename=existing_doc.filename,
                    file_type=existing_doc.file_type,
                    file_size_bytes=existing_doc.file_size_bytes,
                    storage_path=existing_doc.storage_path,
                    checksum=existing_doc.checksum,
                    page_count=existing_doc.page_count,
                )

            ds = db.query(DatasetModel).filter_by(id=dataset_id).first()
            kb = db.query(KnowledgeBaseModel).filter_by(id=ds.kb_id).first() if ds else None

            provider_name = kb.embedding_provider if kb else "local"
            model_name = kb.embedding_model if kb else "text-embedding-3-small"
            dims = kb.dimensions if kb else 1536

            provider = EmbeddingProviderFactory.get_provider(provider_name, model_name, dims)

            try:
                doc_record = DocumentModel(
                    id=doc_obj.id,
                    dataset_id=dataset_id,
                    filename=filename,
                    file_type=file_type,
                    file_size_bytes=doc_obj.file_size_bytes,
                    storage_path=f"data/{doc_obj.id}_{filename}",
                    checksum=calc_checksum,
                    page_count=extracted_doc.page_count,
                    ingested_at=doc_obj.ingested_at.isoformat(),
                )
                db.add(doc_record)

                chunker = SemanticChunker(target_chunk_size=400, overlap_words=40)
                semantic_chunks = chunker.chunk_document(extracted_doc, doc_obj.id)

                chunk_records = []
                chunk_texts = []

                for sc in semantic_chunks:
                    chunk_texts.append(sc.raw_text)
                    chk = ChunkModel(
                        id=f"chk_{doc_obj.id}_{sc.chunk_index}",
                        document_id=doc_obj.id,
                        chunk_index=sc.chunk_index,
                        raw_text=sc.raw_text,
                        token_length=sc.token_length,
                        chunk_hash=sc.chunk_hash,
                        metadata_payload=json.dumps(sc.metadata),
                    )
                    db.add(chk)
                    chunk_records.append(chk)

                # Generate vector embeddings
                vectors = provider.embed_documents(chunk_texts)

                for chk_record, vec in zip(chunk_records, vectors):
                    emb_record = RAGEmbeddingModel(
                        id=f"emb_{chk_record.id}",
                        chunk_id=chk_record.id,
                        provider=provider.provider_name,
                        model=provider.model_name,
                        dimensions=provider.dimensions,
                        version=provider.version,
                        vector_data=pack_vector(vec),
                        vector_store_id="sqlite_vector",
                        created_at=datetime.now(timezone.utc).isoformat(),
                    )
                    db.add(emb_record)

                if ds:
                    ds.document_count += 1

                db.commit()
            except Exception as exc:
                db.rollback()
                logger.error("[RAG-REPO] Transaction failed during document ingestion; rolled back: %s", exc)
                raise exc

        return doc_obj

    def delete_document(self, document_id: str) -> bool:
        with self._get_session() as db:
            doc = db.query(DocumentModel).filter_by(id=document_id).first()
            if not doc:
                return False
            ds = db.query(DatasetModel).filter_by(id=doc.dataset_id).first()
            if ds and ds.document_count > 0:
                ds.document_count -= 1
            db.delete(doc)
            db.commit()
            return True

    def list_chunks(self, document_id: Optional[str] = None) -> List[Chunk]:
        with self._get_session() as db:
            query = db.query(ChunkModel)
            if document_id:
                query = query.filter_by(document_id=document_id)
            rows = query.all()
            res = []
            for r in rows:
                meta = json.loads(r.metadata_payload) if r.metadata_payload else {}
                res.append(
                    Chunk(
                        id=r.id,
                        document_id=r.document_id,
                        chunk_index=r.chunk_index,
                        raw_text=r.raw_text,
                        token_length=r.token_length,
                        metadata_payload=meta,
                    )
                )
            return res

    def list_embeddings_with_chunks(
        self,
        kb_id: Optional[str] = None,
        document_id: Optional[str] = None,
        document_ids: Optional[List[str]] = None,
        filename: Optional[str] = None,
    ) -> List[Dict]:
        """Fetch joined chunk texts and unpacked float vector embeddings with early SQL filtering."""
        with self._get_session() as db:
            query = db.query(ChunkModel, RAGEmbeddingModel)
            query = query.join(RAGEmbeddingModel, ChunkModel.id == RAGEmbeddingModel.chunk_id)

            if document_id:
                query = query.filter(ChunkModel.document_id == document_id)
            elif document_ids:
                query = query.filter(ChunkModel.document_id.in_(document_ids))

            if filename:
                query = query.join(DocumentModel, ChunkModel.document_id == DocumentModel.id)
                query = query.filter(DocumentModel.filename == filename)
            elif kb_id and not document_id and not document_ids:
                query = query.join(DocumentModel, ChunkModel.document_id == DocumentModel.id)
                query = query.join(DatasetModel, DocumentModel.dataset_id == DatasetModel.id)
                query = query.filter(DatasetModel.kb_id == kb_id)

            results = []
            for chk, emb in query.all():
                results.append({
                    "chunk_id": chk.id,
                    "document_id": chk.document_id,
                    "raw_text": chk.raw_text,
                    "token_length": chk.token_length,
                    "metadata": json.loads(chk.metadata_payload) if chk.metadata_payload else {},
                    "provider": emb.provider,
                    "model": emb.model,
                    "dimensions": emb.dimensions,
                    "version": emb.version,
                    "vector": unpack_vector(emb.vector_data),
                })
            return results

    def add_session_attachment(
        self,
        session_id: str,
        document_id: str,
        filename: str,
        file_type: str,
    ) -> Dict[str, Any]:
        import uuid
        att_id = f"att_{uuid.uuid4().hex[:8]}"
        now_str = datetime.now(timezone.utc).isoformat()
        with self._get_session() as db:
            att = SessionAttachmentModel(
                id=att_id,
                session_id=session_id,
                document_id=document_id,
                filename=filename,
                file_type=file_type,
                created_at=now_str,
            )
            db.add(att)
            db.commit()
            return {
                "id": att_id,
                "session_id": session_id,
                "document_id": document_id,
                "filename": filename,
                "file_type": file_type,
                "created_at": now_str,
            }

    def list_session_attachments(self, session_id: str) -> List[Dict[str, Any]]:
        with self._get_session() as db:
            rows = db.query(SessionAttachmentModel).filter_by(session_id=session_id).all()
            return [
                {
                    "id": r.id,
                    "session_id": r.session_id,
                    "document_id": r.document_id,
                    "filename": r.filename,
                    "file_type": r.file_type,
                    "created_at": r.created_at,
                }
                for r in rows
            ]

    def add_trace(self, trace: RetrievalTrace):
        with self._get_session() as db:
            record = RetrievalTraceModel(
                id=trace.id,
                kb_id=trace.kb_id,
                raw_query=trace.raw_query,
                alpha_used=trace.alpha_used,
                top_k_requested=trace.top_k_requested,
                latency_ms=trace.latency_ms,
                executed_at=trace.executed_at.isoformat(),
            )
            db.add(record)
            db.commit()

    def list_traces(self) -> List[RetrievalTrace]:
        with self._get_session() as db:
            rows = db.query(RetrievalTraceModel).all()
            return [
                RetrievalTrace(
                    id=r.id,
                    kb_id=r.kb_id,
                    raw_query=r.raw_query,
                    alpha_used=r.alpha_used,
                    top_k_requested=r.top_k_requested,
                    latency_ms=r.latency_ms,
                )
                for r in rows
            ]

    def add_evaluation(self, eval_data: RAGEvaluation):
        with self._get_session() as db:
            record = RAGEvaluationModel(
                id=eval_data.id,
                trace_id=eval_data.trace_id,
                context_recall=eval_data.context_recall,
                context_precision=eval_data.context_precision,
                faithfulness=eval_data.faithfulness,
                answer_relevance=eval_data.answer_relevance,
                mrr=eval_data.mrr,
                ndcg=eval_data.ndcg,
                evaluated_at=eval_data.evaluated_at.isoformat(),
            )
            db.add(record)
            db.commit()

    def list_evaluations(self) -> List[RAGEvaluation]:
        with self._get_session() as db:
            rows = db.query(RAGEvaluationModel).all()
            return [
                RAGEvaluation(
                    id=r.id,
                    trace_id=r.trace_id,
                    context_recall=r.context_recall,
                    context_precision=r.context_precision,
                    faithfulness=r.faithfulness,
                    answer_relevance=r.answer_relevance,
                    mrr=r.mrr,
                    ndcg=r.ndcg,
                )
                for r in rows
            ]

    def get_knowledge_graph(self, kb_id: str) -> KnowledgeGraphData:
        nodes = [
            {"id": "Jarvis_AIOS", "label": "Jarvis AIOS", "category": "System"},
            {"id": "LangGraph", "label": "LangGraph Engine", "category": "Orchestrator"},
            {"id": "RAG_Subsystem", "label": "RAG Subsystem", "category": "Module"},
            {"id": "SQLPersistence", "label": "SQL Vector Persistence", "category": "Storage"},
            {"id": "ToolEngine", "label": "Tool Engine", "category": "Executor"},
        ]
        edges = [
            {"source": "Jarvis_AIOS", "target": "LangGraph", "relation": "uses"},
            {"source": "Jarvis_AIOS", "target": "RAG_Subsystem", "relation": "includes"},
            {"source": "RAG_Subsystem", "target": "SQLPersistence", "relation": "indexes into"},
            {"source": "LangGraph", "target": "ToolEngine", "relation": "invokes"},
        ]
        return KnowledgeGraphData(kb_id=kb_id, nodes=nodes, edges=edges)
