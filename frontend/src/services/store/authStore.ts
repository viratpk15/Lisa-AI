import { create } from "zustand"
import type { User } from "@/types/api"
import { getStoredToken, logoutUser } from "@/services/api/auth"

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isRestored: boolean
  /**
   * Stores the protected route the user attempted to access before being
   * redirected to /auth. After a successful login the app navigates here
   * instead of always landing on /dashboard.
   */
  redirectTo: string | null
  setUser: (user: User | null) => void
  setToken: (token: string | null) => void
  setAuthenticated: (auth: boolean) => void
  setRestored: (restored: boolean) => void
  setRedirectTo: (path: string | null) => void
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
  redirectTo: null,
  setUser: (user) => set({ user }),
  setToken: (token) => set({ token }),
  setAuthenticated: (isAuthenticated) => set({ isAuthenticated }),
  setRestored: (isRestored) => set({ isRestored }),
  setRedirectTo: (redirectTo) => set({ redirectTo }),
  clearAuth: () => {
    logoutUser()
    set({ user: null, token: null, isAuthenticated: false, isRestored: true })
  }
}))

/**
 * Returns true if the token appears to be a real cryptographic JWT.
 * Rejects any token whose signature segment is too short (< 20 chars) or
 * matches known fake/placeholder patterns injected by old development builds.
 */
const _isRealJwt = (token: string): boolean => {
  const parts = token.split(".")
  if (parts.length !== 3) return false
  const sig = parts[2]
  // Real HS256 signatures are base64url-encoded 32 bytes → 43 chars
  // Placeholder signatures like 'default_sig' are obviously too short
  if (sig.length < 20) return false
  // Explicitly reject the known legacy fake token signature
  if (sig === "default_sig") return false
  return true
}

/**
 * Restores authenticated session from a previously stored JWT on application
 * boot. If no valid token is found the store is marked as restored but
 * unauthenticated so the router guard redirects to /auth immediately.
 *
 * NOTE: Never auto-seeds a guest token. Unauthenticated visitors must log in.
 */
export const restoreUserSession = (): void => {
  const token = getStoredToken()

  if (!token) {
    // No stored token — mark as restored but unauthenticated
    useAuthStore.setState({ isRestored: true, isAuthenticated: false })
    return
  }

  // Guard: reject fake/placeholder tokens left over from development builds
  if (!_isRealJwt(token)) {
    console.warn("[AUTH] Detected non-cryptographic token in storage — clearing.")
    useAuthStore.getState().clearAuth()
    return
  }

  const decoded = decodeJwt(token)
  if (!decoded) {
    // Token present but malformed — clear it and mark unauthenticated
    useAuthStore.getState().clearAuth()
    return
  }

  // Valid token — check expiry
  if (decoded.exp && decoded.exp * 1000 < Date.now()) {
    // Token has expired — clear it and mark unauthenticated
    useAuthStore.getState().clearAuth()
    return
  }

  // Restore authenticated state
  useAuthStore.setState({
    user: { id: decoded.user_id || 1, email: decoded.email || "" },
    token,
    isAuthenticated: true,
    isRestored: true
  })
}
