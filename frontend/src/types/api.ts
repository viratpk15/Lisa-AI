/**
 * Jarvis AIOS Canonical Types Registry
 * Strictly typed models matching backend schemas and API payloads.
 */

// Generic API response container
export interface APIResponse<T> {
  data: T
}

// Reusable paginated wrapper
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
  pages: number
}

// User Profile model
export interface User {
  id: number
  email: string
}

// Token Response payload returned upon login
export interface AuthResponse {
  access_token: string
  token_type: string
}

// Message schema inside chats history
export interface Message {
  id: string
  role: "user" | "assistant" | "system"
  content: string
  timestamp: string
}

// Cursor-based paginated messages response schema
export interface PaginatedMessagesResponse {
  messages: Message[]
  next_cursor: number | null
  has_more: boolean
}

// Conversation Thread container
export interface Conversation {
  id: string
  title: string
  preview: string
  time: string
  pinned: boolean
  model: string
  unread: boolean
  group: "Today" | "Yesterday" | "Last Week" | "Older"
  messages: Message[]
}

// Chat request parameters
export interface ChatRequest {
  session_id: string
  message: string
}

// Chat response payload
export interface ConversationResponse {
  response: string
}

// Project/Workspace scopes
export interface Project {
  id: string
  name: string
  description: string
  category: string
  tasksCompleted: number
  tasksTotal: number
  priority: "high" | "medium" | "low"
  status: "in_progress" | "review" | "paused"
  activity: string
}

// AI Agent model mapping LangGraph configurations
export interface Agent {
  id: string
  name: string
  role: string
  status: "idle" | "working" | "waiting" | "completed"
  taskCount: number
  lastExecution: string
  avatarColor: string
  avatarText: string
  activeNode?: string
}

// Telemetry stat items for system status metrics
export interface TelemetryStats {
  status: "nominal" | "warning" | "error"
  uptime: string
  latency: string
  load: string
  memoryAllocated: string
  activeThreads: number
}

// Dashboard statistics aggregation
export interface DashboardResponse {
  status: TelemetryStats
  agents: {
    active: number
    total: number
    standby: number
  }
  memory: {
    allocated: string
    total: string
    loadPercent: number
  }
  tools: {
    count: number
    status: string
  }
}

// Memory block items
export interface MemoryStore {
  session_id: string
  summary: string | null
  vectorCount: number
  lastSynced: string
}

// Attachment file types
export interface Attachment {
  id: string
  name: string
  type: "pdf" | "image" | "zip" | "markdown" | "code"
  sizeBytes?: number
  urlPlaceholder?: string
}

// Health check status
export interface HealthResponse {
  status: string
  version: string
}

// Unified error schema matches backend ErrorResponse details
export interface APIErrorDetails {
  code: string
  message: string
  details?: Record<string, string | string[]>
}

export interface APIErrorResponse {
  error: APIErrorDetails
}

// UI State flags for asynchronous states
export type LoadingState = "idle" | "loading" | "success" | "error"
export type StreamingState = "thinking" | "generating" | "completed"
