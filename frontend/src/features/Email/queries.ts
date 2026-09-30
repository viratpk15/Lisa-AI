// frontend/src/features/Email/queries.ts
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import {
  classifyEmailApi,
  extractActionsEmailApi,
  fetchEmailDetailApi,
  fetchEmailDigestApi,
  fetchEmailListApi,
  summarizeEmailApi,
  syncEmailApi,
  fetchGoogleAuthStatusApi,
  disconnectGoogleAuthApi,
  type GoogleAuthStatusResponse,
  type EmailDetail,
  type EmailDigest,
  type EmailListItem,
  type EmailListParams,
  type EmailSyncResponse,
} from "./api"

export const emailQueryKeys = {
  all: () => ["email"] as const,
  lists: () => [...emailQueryKeys.all(), "list"] as const,
  list: (params?: EmailListParams) => [...emailQueryKeys.lists(), params] as const,
  details: () => [...emailQueryKeys.all(), "detail"] as const,
  detail: (id: number) => [...emailQueryKeys.details(), id] as const,
  digests: () => [...emailQueryKeys.all(), "digest"] as const,
  digest: (period: "today" | "week") => [...emailQueryKeys.digests(), period] as const,
}

// ---------------------------------------------------------------------------
// Query Hooks
// ---------------------------------------------------------------------------

export function useEmailList(params?: EmailListParams) {
  return useQuery<{ emails: EmailListItem[]; count: number }>({
    queryKey: emailQueryKeys.list(params),
    queryFn: () => fetchEmailListApi(params),
    staleTime: 30_000,
  })
}

export function useEmailDetail(emailId: number | null) {
  return useQuery<EmailDetail>({
    queryKey: emailQueryKeys.detail(emailId ?? 0),
    queryFn: () => fetchEmailDetailApi(emailId!),
    enabled: Boolean(emailId && emailId > 0),
    staleTime: 30_000,
  })
}

export function useEmailDigest(period: "today" | "week" = "today") {
  return useQuery<EmailDigest>({
    queryKey: emailQueryKeys.digest(period),
    queryFn: () => fetchEmailDigestApi(period),
    staleTime: 60_000,
  })
}

// ---------------------------------------------------------------------------
// Mutation Hooks
// ---------------------------------------------------------------------------

export interface EmailSyncVariables {
  maxResults?: number
  query?: string
}

export function useSyncEmail() {
  const queryClient = useQueryClient()
  return useMutation<EmailSyncResponse, Error, EmailSyncVariables | void>({
    mutationFn: (variables) => {
      if (variables) {
        return syncEmailApi(variables.maxResults, variables.query)
      }
      return syncEmailApi()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: emailQueryKeys.all() })
    },
  })
}

export function useClassifyEmail() {
  const queryClient = useQueryClient()
  return useMutation<Record<string, unknown>, Error, number>({
    mutationFn: (emailId: number) => classifyEmailApi(emailId),
    onSuccess: (_data, emailId) => {
      queryClient.invalidateQueries({ queryKey: emailQueryKeys.detail(emailId) })
      queryClient.invalidateQueries({ queryKey: emailQueryKeys.lists() })
      queryClient.invalidateQueries({ queryKey: emailQueryKeys.digests() })
    },
  })
}

export function useSummarizeEmail() {
  const queryClient = useQueryClient()
  return useMutation<Record<string, unknown>, Error, number>({
    mutationFn: (emailId: number) => summarizeEmailApi(emailId),
    onSuccess: (_data, emailId) => {
      queryClient.invalidateQueries({ queryKey: emailQueryKeys.detail(emailId) })
      queryClient.invalidateQueries({ queryKey: emailQueryKeys.lists() })
      queryClient.invalidateQueries({ queryKey: emailQueryKeys.digests() })
    },
  })
}

export function useExtractActionsEmail() {
  const queryClient = useQueryClient()
  return useMutation<Record<string, unknown>, Error, number>({
    mutationFn: (emailId: number) => extractActionsEmailApi(emailId),
    onSuccess: (_data, emailId) => {
      queryClient.invalidateQueries({ queryKey: emailQueryKeys.detail(emailId) })
      queryClient.invalidateQueries({ queryKey: emailQueryKeys.lists() })
      queryClient.invalidateQueries({ queryKey: emailQueryKeys.digests() })
    },
  })
}

export function useGoogleAuthStatus() {
  return useQuery<GoogleAuthStatusResponse>({
    queryKey: ["auth", "google", "status"],
    queryFn: fetchGoogleAuthStatusApi,
    staleTime: 5_000,
    refetchOnMount: "always",
  })
}

export function useDisconnectGoogleAuth() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: disconnectGoogleAuthApi,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["auth", "google", "status"] })
      queryClient.invalidateQueries({ queryKey: emailQueryKeys.all() })
    },
  })
}
