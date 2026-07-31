// frontend/src/features/Memory/types/memory.types.ts

export type MemoryTabType = "timeline" | "graph" | "embeddings" | "recall" | "context" | "debugger" | "semantic"
export type MemoryTierFilterType = "all" | "working" | "conversation" | "episodic" | "semantic" | "long_term"
export type MemoryLifecycleStatus = "candidate" | "validated" | "active" | "compressed" | "archived"

export interface MemoryEntity {
  id: number
  entity_name: string
  entity_category: string
  attributes_json: string | null
  importance_score: number
  confidence_score: number
  status: MemoryLifecycleStatus
  pinned: boolean
  created_at: string
}

export interface ExplainabilityMetrics {
  similarity: number
  importance: number
  confidence: number
  recency_decay: number
}

export interface ExplainabilityTrace {
  memory_id: string
  tier: string
  content: string
  final_score: number
  status: string
  metrics: ExplainabilityMetrics
  explanations: string[]
}

export interface MemoryItem {
  id: string
  session_id: string
  tier: "working" | "conversation" | "episodic" | "semantic" | "long_term"
  content: string
  metadata_json: Record<string, any>
  tokens: number
  ttl_seconds?: number | null
  created_at: string
}

export interface EntityNode {
  id: number
  name: string
  category: string
  attributes: Record<string, any>
  created_at: string
}

export interface RelationEdge {
  id: number
  subject_id: number
  object_id: number
  relation: string
  confidence: number
}

export interface KnowledgeGraphData {
  nodes: EntityNode[]
  edges: RelationEdge[]
}

export interface VectorPoint {
  id: string
  session_id: string
  text_preview: string
  x: number
  y: number
  tier: string
}

export interface RankedMemoryHit {
  memory_id: string
  tier: string
  content: string
  dense_score: number
  sparse_score: number
  rrf_score: number
}

export interface RecallResultsData {
  query: string
  total_hits: number
  latency_ms: number
  results: RankedMemoryHit[]
}

export interface TokenBreakdown {
  system_prompt: number
  conversation_history: number
  recalled_long_term: number
  working_buffer: number
  headroom: number
}

export interface ContextWindowData {
  session_id: string
  max_tokens: number
  used_tokens: number
  headroom: number
  breakdown: TokenBreakdown
  assembled_prompt: string
}

export interface MemoryAnalyticsData {
  session_id: string
  total_items: number
  avg_latency_ms: number
  cache_hit_rate: number
  token_usage_pct: number
  tier_distribution: Record<string, number>
}
