import { env } from "@/utils/env"
import { UnauthorizedError, ForbiddenError } from "./errors"

/**
 * Event Types emitted during chat/agent inference runs
 */
export type StreamEventType = 
  | "thinking"     // Initial status frame
  | "token"        // Word tokens emitted from LLM
  | "agent_state"  // Transition of graph nodes
  | "tool_output"  // Log lines from execution agents
  | "error"        // Failure alerts
  | "done"         // Execution completed cleanly

/**
 * Normalized event payload
 */
export interface StreamEvent {
  type: StreamEventType
  data: string
  timestamp: string
}

/**
 * Strategy for connection retry delays
 */
export interface ReconnectPolicy {
  maxRetries: number
  initialDelayMs: number
  maxDelayMs: number
  calculateNextDelay: (retryCount: number) => number
}

/**
 * Handler interface to abort streaming requests safely
 */
export interface CancellationToken {
  isCancelled: boolean
  abort: () => void
}

/**
 * Callback listeners registry for structured stream events
 */
export interface StructuredStreamListeners {
  onThinking?: (status: string) => void
  onToken?: (token: string) => void
  onDone?: (response: string) => void
  onError?: (error: Error) => void
}

/**
 * Legacy listeners interface for backward compatibility
 */
export interface StreamListeners extends StructuredStreamListeners {
  onAgentState?: (nodeName: string) => void
  onToolOutput?: (logLine: string) => void
}

/**
 * Stream chat message tokens via Server-Sent Events (SSE) using fetch & ReadableStream.
 * Parses structured SSE event lines (event: thinking, event: token, event: done, event: error).
 *
 * @param session_id Unique session identifier bound to user token.
 * @param message User prompt text.
 * @param listeners Registry of callbacks for SSE events.
 * @returns CancellationToken handle to abort generation safely.
 */
export const streamChatMessage = (
  session_id: string,
  message: string,
  listeners: StructuredStreamListeners,
  attachment_ids?: string[],
  active_document_id?: string,
  active_filename?: string
): CancellationToken => {
  const controller = new AbortController()
  const token = localStorage.getItem("jarvis_access_token")

  const cancellationToken: CancellationToken = {
    isCancelled: false,
    abort: () => {
      cancellationToken.isCancelled = true
      controller.abort()
    }
  }

  ;(async () => {
    try {
      const response = await fetch(`${env.apiUrl}/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "text/event-stream",
          ...(token ? { "Authorization": `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          session_id,
          message,
          attachment_ids: attachment_ids || [],
          active_document_id: active_document_id || null,
          active_filename: active_filename || null
        }),
        signal: controller.signal
      })

      if (!response.ok) {
        if (response.status === 401) {
          throw new UnauthorizedError("Session authentication expired. Please sign in again.")
        }
        if (response.status === 403) {
          throw new ForbiddenError("Session access denied.")
        }
        const text = await response.text()
        throw new Error(text || `HTTP error ${response.status}`)
      }

      if (!response.body) {
        throw new Error("No response body returned from SSE endpoint.")
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder("utf-8")
      let buffer = ""
      let currentEvent = "token"

      try {
        while (!cancellationToken.isCancelled) {
          const { value, done } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split("\n")
          buffer = lines.pop() || ""

          for (const line of lines) {
            const trimmed = line.trim()
            if (!trimmed) continue

            if (trimmed.startsWith("event:")) {
              currentEvent = trimmed.slice(6).trim()
            } else if (trimmed.startsWith("data:")) {
              const rawData = trimmed.slice(5).trim()
              try {
                const parsed = JSON.parse(rawData)
                const eventType = currentEvent || parsed.type || "token"

                if (eventType === "thinking") {
                  listeners.onThinking?.(parsed.status || "Thinking...")
                } else if (eventType === "token") {
                  const tokenStr = parsed.token !== undefined ? parsed.token : (parsed.data || "")
                  listeners.onToken?.(tokenStr)
                } else if (eventType === "done") {
                  const fullResp = parsed.response !== undefined ? parsed.response : (parsed.data || "")
                  listeners.onDone?.(fullResp)
                } else if (eventType === "error") {
                  const errStr = parsed.error !== undefined ? parsed.error : (parsed.data || "Stream error")
                  listeners.onError?.(new Error(errStr))
                }
              } catch {
                if (currentEvent === "token") {
                  listeners.onToken?.(rawData)
                }
              }
            }
          }
        }
      } finally {
        reader.releaseLock()
      }
    } catch (err: unknown) {
      if (err instanceof DOMException && err.name === "AbortError") {
        // Stream cancelled cleanly by user
        return
      }
      const errorObj = err instanceof Error ? err : new Error(String(err))
      listeners.onError?.(errorObj)
    }
  })()

  return cancellationToken
}

