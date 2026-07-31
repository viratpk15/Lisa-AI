import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/services/api/apiClient"
import type {
  PromptSummary,
  PromptDetailsResponse,
  PromptVersion,
  PromptFolder,
  PromptTemplate,
  PromptExecution,
  PromptEvaluation,
  PromptAnalyticsResponse,
} from "../types/prompts.types"

export async function fetchPrompts(folderId?: string | null, tag?: string | null, query?: string): Promise<PromptSummary[]> {
  const params = new URLSearchParams()
  if (folderId) params.append("folder_id", folderId)
  if (tag) params.append("tag", tag)
  if (query) params.append("query", query)
  const q = params.toString()
  return apiClient.get<PromptSummary[]>(`/api/v1/prompts${q ? `?${q}` : ""}`)
}

export async function fetchPromptDetails(promptId: string): Promise<PromptDetailsResponse> {
  return apiClient.get<PromptDetailsResponse>(`/api/v1/prompts/${promptId}`)
}

export async function fetchPromptVersions(promptId: string): Promise<PromptVersion[]> {
  return apiClient.get<PromptVersion[]>(`/api/v1/prompts/${promptId}/versions`)
}

export async function fetchFolders(): Promise<PromptFolder[]> {
  return apiClient.get<PromptFolder[]>("/api/v1/prompts/folders")
}

export async function fetchTemplates(): Promise<PromptTemplate[]> {
  return apiClient.get<PromptTemplate[]>("/api/v1/prompts/templates")
}

export async function fetchAnalytics(): Promise<PromptAnalyticsResponse> {
  return apiClient.get<PromptAnalyticsResponse>("/api/v1/prompts/analytics")
}

export async function parseVariablesApi(text: string): Promise<{ variables: string[] }> {
  return apiClient.post<{ variables: string[] }>("/api/v1/prompts/parse-variables", { text })
}

export async function runPlaygroundApi(payload: {
  prompt_id?: string | null
  system_prompt: string
  user_prompt: string
  variables: Record<string, any>
  model: string
  temperature: number
}): Promise<PromptExecution> {
  return apiClient.post<PromptExecution>("/api/v1/prompts/playground/run", payload)
}

export async function comparePromptsApi(payload: {
  system_prompt: string
  user_prompt: string
  variables: Record<string, any>
  models: string[]
}): Promise<{ comparisons: PromptExecution[] }> {
  return apiClient.post<{ comparisons: PromptExecution[] }>("/api/v1/prompts/compare", payload)
}

export async function evaluateExecutionApi(payload: {
  execution_id: string
  correctness: number
  hallucination: number
  tone: number
  clarity: number
  relevance: number
}): Promise<PromptEvaluation> {
  return apiClient.post<PromptEvaluation>("/api/v1/prompts/evaluate", payload)
}

export async function commitVersionApi(
  promptId: string,
  payload: {
    system_prompt: string
    user_prompt: string
    commit_message: string
    model: string
    temperature: number
    top_p: number
    max_tokens: number
  }
): Promise<PromptVersion> {
  return apiClient.post<PromptVersion>(`/api/v1/prompts/${promptId}/versions`, payload)
}

export async function restoreVersionApi(promptId: string, versionId: string): Promise<PromptVersion> {
  return apiClient.post<PromptVersion>(`/api/v1/prompts/${promptId}/restore`, { version_id: versionId })
}

export async function cloneTemplateApi(templateId: string, title?: string): Promise<PromptDetailsResponse> {
  return apiClient.post<PromptDetailsResponse>(`/api/v1/prompts/templates/${templateId}/clone`, { title })
}

export async function aiAssistApi(text: string, action: string): Promise<{ suggested_text: string }> {
  return apiClient.post<{ suggested_text: string }>("/api/v1/prompts/ai-assist", { text, action })
}

// React Query Hooks
export function usePromptsQuery(folderId?: string | null, tag?: string | null, query?: string) {
  return useQuery({
    queryKey: ["prompts", folderId, tag, query],
    queryFn: () => fetchPrompts(folderId, tag, query),
    staleTime: 5 * 60 * 1000,
  })
}

export function usePromptDetailsQuery(promptId: string | null) {
  return useQuery({
    queryKey: ["prompt-details", promptId],
    queryFn: () => fetchPromptDetails(promptId!),
    enabled: Boolean(promptId),
    staleTime: 5 * 60 * 1000,
  })
}

export function usePromptVersionsQuery(promptId: string | null) {
  return useQuery({
    queryKey: ["prompt-versions", promptId],
    queryFn: () => fetchPromptVersions(promptId!),
    enabled: Boolean(promptId),
    staleTime: 5 * 60 * 1000,
  })
}

export function usePromptTemplatesQuery() {
  return useQuery({
    queryKey: ["prompt-templates"],
    queryFn: fetchTemplates,
    staleTime: 10 * 60 * 1000,
  })
}

export function usePromptAnalyticsQuery() {
  return useQuery({
    queryKey: ["prompt-analytics"],
    queryFn: fetchAnalytics,
    staleTime: 5 * 60 * 1000,
  })
}
