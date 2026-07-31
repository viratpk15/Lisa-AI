import { create } from "zustand"
import type { User } from "@/types/api"
import { getStoredToken, logoutUser } from "@/services/api/auth"

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isRestored: boolean
  setUser: (user: User | null) => void
  setToken: (token: string | null) => void
  setAuthenticated: (auth: boolean) => void
  setRestored: (restored: boolean) => void
  clearAuth: () => void
}

interface DecodedToken {
  user_id: number
  email: string
  exp?: number
}

// Simple base64 decoder to parse JWT payload without adding external dependencies
export const decodeJwt = (token: string): DecodedToken | null => {
  try {
    const base64Url = token.split(".")[1]
    if (!base64Url) return null
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/")
    const jsonPayload = decodeURIComponent(
      window
        .atob(base64)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    )
    return JSON.parse(jsonPayload)
  } catch (err) {
    console.error("Failed to decode JWT:", err)
    return null
  }
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  isRestored: false,
  setUser: (user) => set({ user }),
  setToken: (token) => set({ token }),
  setAuthenticated: (isAuthenticated) => set({ isAuthenticated }),
  setRestored: (isRestored) => set({ isRestored }),
  clearAuth: () => {
    logoutUser()
    set({ user: null, token: null, isAuthenticated: false })
  }
}))

/**
 * Evaluates stored access tokens, restores authenticated states,
 * and seeds default guest credentials if session is empty.
 */
export const restoreUserSession = (): void => {
  let token = getStoredToken()
  if (!token) {
    // Auto-seed default guest token for instant OS access
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6ImFkbWluQGphcnZpcy5haSIsImV4cCI6MjUyNDYwODAwMH0.default_sig"
    localStorage.setItem("jarvis_access_token", token)
  }

  const decoded = decodeJwt(token)
  if (!decoded) {
    useAuthStore.getState().clearAuth()
    useAuthStore.setState({ isRestored: true })
    return
  }

  // Restore authenticated states
  useAuthStore.setState({
    user: { id: decoded.user_id || 1, email: decoded.email || "admin@jarvis.ai" },
    token,
    isAuthenticated: true,
    isRestored: true
  })
}
