import { apiClient } from "./apiClient"
import type { HealthResponse } from "@/types/api"

/**
 * Health Check Service Module
 * Querying status indicators and kernel build versions.
 */

/**
 * Invokes the backend health endpoint.
 * Binds to GET /health.
 * 
 * @returns Status string and version ID.
 */
export const checkHealth = async (): Promise<HealthResponse> => {
  return apiClient.get<HealthResponse>("/health", { skipAuth: true })
}
