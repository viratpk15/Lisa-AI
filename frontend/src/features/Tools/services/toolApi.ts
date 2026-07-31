import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/services/api/apiClient"
import { env } from "@/utils/env"
import type { ToolMetadata, ToolDetailsResponse, ToolResult } from "../types/tools.types"

/**
 * Fetch all registered tools from GET /tools
 */
export async function fetchTools(category?: string | null, tag?: string | null, query?: string): Promise<ToolMetadata[]> {
  const params = new URLSearchParams()
  if (category) params.append("category", category)
  if (tag) params.append("tag", tag)
  if (query) params.append("query", query)

  const queryString = params.toString()
  const endpoint = `/tools${queryString ? `?${queryString}` : ""}`
  return apiClient.get<ToolMetadata[]>(endpoint)
}

/**
 * Fetch unique tool categories from GET /tools/categories
 */
export async function fetchCategories(): Promise<string[]> {
  return apiClient.get<string[]>("/tools/categories")
}

/**
 * Fetch specific tool metadata and OpenAPI schema from GET /tools/{name}
 */
export async function fetchToolDetails(toolName: string): Promise<ToolDetailsResponse> {
  return apiClient.get<ToolDetailsResponse>(`/tools/${toolName}`)
}

/**
 * Execute tool via POST /tools/{name}/execute
 */
export async function executeTool(
  toolName: string,
  args: Record<string, any>,
  callerContext?: Record<string, any>
): Promise<ToolResult> {
  const payload = {
    arguments: args,
    caller_context: callerContext || {},
  }
  return apiClient.post<ToolResult>(`/tools/${toolName}/execute`, payload)
}

/**
 * Stream tool output chunks via SSE POST /tools/{name}/execute/stream
 */
export async function streamTool(
  toolName: string,
  args: Record<string, any>,
  onChunk: (chunk: string) => void,
  onError: (err: string) => void,
  onComplete: () => void
): Promise<void> {
  const token = localStorage.getItem("jarvis_access_token")
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "Accept": "text/event-stream",
  }
  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }

  try {
    const response = await fetch(`${env.apiUrl}/tools/${toolName}/execute/stream`, {
      method: "POST",
      headers,
      body: JSON.stringify({ arguments: args }),
    })

    if (!response.ok) {
      throw new Error(`Streaming failed with status ${response.status}: ${response.statusText}`)
    }

    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error("ReadableStream not supported by response body.")
    }

    const decoder = new TextDecoder()
    let buffer = ""

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split("\n\n")
      buffer = lines.pop() || ""

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const rawData = line.slice(6).trim()
          if (rawData === "[DONE]") {
            onComplete()
            return
          }
          try {
            const parsed = JSON.parse(rawData)
            if (parsed.chunk !== undefined) {
              onChunk(String(parsed.chunk))
            } else if (parsed.error) {
              onError(parsed.error)
            }
          } catch {
            onChunk(rawData)
          }
        }
      }
    }
    onComplete()
  } catch (err: any) {
    onError(err?.message || "An error occurred during tool streaming.")
  }
}

/**
 * React Query Hook for discovery tool list
 */
export function useToolsQuery(category?: string | null, tag?: string | null, query?: string) {
  return useQuery({
    queryKey: ["tools", category, tag, query],
    queryFn: () => fetchTools(category, tag, query),
    staleTime: 5 * 60 * 1000,
  })
}

/**
 * React Query Hook for categories list
 */
export function useCategoriesQuery() {
  return useQuery({
    queryKey: ["tool-categories"],
    queryFn: fetchCategories,
    staleTime: 10 * 60 * 1000,
  })
}

/**
 * React Query Hook for tool details schema
 */
export function useToolDetailsQuery(toolName: string | null) {
  return useQuery({
    queryKey: ["tool-details", toolName],
    queryFn: () => fetchToolDetails(toolName!),
    enabled: Boolean(toolName),
    staleTime: 5 * 60 * 1000,
  })
}
