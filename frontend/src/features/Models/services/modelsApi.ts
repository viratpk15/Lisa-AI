// frontend/src/features/Models/services/modelsApi.ts

import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/services/api/apiClient"
import { queryKeys } from "@/services/queries/queryKeys"
import type {
  ProviderConfig,
  LLMModelConfig,
  RoutingPolicy,
  BenchmarkRun,
  CostEstimate,
  ModelAnalytics,
} from "../types/models.types"

export async function fetchProvidersApi(): Promise<ProviderConfig[]> {
  return apiClient.get<ProviderConfig[]>("/api/v1/models/providers")
}

export async function registerProviderApi(payload: {
  provider_name: string
  display_name: string
  api_base_url: string
  api_key?: string
  is_enabled?: boolean
}): Promise<ProviderConfig> {
  return apiClient.post<ProviderConfig>("/api/v1/models/providers", payload)
}

export async function deleteProviderApi(providerId: number): Promise<{ message: string }> {
  return apiClient.del<{ message: string }>(`/api/v1/models/providers/${providerId}`)
}

export async function fetchModelRegistryApi(): Promise<LLMModelConfig[]> {
  return apiClient.get<LLMModelConfig[]>("/api/v1/models/registry")
}

export async function registerModelApi(payload: {
  provider_name: string
  model_id: string
  display_name: string
  context_window?: number
  max_output_tokens?: number
  input_cost_per_1k?: number
  output_cost_per_1k?: number
  is_default?: boolean
  routing_priority?: number
}): Promise<LLMModelConfig> {
  return apiClient.post<LLMModelConfig>("/api/v1/models/registry", payload)
}

export async function setDefaultModelApi(modelId: string): Promise<{ model_id: string; is_default: boolean }> {
  return apiClient.patch<{ model_id: string; is_default: boolean }>(`/api/v1/models/registry/${modelId}/default`, {})
}

export async function fetchRoutingPoliciesApi(): Promise<RoutingPolicy[]> {
  return apiClient.get<RoutingPolicy[]>("/api/v1/models/routing-policies")
}

export async function runBenchmarkApi(payload: {
  model_id: string
  prompt_tokens?: number
  completion_tokens?: number
}): Promise<BenchmarkRun> {
  return apiClient.post<BenchmarkRun>("/api/v1/models/benchmark", payload)
}

export async function estimateCostApi(payload: {
  model_id: string
  prompt_tokens: number
  completion_tokens: number
  monthly_requests: number
}): Promise<CostEstimate> {
  return apiClient.post<CostEstimate>("/api/v1/models/cost-estimate", payload)
}

export async function fetchModelAnalyticsApi(): Promise<ModelAnalytics> {
  return apiClient.get<ModelAnalytics>("/api/v1/models/analytics")
}

// React Query Hooks
export function useProvidersQuery() {
  return useQuery({
    queryKey: queryKeys.models.providers(),
    queryFn: fetchProvidersApi,
  })
}

export function useModelRegistryQuery() {
  return useQuery({
    queryKey: queryKeys.models.registry(),
    queryFn: fetchModelRegistryApi,
  })
}

export function useRoutingPoliciesQuery() {
  return useQuery({
    queryKey: queryKeys.models.routingPolicies(),
    queryFn: fetchRoutingPoliciesApi,
  })
}

export function useModelAnalyticsQuery() {
  return useQuery({
    queryKey: queryKeys.models.analytics(),
    queryFn: fetchModelAnalyticsApi,
  })
}
