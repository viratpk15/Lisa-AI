// frontend/src/features/Memory/services/memoryApi.ts

import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/services/api/apiClient"
import { queryKeys } from "@/services/queries/queryKeys"
import type {
  MemoryItem,
  KnowledgeGraphData,
  VectorPoint,
  RecallResultsData,
  ContextWindowData,
  MemoryAnalyticsData,
} from "../types/memory.types"

export async function fetchMemoryTimeline(sessionId: string, tier: string = "all"): Promise<MemoryItem[]> {
  return apiClient.get<MemoryItem[]>(`/api/v1/memory/timeline?session_id=${sessionId}&tier=${tier}`)
}

export async function fetchWorkingMemory(sessionId: string): Promise<Record<string, any>> {
  return apiClient.get<Record<string, any>>(`/api/v1/memory/working?session_id=${sessionId}`)
}

export async function flushWorkingMemoryApi(sessionId: string): Promise<{ message: string }> {
  return apiClient.post<{ message: string }>("/api/v1/memory/working/flush", { session_id: sessionId })
}

export async function deleteMemoryItemApi(memoryId: string): Promise<{ message: string }> {
  return apiClient.del<{ message: string }>(`/api/v1/memory/${memoryId}`)
}

export async function fetchKnowledgeGraphApi(): Promise<KnowledgeGraphData> {
  return apiClient.get<KnowledgeGraphData>("/api/v1/memory/graph")
}

export async function addRelationApi(payload: {
  subject_name: string
  subject_category?: string
  predicate: string
  object_name: string
  object_category?: string
}): Promise<any> {
  return apiClient.post<any>("/api/v1/memory/graph/relation", payload)
}

export async function fetchVectorProjections(sessionId: string): Promise<{ session_id: string; points: VectorPoint[] }> {
  return apiClient.get<{ session_id: string; points: VectorPoint[] }>(`/api/v1/memory/embeddings?session_id=${sessionId}`)
}

export async function runRecallSearchApi(payload: {
  session_id: string
  query: string
  top_k: number
  alpha: number
}): Promise<RecallResultsData> {
  return apiClient.post<RecallResultsData>("/api/v1/memory/recall", payload)
}

export async function fetchContextWindowApi(sessionId: string): Promise<ContextWindowData> {
  return apiClient.get<ContextWindowData>(`/api/v1/memory/context-window?session_id=${sessionId}`)
}

export async function compressMemoryApi(payload: { session_id: string; strategy: string }): Promise<any> {
  return apiClient.post<any>("/api/v1/memory/compress", payload)
}

export async function fetchMemoryAnalyticsApi(sessionId: string): Promise<MemoryAnalyticsData> {
  return apiClient.get<MemoryAnalyticsData>(`/api/v1/memory/analytics?session_id=${sessionId}`)
}

// React Query Hooks
export function useMemoryTimelineQuery(sessionId: string, tier: string = "all") {
  return useQuery({
    queryKey: queryKeys.memory.timeline(sessionId, tier),
    queryFn: () => fetchMemoryTimeline(sessionId, tier),
    enabled: Boolean(sessionId),
  })
}

export function useKnowledgeGraphQuery() {
  return useQuery({
    queryKey: queryKeys.memory.graph(),
    queryFn: fetchKnowledgeGraphApi,
  })
}

export function useVectorProjectionsQuery(sessionId: string) {
  return useQuery({
    queryKey: queryKeys.memory.embeddings(sessionId),
    queryFn: () => fetchVectorProjections(sessionId),
    enabled: Boolean(sessionId),
  })
}

export function useContextWindowQuery(sessionId: string) {
  return useQuery({
    queryKey: queryKeys.memory.contextWindow(sessionId),
    queryFn: () => fetchContextWindowApi(sessionId),
    enabled: Boolean(sessionId),
  })
}

export function useMemoryAnalyticsQuery(sessionId: string) {
  return useQuery({
    queryKey: queryKeys.memory.analytics(sessionId),
    queryFn: () => fetchMemoryAnalyticsApi(sessionId),
    enabled: Boolean(sessionId),
  })
}

// ---------------------------------------------------------------------------
// Intelligent Memory Engine — Semantic Entities, Extraction, Explainability
// ---------------------------------------------------------------------------

import type { MemoryEntity, ExplainabilityTrace } from "../types/memory.types"
import { useMutation, useQueryClient } from "@tanstack/react-query"

export async function fetchMemoryEntitiesApi(params?: { q?: string; status?: string }): Promise<MemoryEntity[]> {
  const query = new URLSearchParams()
  if (params?.q) query.set("q", params.q)
  if (params?.status) query.set("status", params.status)
  const qs = query.toString() ? `?${query.toString()}` : ""
  return apiClient.get<MemoryEntity[]>(`/api/v1/memory/entities${qs}`)
}

export async function pinMemoryEntityApi(entityId: number, pinned: boolean): Promise<{ id: number; pinned: boolean }> {
  return apiClient.post<{ id: number; pinned: boolean }>(`/api/v1/memory/entities/${entityId}/pin?pinned=${pinned}`, {})
}

export async function deleteMemoryEntityApi(entityId: number): Promise<{ status: string }> {
  return apiClient.del<{ status: string }>(`/api/v1/memory/entities/${entityId}`)
}

export async function triggerMemoryExtractionApi(sessionId: string): Promise<MemoryEntity[]> {
  return apiClient.post<MemoryEntity[]>(`/api/v1/memory/extract?session_id=${sessionId}`, {})
}

export async function explainMemoryRecallApi(params: {
  query: string
  similarity_threshold?: number
  top_k?: number
}): Promise<ExplainabilityTrace[]> {
  const qs = new URLSearchParams({ query: params.query })
  if (params.similarity_threshold !== undefined) qs.set("similarity_threshold", String(params.similarity_threshold))
  if (params.top_k !== undefined) qs.set("top_k", String(params.top_k))
  return apiClient.post<ExplainabilityTrace[]>(`/api/v1/memory/explain?${qs.toString()}`, {})
}

// React Query hooks
export function useMemoryEntitiesQuery(params?: { q?: string; status?: string }) {
  return useQuery({
    queryKey: ["memory", "entities", params?.q ?? "", params?.status ?? ""],
    queryFn: () => fetchMemoryEntitiesApi(params),
    staleTime: 30_000,
  })
}

export function usePinMemoryEntity() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ entityId, pinned }: { entityId: number; pinned: boolean }) =>
      pinMemoryEntityApi(entityId, pinned),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["memory", "entities"] }),
  })
}

export function useDeleteMemoryEntity() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (entityId: number) => deleteMemoryEntityApi(entityId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["memory", "entities"] }),
  })
}

export function useTriggerMemoryExtraction() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (sessionId: string) => triggerMemoryExtractionApi(sessionId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["memory", "entities"] }),
  })
}

export function useExplainMemoryRecall() {
  return useMutation({
    mutationFn: (params: { query: string; similarity_threshold?: number; top_k?: number }) =>
      explainMemoryRecallApi(params),
  })
}

