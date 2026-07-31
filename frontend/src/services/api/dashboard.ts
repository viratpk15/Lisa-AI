import { apiClient } from "./apiClient"
import type { DashboardResponse } from "@/types/api"

/**
 * System Telemetry & Dashboard Service Module
 * Aggregates core system stats, memory allocations, CPU/load parameters, and loaded tools list.
 */

/**
 * Fetches dashboard aggregation statistics from the Jarvis runtime.
 *
 * KNOWN LIMITATION: the backend has no aggregation endpoint that returns
 * combined tools/memory/agents/system stats in one call — `/system/telemetry`
 * (the endpoint this used to call) does not exist anywhere in the backend.
 * The only real, callable status endpoint today is GET /health (see
 * app/FastAPI/routes.py), which returns just `{ status, version }`.
 * This function is wired to that endpoint so callers get a real response
 * instead of a guaranteed 404, but it will NOT populate per-widget stats
 * (tool counts, memory usage, agent counts, etc). Building a true dashboard
 * aggregation requires adding a new backend endpoint — flagged as a
 * follow-up, not something this call can paper over.
 */
export const getDashboardStats = async (): Promise<DashboardResponse> => {
  return apiClient.get<DashboardResponse>("/health")
}
