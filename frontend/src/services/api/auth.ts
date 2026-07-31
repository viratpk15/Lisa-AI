import { apiClient } from "./apiClient"
import type { AuthResponse, User } from "@/types/api"

/**
 * Authentication Service Module
 * Handles login authentication, registration workflows, and JWT local caching.
 */

const TOKEN_KEY = "jarvis_access_token"

/**
 * Register a new user account with credentials.
 * 
 * @param email Validated email address.
 * @param password Password matching security requirements.
 * @returns Standard user profile response object.
 */
export const registerUser = async (email: string, password: string): Promise<User> => {
  return apiClient.post<User>("/auth/register", { email, password }, { skipAuth: true })
}

/**
 * Authenticate credentials and return signed access token payload.
 * Stores token inside LocalStorage upon success.
 * 
 * @param email Validated email address.
 * @param password Plain-text password.
 * @returns JWT access token container.
 */
export const loginUser = async (email: string, password: string): Promise<AuthResponse> => {
  const result = await apiClient.post<AuthResponse>("/auth/login", { email, password }, { skipAuth: true })
  if (result.access_token) {
    localStorage.setItem(TOKEN_KEY, result.access_token)
  }
  return result
}

/**
 * Clears JWT session token caches, logging the user out immediately.
 */
export const logoutUser = (): void => {
  localStorage.removeItem(TOKEN_KEY)
}

/**
 * Evaluates whether an active access token is present in browser storage.
 * 
 * @returns Boolean flag.
 */
export const isAuthenticated = (): boolean => {
  return !!localStorage.getItem(TOKEN_KEY)
}

/**
 * Retrieves the stored JWT token.
 * 
 * @returns Token string or null.
 */
export const getStoredToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEY)
}
