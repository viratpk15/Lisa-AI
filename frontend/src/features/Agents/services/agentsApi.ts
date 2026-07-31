// frontend/src/features/Agents/services/agentsApi.ts
//
// Wires Agent Studio to backend/app/Agents/routers.py (prefix /api/v1/agents).
// Previously this Studio had no API layer at all — every action only mutated
// local component state. All endpoints below require auth (the backend router
// has `dependencies=[Depends(get_current_user)]` applied to the whole router),
// which apiClient already attaches via the stored bearer token.

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/services/api/apiClient"
import { queryKeys } from "@/services/queries/queryKeys"
import type {
  Agent,
  AgentCreatePayload,
  AgentUpdatePayload,
  AgentVersion,
  AgentVersionCreatePayload,
  AgentTeam,
  AgentTeamCreatePayload,
  AgentExecution,
  ExecutionCreatePayload,
} from "../types/agents.types"

// ---------------------------------------------------------------------------
// Agent CRUD
// ---------------------------------------------------------------------------

export async function fetchAgentsApi(offset = 0, limit = 100): Promise<Agent[]> {
  return apiClient.get<Agent[]>(`/api/v1/agents/?offset=${offset}&limit=${limit}`)
}

export async function fetchAgentApi(agentId: number): Promise<Agent> {
  return apiClient.get<Agent>(`/api/v1/agents/${agentId}`)
}

export async function createAgentApi(payload: AgentCreatePayload): Promise<Agent> {
  return apiClient.post<Agent>("/api/v1/agents/", payload)
}

export async function updateAgentApi(agentId: number, payload: AgentUpdatePayload): Promise<Agent> {
  return apiClient.patch<Agent>(`/api/v1/agents/${agentId}`, payload)
}

export async function deleteAgentApi(agentId: number): Promise<void> {
  return apiClient.del<void>(`/api/v1/agents/${agentId}`)
}

// ---------------------------------------------------------------------------
// Versions
// ---------------------------------------------------------------------------

export async function createAgentVersionApi(payload: AgentVersionCreatePayload): Promise<AgentVersion> {
  return apiClient.post<AgentVersion>("/api/v1/agents/versions", payload)
}

export async function fetchAgentVersionsApi(agentId: number): Promise<AgentVersion[]> {
  return apiClient.get<AgentVersion[]>(`/api/v1/agents/${agentId}/versions`)
}

// ---------------------------------------------------------------------------
// Teams
// ---------------------------------------------------------------------------

export async function createAgentTeamApi(payload: AgentTeamCreatePayload): Promise<AgentTeam> {
  return apiClient.post<AgentTeam>("/api/v1/agents/teams", payload)
}

// ---------------------------------------------------------------------------
// Execution
// ---------------------------------------------------------------------------

export async function executeAgentApi(payload: ExecutionCreatePayload): Promise<AgentExecution> {
  return apiClient.post<AgentExecution>("/api/v1/agents/executions", payload)
}

// ---------------------------------------------------------------------------
// React Query hooks
// ---------------------------------------------------------------------------

export function useAgentsQuery(offset = 0, limit = 100) {
  return useQuery({
    queryKey: queryKeys.agents.list(),
    queryFn: () => fetchAgentsApi(offset, limit),
  })
}

export function useAgentQuery(agentId: number | null) {
  return useQuery({
    queryKey: queryKeys.agents.state(String(agentId)),
    queryFn: () => fetchAgentApi(agentId as number),
    enabled: agentId !== null,
  })
}

export function useAgentVersionsQuery(agentId: number | null) {
  return useQuery({
    queryKey: [...queryKeys.agents.all(), "versions", agentId] as const,
    queryFn: () => fetchAgentVersionsApi(agentId as number),
    enabled: agentId !== null,
  })
}

export function useCreateAgentMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createAgentApi,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.agents.list() })
    },
  })
}

export function useUpdateAgentMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ agentId, payload }: { agentId: number; payload: AgentUpdatePayload }) =>
      updateAgentApi(agentId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.agents.list() })
    },
  })
}

export function useDeleteAgentMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: deleteAgentApi,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.agents.list() })
    },
  })
}

export function useCreateAgentTeamMutation() {
  return useMutation({ mutationFn: createAgentTeamApi })
}

export function useExecuteAgentMutation() {
  return useMutation({ mutationFn: executeAgentApi })
}
