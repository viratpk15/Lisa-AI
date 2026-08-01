import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "react-router"
import { loginUser, registerUser } from "@/services/api/auth"
import { useAuthStore, decodeJwt } from "@/services/store/authStore"
import { resetUnauthorizedGuard } from "@/services/api/apiClient"
import { queryKeys } from "./queryKeys"
import { normalizeError } from "@/services/api/errors"

/**
 * Authentication Queries & Mutations Module
 * Coordinates network auth requests with the centralized Zustand state store.
 */

/**
 * Login mutation handling JWT cache storage and token decoding.
 * After a successful login the user is redirected to either the originally
 * requested protected route (redirectTo) or /dashboard as default.
 */
export const useLoginMutation = () => {
  const setUser = useAuthStore((state) => state.setUser)
  const setToken = useAuthStore((state) => state.setToken)
  const setAuthenticated = useAuthStore((state) => state.setAuthenticated)
  const redirectTo = useAuthStore((state) => state.redirectTo)
  const setRedirectTo = useAuthStore((state) => state.setRedirectTo)
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: async ({ email, password }: { email: string; password: string }) => {
      return loginUser(email, password)
    },
    onSuccess: (data) => {
      const decoded = decodeJwt(data.access_token)
      if (decoded) {
        setUser({ id: decoded.user_id, email: decoded.email })
        setToken(data.access_token)
        setAuthenticated(true)
        // Reset query caches upon successful authentication
        queryClient.clear()
        // Reset 401 guard so the new session's requests are not blocked
        resetUnauthorizedGuard()
        // Navigate to originally intended destination or default dashboard
        const destination = redirectTo || "/dashboard"
        setRedirectTo(null)
        navigate(destination, { replace: true })
      }
    },
    onError: (error) => {
      // Return normalized error objects to the UI boundaries
      throw normalizeError(error)
    }
  })
}

/**
 * Registration mutation to create new credentials.
 */
export const useRegisterMutation = () => {
  return useMutation({
    mutationKey: queryKeys.auth.all(),
    mutationFn: async ({ email, password }: { email: string; password: string }) => {
      return registerUser(email, password)
    },
    onError: (error) => {
      throw normalizeError(error)
    }
  })
}

