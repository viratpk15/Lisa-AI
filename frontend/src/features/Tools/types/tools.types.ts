/**
 * Jarvis AIOS — Tool Console Type Definitions
 */

export type PermissionLevel = "PUBLIC" | "USER" | "ADMIN" | "SYSTEM" | "INTERNAL"

export type ExecutionStatus = "SUCCESS" | "ERROR" | "PENDING_APPROVAL" | "TIMEOUT" | "CANCELLED" | "PERMISSION_DENIED"

export interface ToolMetadata {
  name: string
  display_name: string
  description: string
  category: string
  tags: string[]
  version: string
  author: string
  permission_level: PermissionLevel
  requires_approval: boolean
  enabled: boolean
  timeout_seconds: number
  supports_streaming: boolean
  supports_async: boolean
  supports_parallel: boolean
  supports_cancellation: boolean
  parameter_schema: Record<string, any>
  output_schema: Record<string, any>
  examples: Array<Record<string, any>>
  icon: string
  documentation_url: string
}

export interface ToolDetailsResponse {
  metadata: ToolMetadata
  schema: Record<string, any>
}

export interface ToolResult {
  tool_name: string
  execution_id: string
  status: ExecutionStatus
  started_at: string
  completed_at: string
  duration_ms: number
  output: any
  structured_output?: Record<string, any> | null
  error?: string | null
  logs: string[]
  warnings: string[]
  metadata: Record<string, any>
}

export interface ConsoleLogEntry {
  id: string
  timestamp: string
  type: "stdout" | "stderr" | "info" | "warning" | "success"
  message: string
  executionId?: string
}

export interface PendingApprovalItem {
  execution_id: string
  tool_name: string
  arguments: Record<string, any>
  requires_approval: boolean
  requested_at: string
}
