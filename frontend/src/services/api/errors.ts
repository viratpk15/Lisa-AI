
/**
 * Interface representing a normalized system-wide API error.
 * Every request failure maps to this canonical error structure.
 */
export interface NormalizedError {
  status: number
  code: string
  message: string
  details?: Record<string, string | string[]>
  retryable: boolean
  timestamp: string
}

/**
 * Base custom error class for networking exceptions
 */
export class APIError extends Error implements NormalizedError {
  status: number
  code: string
  details?: Record<string, string | string[]>
  retryable: boolean
  timestamp: string

  constructor(
    status: number,
    code: string,
    message: string,
    details?: Record<string, string | string[]>,
    retryable = false
  ) {
    super(message)
    this.name = "APIError"
    this.status = status
    this.code = code
    this.details = details
    this.retryable = retryable
    this.timestamp = new Date().toISOString()

    // Restores prototype chain in compilation outputs
    Object.setPrototypeOf(this, new.target.prototype)
  }

  /**
   * Serializes the error object to a plain javascript dictionary
   */
  toNormalized(): NormalizedError {
    return {
      status: this.status,
      code: this.code,
      message: this.message,
      details: this.details,
      retryable: this.retryable,
      timestamp: this.timestamp
    }
  }
}

/**
 * HTTP 422: Input validation constraints failures
 */
export class ValidationError extends APIError {
  constructor(message: string, details?: Record<string, string | string[]>) {
    super(422, "validation_error", message, details, false)
    this.name = "ValidationError"
  }
}

/**
 * HTTP 401: Unauthorized access token failures
 */
export class UnauthorizedError extends APIError {
  constructor(message = "Session unauthorized. Access token is missing or expired.") {
    super(401, "unauthorized", message, undefined, false)
    this.name = "UnauthorizedError"
  }
}

/**
 * HTTP 403: Forbidden access, e.g. ownership breaches
 */
export class ForbiddenError extends APIError {
  constructor(message = "Access forbidden to requested resource.") {
    super(403, "forbidden", message, undefined, false)
    this.name = "ForbiddenError"
  }
}

/**
 * HTTP 404: Resource target missing
 */
export class NotFoundError extends APIError {
  constructor(message = "Target resource could not be found.") {
    super(404, "not_found", message, undefined, false)
    this.name = "NotFoundError"
  }
}

/**
 * Request Timeout exceptions
 */
export class TimeoutError extends APIError {
  constructor(message = "Network request timed out. Please try again.") {
    super(408, "timeout", message, undefined, true)
    this.name = "TimeoutError"
  }
}

/**
 * HTTP 5xx: Backend system crash exceptions
 */
export class ServerError extends APIError {
  constructor(message = "Internal Server Error occurred inside Jarvis kernel.") {
    super(500, "internal_server_error", message, undefined, true)
    this.name = "ServerError"
  }
}

/**
 * CORS/DNS or offline status connectivity failures
 */
export class NetworkError extends APIError {
  constructor(message = "Network disconnected. Please check internet connections.") {
    super(0, "network_disconnected", message, undefined, true)
    this.name = "NetworkError"
  }
}

/**
 * Fallback generic exceptions
 */
export class UnknownError extends APIError {
  constructor(message = "An unknown communications exception occurred.") {
    super(500, "unknown_error", message, undefined, false)
    this.name = "UnknownError"
  }
}

/**
 * Normalizes any caught Javascript error into a clean APIError representation
 */
export const normalizeError = (error: unknown): APIError => {
  if (error instanceof APIError) {
    return error
  }

  if (error instanceof Error) {
    // Check if network timeout exception
    if (error.name === "AbortError") {
      return new TimeoutError()
    }
    return new UnknownError(error.message)
  }

  return new UnknownError()
}
