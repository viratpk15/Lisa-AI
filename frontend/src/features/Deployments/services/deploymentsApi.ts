// frontend/src/features/Deployments/services/deploymentsApi.ts

import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/services/api/apiClient"
import { queryKeys } from "@/services/queries/queryKeys"
import type {
  DeploymentEnvironment,
  DeploymentTarget,
  DeploymentRelease,
  SecretVaultEntry,
  DatabaseBackup,
  HealthMetrics,
  DeploymentAuditLog,
} from "../types/deployments.types"

export async function fetchEnvironmentsApi(): Promise<DeploymentEnvironment[]> {
  return apiClient.get<DeploymentEnvironment[]>("/api/v1/deployments/environments")
}

export async function fetchTargetsApi(): Promise<DeploymentTarget[]> {
  return apiClient.get<DeploymentTarget[]>("/api/v1/deployments/targets")
}

export async function fetchHealthMetricsApi(envId: string): Promise<HealthMetrics> {
  return apiClient.get<HealthMetrics>(`/api/v1/deployments/${envId}/health`)
}

export async function fetchSecretsApi(envId: string = "prod"): Promise<SecretVaultEntry[]> {
  return apiClient.get<SecretVaultEntry[]>(`/api/v1/deployments/secrets?env_id=${envId}`)
}

export async function fetchAuditLogsApi(): Promise<DeploymentAuditLog[]> {
  return apiClient.get<DeploymentAuditLog[]>("/api/v1/deployments/audit-logs")
}

export async function triggerRolloutApi(payload: {
  env_id: string
  version_tag: string
  strategy: string
}): Promise<DeploymentRelease> {
  return apiClient.post<DeploymentRelease>("/api/v1/deployments/rollout", payload)
}

export async function triggerRollbackApi(payload: {
  env_id: string
  target_release_id?: string
}): Promise<{ status: string; restored_release_id: string; message: string }> {
  return apiClient.post<{ status: string; restored_release_id: string; message: string }>(
    "/api/v1/deployments/rollback",
    payload
  )
}

export async function saveSecretApi(payload: {
  env_id: string
  secret_key: string
  raw_value: string
}): Promise<SecretVaultEntry> {
  return apiClient.post<SecretVaultEntry>("/api/v1/deployments/secrets", payload)
}

export async function createBackupApi(envId: string = "prod"): Promise<DatabaseBackup> {
  return apiClient.post<DatabaseBackup>(`/api/v1/deployments/backups?env_id=${envId}`, {})
}

export async function restoreBackupApi(snapshotName: string): Promise<{ status: string; message: string }> {
  return apiClient.post<{ status: string; message: string }>("/api/v1/deployments/backups/restore", {
    snapshot_name: snapshotName,
  })
}

// React Query Hooks
export function useEnvironmentsQuery() {
  return useQuery({
    queryKey: queryKeys.deployments.environments(),
    queryFn: fetchEnvironmentsApi,
  })
}

export function useTargetsQuery() {
  return useQuery({
    queryKey: queryKeys.deployments.targets(),
    queryFn: fetchTargetsApi,
  })
}

export function useDeploymentHealthQuery(envId: string) {
  return useQuery({
    queryKey: queryKeys.deployments.health(envId),
    queryFn: () => fetchHealthMetricsApi(envId),
    enabled: Boolean(envId),
    refetchInterval: 5000,
  })
}

export function useSecretsQuery(envId: string) {
  return useQuery({
    queryKey: queryKeys.deployments.secrets(envId),
    queryFn: () => fetchSecretsApi(envId),
    enabled: Boolean(envId),
  })
}

export function useAuditLogsQuery() {
  return useQuery({
    queryKey: queryKeys.deployments.auditLogs(),
    queryFn: fetchAuditLogsApi,
  })
}
