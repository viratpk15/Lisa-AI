/**
 * Jarvis AIOS — Prompt Studio Type Definitions
 */

export interface PromptSummary {
  id: string
  title: string
  description: string
  folder_id?: string | null
  tags: string[]
  is_favorite: boolean
  current_version_id?: string | null
  updated_at: string
}

export interface PromptVersion {
  id: string
  prompt_id: string
  version_tag: string
  commit_message: string
  system_prompt: string
  user_prompt: string
  default_model: string
  temperature: number
  top_p: number
  max_tokens: number
  author: string
  created_at: string
}

export interface PromptDetailsResponse {
  prompt: PromptSummary
  current_version?: PromptVersion | null
  versions: PromptVersion[]
  variables: string[]
}

export interface PromptFolder {
  id: string
  name: string
  parent_id?: string | null
  created_at: string
}

export interface PromptTemplate {
  id: string
  name: string
  category: string
  description: string
  system_prompt: string
  user_prompt: string
  default_variables: Record<string, any>
}

export interface PromptExecution {
  id: string
  prompt_id: string
  version_id?: string | null
  model_used: string
  input_variables: Record<string, any>
  raw_output: string
  latency_ms: number
  prompt_tokens: number
  completion_tokens: number
  total_cost: number
  status: string
  executed_at: string
}

export interface PromptEvaluation {
  id: string
  execution_id: string
  correctness_score: number
  hallucination_score: number
  tone_score: number
  clarity_score: number
  relevance_score: number
  evaluator_type: string
  detailed_feedback: Record<string, any>
  evaluated_at: string
}

export interface PromptAnalyticsResponse {
  total_executions: number
  success_rate: number
  avg_latency_ms: number
  total_cost_usd: number
  model_distribution: Record<string, number>
}
