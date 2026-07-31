import { env } from "@/utils/env"
import {
  APIError,
  ValidationError,
  UnauthorizedError,
  ForbiddenError,
  NotFoundError,
  ServerError,
  NetworkError,
  UnknownError
} from "./errors"
import type { APIErrorResponse } from "@/types/api"

interface RequestOptions extends RequestInit {
  timeoutMs?: number
  skipAuth?: boolean
}

/**
 * Main API Client wrapper using the native Fetch API.
 * Configured with timeouts, validation guards, and JWT headers.
 */
class APIClient {
  private getHeaders(skipAuth = false): HeadersInit {
    const headers: Record<string, string> = {
      "Accept": "application/json"
    }

    if (!skipAuth) {
      const token = localStorage.getItem("jarvis_access_token")
      if (token) {
        headers["Authorization"] = `Bearer ${token}`
      }
    }

    return headers
  }

  /**
   * Evaluates HTTP status parameters and parses error structures
   */
  private async handleError(response: Response): Promise<never> {
    const status = response.status
    let apiError: APIErrorResponse | null = null

    try {
      const text = await response.text()
      if (text) {
        apiError = JSON.parse(text)
      }
    } catch {
      // Swallowed: response wasn't JSON
    }

    const message = apiError?.error?.message || response.statusText
    const details = apiError?.error?.details

    switch (status) {
      case 401:
        throw new UnauthorizedError(message)
      case 403:
        throw new ForbiddenError(message)
      case 404:
        throw new NotFoundError(message)
      case 422:
        throw new ValidationError(message, details)
      case 429:
        throw new APIError(429, "rate_limited", message || "Too many requests. Please slow down.", undefined, true)
      default:
        if (status >= 500) {
          throw new ServerError(message)
        }
        throw new UnknownError(message)
    }
  }

  /**
   * Core request dispatcher mapping timeout loops
   */
  async request<T>(path: string, options: RequestOptions = {}): Promise<T> {
    const { timeoutMs = env.timeoutMs, skipAuth = false, ...fetchOptions } = options
    const url = `${env.apiUrl}${path}`

    // Setup network timeout controller
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs)

    if (fetchOptions.signal) {
      if (fetchOptions.signal.aborted) {
        controller.abort()
      } else {
        fetchOptions.signal.addEventListener("abort", () => controller.abort())
      }
    }

    // Assemble headers
    const headers = new Headers(this.getHeaders(skipAuth))
    if (fetchOptions.headers) {
      new Headers(fetchOptions.headers).forEach((value, key) => {
        headers.set(key, value)
      })
    }

    try {
      const response = await fetch(url, {
        ...fetchOptions,
        headers,
        signal: controller.signal
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        return await this.handleError(response)
      }

      // Check for empty body responses (e.g. HTTP 204)
      if (response.status === 204) {
        return {} as T
      }

      const contentType = response.headers.get("content-type")
      if (contentType && contentType.includes("application/json")) {
        return await response.json()
      }

      return (await response.text()) as unknown as T
    } catch (error: unknown) {
      clearTimeout(timeoutId)

      if (error instanceof DOMException && error.name === "AbortError") {
        throw new APIError(408, "timeout", "Request timed out on client boundary.", undefined, true)
      }

      if (error instanceof TypeError) {
        // Typically indicates DNS failure, host unreachable or CORS blocking
        throw new NetworkError("Connection refused by Jarvis server.")
      }

      if (error instanceof APIError) {
        throw error
      }

      throw new UnknownError(error instanceof Error ? error.message : undefined)
    }
  }

  // Request Helpers
  async get<T>(path: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(path, { ...options, method: "GET" })
  }

  async post<T>(path: string, body?: unknown, options?: RequestOptions): Promise<T> {
    const isFormData = body instanceof FormData
    const headers: Record<string, string> = {}
    if (!isFormData) {
      headers["Content-Type"] = "application/json"
    }

    return this.request<T>(path, {
      ...options,
      method: "POST",
      headers,
      body: isFormData ? body : JSON.stringify(body)
    })
  }

  async put<T>(path: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>(path, {
      ...options,
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    })
  }

  async patch<T>(path: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>(path, {
      ...options,
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    })
  }

  async del<T>(path: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(path, { ...options, method: "DELETE" })
  }

  /**
   * Foundation for Multipart uploads supporting progress monitoring hooks.
   */
  async upload<T>(
    path: string,
    file: File,
    fieldName = "file",
    additionalFields?: Record<string, string>,
    options?: RequestOptions
  ): Promise<T> {
    const formData = new FormData()
    formData.append(fieldName, file)
    
    if (additionalFields) {
      Object.entries(additionalFields).forEach(([key, value]) => {
        formData.append(key, value)
      })
    }

    return this.post<T>(path, formData, options)
  }
}

export const apiClient = new APIClient()
export type { RequestOptions }
