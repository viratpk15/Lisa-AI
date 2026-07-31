// frontend/src/features/Deployments/types/deployments.types.ts

export type DeploymentTabType = "dashboard" | "environments" | "releases" | "secrets" | "backups"

export interface DeploymentEnvironment {
  id: number
  env_id: string
  name: string
  tier: "dev" | "staging" | "production"
  is_active: boolean
  created_at: string
}

export interface DeploymentTarget {
  id: number
  env_id: number
  provider_type: "docker" | "k8s" | "railway" | "render" | "vercel" | "fly" | "aws" | "gcp" | "azure" | "self_hosted"
  config: Record<string, any>
  status: string
  created_at: string
}

export interface DeploymentRelease {
  release_id: string
  environment: string
  version_tag: string
  strategy: "blue_green" | "canary" | "direct"
  status: string
  rollout_duration_s: number
  deployed_at: string
}

export interface SecretVaultEntry {
  id: number
  secret_key: string
  masked_value: string
  updated_at: string
}

export interface DatabaseBackup {
  id: number
  snapshot_name: string
  storage_path: string
  size_bytes: number
  created_at: string
}

export interface ContainerProbe {
  name: string
  status: string
  latency_ms: number
}

export interface HealthMetrics {
  environment: string
  status: string
  cpu_percent: number
  memory_mb: number
  containers_running: number
  probes: ContainerProbe[]
}

export interface DeploymentAuditLog {
  id: number
  action: string
  operator_user: string
  details: Record<string, any>
  timestamp: string
}
