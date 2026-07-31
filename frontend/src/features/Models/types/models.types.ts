// frontend/src/features/Models/types/models.types.ts

export type ModelTabType = "registry" | "providers" | "benchmark" | "cost" | "routing" | "analytics"

export interface ProviderConfig {
  id: number
  provider_name: string
  display_name: string
  api_base_url: string
  is_enabled: boolean
  is_healthy: boolean
  latency_ms: float
  has_api_key: boolean
  updated_at: string
}

export type float = number

export interface LLMModelConfig {
  id: number
  provider_id: number
  provider_name: string
  model_id: string
  display_name: string
  context_window: number
  max_output_tokens: number
  input_cost_per_1k: number
  output_cost_per_1k: number
  is_active: boolean
  is_default: boolean
  routing_priority: number
  created_at: string
}

export interface RoutingPolicy {
  id: number
  policy_name: string
  description?: string
  is_active: boolean
  config_json: Record<string, any>
  created_at: string
}

export interface BenchmarkRun {
  id: number
  model_id: string
  prompt_tokens: number
  completion_tokens: number
  total_latency_ms: number
  ttft_ms: number
  status: string
  created_at: string
}

export interface CostEstimate {
  model_id: string
  prompt_cost: number
  completion_cost: number
  total_cost_per_request: number
  estimated_monthly_cost: number
}

export interface ModelAnalytics {
  total_providers: number
  healthy_providers: number
  total_models: number
  default_model: string
  avg_latency_ms: number
  total_benchmark_runs: number
}
