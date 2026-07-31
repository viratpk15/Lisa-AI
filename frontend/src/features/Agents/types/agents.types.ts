// frontend/src/features/Agents/types/agents.types.ts
// Mirrors backend/app/Agents/schemas.py exactly.

export interface Agent {
  id: number
  name: string
  description: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface AgentCreatePayload {
  name: string
  description?: string | null
}

export interface AgentUpdatePayload {
  name?: string | null
  description?: string | null
  is_active?: boolean | null
}

export interface AgentVersion {
  id: number
  agent_id: number
  version_number: number
  changelog: string | null
  is_current: boolean
  created_at: string
}

export interface AgentVersionCreatePayload {
  agent_id: number
  version_number: number
  changelog?: string | null
}

export interface TeamNodeCreatePayload {
  agent_version_id: number
  position_x?: number
  position_y?: number
}

export interface TeamEdgeCreatePayload {
  source_node_id: number
  target_node_id: number
  condition_json?: string | null
}

export interface AgentTeamCreatePayload {
  agent_id: number
  name: string
  nodes: TeamNodeCreatePayload[]
  edges: TeamEdgeCreatePayload[]
}

export interface AgentTeam {
  id: number
  agent_id: number
  name: string
  nodes: Record<string, unknown>[]
  edges: Record<string, unknown>[]
}

export interface ExecutionCreatePayload {
  version_id: number
  input_payload?: Record<string, unknown> | null
}

export interface AgentExecution {
  id: number
  version_id: number
  status: string
  started_at: string | null
  finished_at: string | null
  run_id: string | null
}
