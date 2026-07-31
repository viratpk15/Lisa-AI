import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/services/api/apiClient"
import { queryKeys } from "@/services/queries/queryKeys"
import type {
  KnowledgeBase,
  Dataset,
  Document,
  Chunk,
  HybridSearchResult,
  RAGEvaluation,
  KnowledgeGraphData,
} from "../types/rag.types"

export async function fetchKnowledgeBases(): Promise<KnowledgeBase[]> {
  return apiClient.get<KnowledgeBase[]>("/api/v1/rag/knowledge-bases")
}

// NOTE: the backend has supported creating knowledge bases, datasets, and
// ingesting documents since day one (POST /knowledge-bases, POST /datasets,
// POST /documents/ingest) — but nothing in the frontend ever called them,
// so RAG Studio could only ever list what already existed. These three
// functions were missing entirely; added here.
export async function createKnowledgeBaseApi(payload: { name: string; description?: string }): Promise<KnowledgeBase> {
  return apiClient.post<KnowledgeBase>("/api/v1/rag/knowledge-bases", payload)
}

export async function createDatasetApi(payload: { kb_id: string; name: string }): Promise<Dataset> {
  return apiClient.post<Dataset>("/api/v1/rag/datasets", payload)
}

export async function ingestDocumentApi(payload: {
  dataset_id: string
  filename: string
  file_type?: string
  text: string
}): Promise<Document> {
  const form = new FormData()
  form.append("dataset_id", payload.dataset_id)
  form.append("filename", payload.filename)
  form.append("file_type", payload.file_type ?? "txt")
  form.append("text", payload.text)
  return apiClient.post<Document>("/api/v1/rag/documents/ingest", form)
}

export async function fetchDatasets(kbId?: string | null): Promise<Dataset[]> {
  const url = kbId ? `/api/v1/rag/datasets?kb_id=${kbId}` : "/api/v1/rag/datasets"
  return apiClient.get<Dataset[]>(url)
}

export async function fetchDocuments(datasetId?: string | null): Promise<Document[]> {
  const url = datasetId ? `/api/v1/rag/documents?dataset_id=${datasetId}` : "/api/v1/rag/documents"
  return apiClient.get<Document[]>(url)
}

export async function fetchChunks(documentId?: string | null): Promise<Chunk[]> {
  const url = documentId ? `/api/v1/rag/chunks?document_id=${documentId}` : "/api/v1/rag/chunks"
  return apiClient.get<Chunk[]>(url)
}

export async function previewChunkingApi(payload: {
  text: string
  chunk_size: number
  overlap: number
  strategy: string
}): Promise<any[]> {
  return apiClient.post<any[]>("/api/v1/rag/chunk-preview", payload)
}

export async function runHybridSearchApi(payload: {
  query: string
  kb_id?: string | null
  top_k: number
  alpha: number
  use_reranker: boolean
}): Promise<HybridSearchResult> {
  return apiClient.post<HybridSearchResult>("/api/v1/rag/hybrid-search", payload)
}

export async function fetchRAGAnalytics(): Promise<any> {
  return apiClient.get<any>("/api/v1/rag/analytics")
}

export async function fetchKnowledgeGraph(kbId: string = "kb_enterprise_01"): Promise<KnowledgeGraphData> {
  return apiClient.get<KnowledgeGraphData>(`/api/v1/rag/graph?kb_id=${kbId}`)
}

export async function fetchEvaluations(): Promise<RAGEvaluation[]> {
  return apiClient.get<RAGEvaluation[]>("/api/v1/rag/evaluations")
}

// React Query Hooks — keyed via central queryKeys factory
export function useKnowledgeBasesQuery() {
  return useQuery({
    queryKey: queryKeys.rag.knowledgeBases(),
    queryFn: fetchKnowledgeBases,
  })
}

export function useDatasetsQuery(kbId?: string | null) {
  return useQuery({
    queryKey: queryKeys.rag.datasets(kbId),
    queryFn: () => fetchDatasets(kbId),
  })
}

export function useDocumentsQuery(datasetId?: string | null) {
  return useQuery({
    queryKey: queryKeys.rag.documents(datasetId),
    queryFn: () => fetchDocuments(datasetId),
  })
}

export function useChunksQuery(documentId?: string | null) {
  return useQuery({
    queryKey: queryKeys.rag.chunks(documentId),
    queryFn: () => fetchChunks(documentId),
  })
}

export function useRAGAnalyticsQuery() {
  return useQuery({
    queryKey: queryKeys.rag.analytics(),
    queryFn: fetchRAGAnalytics,
  })
}

export function useKnowledgeGraphQuery(kbId: string = "kb_enterprise_01") {
  return useQuery({
    queryKey: queryKeys.rag.graph(kbId),
    queryFn: () => fetchKnowledgeGraph(kbId),
  })
}

export function useEvaluationsQuery() {
  return useQuery({
    queryKey: queryKeys.rag.evaluations(),
    queryFn: fetchEvaluations,
  })
}

export function useCreateKnowledgeBaseMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createKnowledgeBaseApi,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.rag.knowledgeBases() })
    },
  })
}

export function useCreateDatasetMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createDatasetApi,
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.rag.datasets(variables.kb_id) })
      queryClient.invalidateQueries({ queryKey: queryKeys.rag.datasets(null) })
    },
  })
}

export function useIngestDocumentMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ingestDocumentApi,
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.rag.documents(variables.dataset_id) })
    },
  })
}
