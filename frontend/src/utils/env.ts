/**
 * Jarvis AIOS environment configurations
 * Resolves env parameters cleanly and validates required variables at startup.
 */

interface EnvConfig {
  apiUrl: string
  timeoutMs: number
  isDev: boolean
  isProd: boolean
}

// Perform strict assertions at runtime to catch invalid config parameters
const validateEnv = (): EnvConfig => {
  const rawApiUrl = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").trim()
  let apiUrl = rawApiUrl.replace("http://localhost:8000", "http://127.0.0.1:8000")
  if (apiUrl.endsWith("/") && apiUrl !== "/") {
    apiUrl = apiUrl.slice(0, -1)
  }
  const timeoutMsStr = import.meta.env.VITE_API_TIMEOUT_MS

  if (!apiUrl) {
    throw new Error(
      "CRITICAL CONFIGURATION ERROR: VITE_API_URL environment variable is undefined. " +
      "Verify that .env file exists and exposes a valid backend api URL."
    );
  }

  if (apiUrl.startsWith("http://") || apiUrl.startsWith("https://")) {
    try {
      new URL(apiUrl)
    } catch {
      throw new Error(
        `CRITICAL CONFIGURATION ERROR: VITE_API_URL "${apiUrl}" is not a valid absolute URL.`
      )
    }
  }

  const timeoutMs = timeoutMsStr ? parseInt(timeoutMsStr, 10) : 10000
  if (isNaN(timeoutMs) || timeoutMs <= 0) {
    throw new Error(
      `CRITICAL CONFIGURATION ERROR: VITE_API_TIMEOUT_MS "${timeoutMsStr}" must be a valid positive integer.`
    )
  }

  return {
    apiUrl,
    timeoutMs,
    isDev: import.meta.env.DEV,
    isProd: import.meta.env.PROD
  }
}

export const env = validateEnv()
export type { EnvConfig }
