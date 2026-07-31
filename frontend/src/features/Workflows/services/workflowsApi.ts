// frontend/src/features/Workflows/services/workflowsApi.ts

import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/services/api/apiClient"
import { queryKeys } from "@/services/queries/queryKeys"
import type {
  WorkflowDefinition,
  WorkflowCompileResult,
  ExecutionResult,
  WorkflowAnalytics,
  WorkflowTemplate,
  WorkflowNode,
  WorkflowEdge,
} from "../types/workflows.types"

export async function fetchWorkflowsApi(): Promise<WorkflowDefinition[]> {
  return apiClient.get<WorkflowDefinition[]>("/api/v1/workflows")
}

export async function fetchWorkflowDetailApi(workflowId: string): Promise<WorkflowDefinition> {
  return apiClient.get<WorkflowDefinition>(`/api/v1/workflows/${workflowId}`)
}

export async function fetchTemplatesApi(): Promise<WorkflowTemplate[]> {
  return apiClient.get<WorkflowTemplate[]>("/api/v1/workflows/templates")
}

export async function createWorkflowApi(payload: {
  workflow_id: string
  name: string
  description?: string
  nodes?: WorkflowNode[]
  edges?: WorkflowEdge[]
  variables?: Record<string, any>
}): Promise<WorkflowDefinition> {
  return apiClient.post<WorkflowDefinition>("/api/v1/workflows", payload)
}

export async function compileWorkflowApi(workflowId: string): Promise<WorkflowCompileResult> {
  return apiClient.post<WorkflowCompileResult>(`/api/v1/workflows/${workflowId}/compile`, {})
}

export async function executeWorkflowApi(
  workflowId: string,
  inputs: Record<string, any> = {},
  breakpoints: string[] = []
): Promise<ExecutionResult> {
  return apiClient.post<ExecutionResult>(`/api/v1/workflows/${workflowId}/execute`, { inputs, breakpoints })
}

export async function resumeExecutionApi(
  executionId: string,
  action: string,
  inputs: Record<string, any> = {}
): Promise<{ execution_id: string; status: string }> {
  return apiClient.post<{ execution_id: string; status: string }>(
    `/api/v1/workflows/executions/${executionId}/resume`,
    { action, inputs }
  )
}

export async function deleteWorkflowApi(workflowId: string): Promise<{ message: string }> {
  return apiClient.del<{ message: string }>(`/api/v1/workflows/${workflowId}`)
}

export async function fetchWorkflowAnalyticsApi(workflowId: string): Promise<WorkflowAnalytics> {
  return apiClient.get<WorkflowAnalytics>(`/api/v1/workflows/${workflowId}/analytics`)
}

// React Query Hooks
export function useWorkflowsQuery() {
  return useQuery({
    queryKey: queryKeys.workflows.list(),
    queryFn: fetchWorkflowsApi,
  })
}

export function useWorkflowDetailQuery(workflowId: string) {
  return useQuery({
    queryKey: queryKeys.workflows.detail(workflowId),
    queryFn: () => fetchWorkflowDetailApi(workflowId),
    enabled: Boolean(workflowId),
  })
}

export function useWorkflowTemplatesQuery() {
  return useQuery({
    queryKey: queryKeys.workflows.templates(),
    queryFn: fetchTemplatesApi,
  })
}

export function useWorkflowAnalyticsQuery(workflowId: string) {
  return useQuery({
    queryKey: queryKeys.workflows.analytics(workflowId),
    queryFn: () => fetchWorkflowAnalyticsApi(workflowId),
    enabled: Boolean(workflowId),
  })
}
