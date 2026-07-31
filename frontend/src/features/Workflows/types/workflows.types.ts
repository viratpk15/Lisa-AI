// frontend/src/features/Workflows/types/workflows.types.ts

export type WorkflowTabType = "canvas" | "library" | "analytics" | "debug"

export type WorkflowNodeType =
  | "agent"
  | "tool"
  | "rag"
  | "memory"
  | "model"
  | "condition"
  | "parallel"
  | "loop"
  | "approval"
  | "http"
  | "transform"
  | "code"

export interface WorkflowNodeData {
  label: string
  node_type: WorkflowNodeType
  config: Record<string, any>
}

export interface WorkflowNode {
  id: string
  type: string
  position: { x: number; y: number }
  data: WorkflowNodeData
}

export interface WorkflowEdge {
  id: string
  source: string
  target: string
  label?: string
  condition_expression?: string
}

export interface WorkflowDefinition {
  id: number
  workflow_id: string
  name: string
  description?: string
  is_active: boolean
  nodes: WorkflowNode[]
  edges: WorkflowEdge[]
  variables: Record<string, any>
  definition_json: string
  definition_yaml?: string
  created_at: string
  updated_at: string
}

export interface WorkflowCompileResult {
  workflow_id: string
  is_valid: boolean
  node_count: number
  edge_count: number
  errors: string[]
  warnings: string[]
  compiled_ast: Record<string, any>
}

export interface ExecutionResult {
  execution_id: string
  workflow_id: string
  status: string
  started_at: string
  stream_url: string
}

export interface WorkflowAnalytics {
  workflow_id: string
  total_executions: number
  successful_executions: number
  failed_executions: number
  avg_latency_ms: number
  total_tokens: number
  total_cost: number
}

export interface WorkflowTemplate {
  template_id: string
  name: string
  description: string
  category: string
  node_count: number
}
