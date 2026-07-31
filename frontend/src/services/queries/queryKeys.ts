/**
 * Query Key Factory Registry
 * Centralizes query keys used by TanStack Query, eliminating magic strings.
 */
export const queryKeys = {
  auth: {
    all: () => ["auth"] as const,
    profile: () => ["auth", "profile"] as const
  },
  
  health: {
    all: () => ["health"] as const,
    status: () => ["health", "status"] as const
  },
  
  dashboard: {
    all: () => ["dashboard"] as const,
    telemetry: () => ["dashboard", "telemetry"] as const
  },
  
  projects: {
    all: () => ["projects"] as const,
    list: () => ["projects", "list"] as const,
    detail: (id: string) => ["projects", "detail", id] as const
  },
  
  conversations: {
    all: () => ["conversations"] as const,
    list: () => ["conversations", "list"] as const,
    detail: (id: string) => ["conversations", "detail", id] as const,
    messages: (id: string) => ["conversations", "messages", id] as const
  },
  
  agents: {
    all: () => ["agents"] as const,
    list: () => ["agents", "list"] as const,
    state: (id: string) => ["agents", "state", id] as const
  },
  
  memory: {
    all: () => ["memory"] as const,
    timeline: (sessionId: string, tier?: string) => ["memory", "timeline", sessionId, tier] as const,
    detail: (memoryId: string) => ["memory", "detail", memoryId] as const,
    graph: (userId?: string) => ["memory", "graph", userId] as const,
    embeddings: (sessionId: string) => ["memory", "embeddings", sessionId] as const,
    contextWindow: (sessionId: string) => ["memory", "contextWindow", sessionId] as const,
    analytics: (sessionId: string) => ["memory", "analytics", sessionId] as const,
  },
  
  rag: {
    all: () => ["rag"] as const,
    knowledgeBases: () => ["rag", "kbs"] as const,
    datasets: (kbId?: string | null) => ["rag", "datasets", kbId] as const,
    documents: (datasetId?: string | null) => ["rag", "documents", datasetId] as const,
    chunks: (documentId?: string | null) => ["rag", "chunks", documentId] as const,
    analytics: () => ["rag", "analytics"] as const,
    graph: (kbId: string) => ["rag", "graph", kbId] as const,
    evaluations: () => ["rag", "evaluations"] as const,
  },

  files: {
    all: () => ["files"] as const,
    list: () => ["files", "list"] as const
  },
  
  settings: {
    all: () => ["settings"] as const,
    system: () => ["settings", "system"] as const
  },

  models: {
    all: () => ["models"] as const,
    providers: () => ["models", "providers"] as const,
    registry: () => ["models", "registry"] as const,
    routingPolicies: () => ["models", "routingPolicies"] as const,
    analytics: () => ["models", "analytics"] as const,
  },

  workflows: {
    all: () => ["workflows"] as const,
    list: () => ["workflows", "list"] as const,
    templates: () => ["workflows", "templates"] as const,
    detail: (id: string) => ["workflows", "detail", id] as const,
    analytics: (id: string) => ["workflows", "analytics", id] as const,
  },

  deployments: {
    all: () => ["deployments"] as const,
    environments: () => ["deployments", "environments"] as const,
    targets: () => ["deployments", "targets"] as const,
    health: (env: string) => ["deployments", "health", env] as const,
    secrets: (env: string) => ["deployments", "secrets", env] as const,
    auditLogs: () => ["deployments", "auditLogs"] as const,
  }
} as const
