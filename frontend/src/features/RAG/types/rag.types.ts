export interface KnowledgeBase {
  id: string
  name: string
  description: string
  default_embedding_model: string
  created_at: string
}

export interface Dataset {
  id: string
  kb_id: string
  name: string
  document_count: number
  created_at: string
}

export interface Document {
  id: string
  dataset_id: string
  filename: string
  file_type: string
  file_size_bytes: number
  storage_path: string
  ingested_at: string
}

export interface Chunk {
  id: string
  document_id: string
  chunk_index: number
  raw_text: string
  token_length: number
  metadata_payload: Record<string, any>
}

export interface RetrievedChunk {
  chunk_id: string
  document_id: string
  raw_text: string
  sparse_score: number
  dense_score: number
  hybrid_score: number
  rerank_score: number
  distance: number
}

export interface HybridSearchResult {
  query: string
  alpha: number
  top_k: number
  latency_ms: number
  results: RetrievedChunk[]
  trace_id: string
}

export interface RAGEvaluation {
  id: string
  trace_id: string
  context_recall: number
  context_precision: number
  faithfulness: number
  answer_relevance: number
  mrr: number
  ndcg: number
  evaluated_at: string
}

export interface KnowledgeGraphData {
  id: string
  kb_id: string
  nodes: Array<{ id: string; label: string; category: string }>
  edges: Array<{ source: string; target: string; relation: string }>
}
