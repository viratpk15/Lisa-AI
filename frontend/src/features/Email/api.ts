// frontend/src/features/Email/api.ts
import { apiClient } from "@/services/api/apiClient"

export interface EmailListItem {
  id: number
  sender: string
  sender_domain: string
  recipients: string
  subject: string
  snippet: string
  received_at: string
  category: string | null
  subcategory: string | null
  priority_score: number | null
  one_line_summary: string | null
  deadline: string | null
  is_verified: boolean
  spf_status: string
  dkim_status: string
  dmarc_status: string
}

export interface EmailActionItems {
  tasks: string[]
  links: string[]
  sender_action_required: boolean
}

export interface EmailAnalysisData {
  category: string | null
  subcategory: string | null
  priority_score: number | null
  summary_text: string | null
  action_items: EmailActionItems | null
  deadline: string | null
  classified_at: string | null
  summarized_at: string | null
  extracted_at: string | null
}

export interface EmailVerificationData {
  is_verified: boolean
  spf_status: string
  dkim_status: string
  dmarc_status: string
  spf_details?: string | null
  dkim_details?: string | null
  dmarc_details?: string | null
}

export interface EmailDetail {
  id: number
  sender: string
  sender_domain: string
  recipients: string
  subject: string
  body_text: string
  body_html: string | null
  snippet: string | null
  received_at: string
  analysis: EmailAnalysisData | null
  verification: EmailVerificationData | null
}

export interface EmailDigestUrgentItem {
  email_id: number
  subject: string
  sender: string
  category: string
  priority_score: number
  one_line_summary: string
  received_at: string
}

export interface EmailDigestActionItem {
  email_id: number
  subject: string
  sender: string
  tasks: string[]
  links: string[]
  sender_action_required: boolean
  deadline: string | null
}

export interface EmailDigestDeadlineItem {
  email_id: number
  subject: string
  sender: string
  deadline: string
  category: string
}

export interface EmailDigest {
  period: "today" | "week"
  generated_at: string
  counts_by_category: Record<string, number>
  top_urgent: EmailDigestUrgentItem[]
  action_items: EmailDigestActionItem[]
  upcoming_deadlines: EmailDigestDeadlineItem[]
  cached: boolean
}

export interface EmailSyncResponse {
  status: string
  synced_count: number
  new_messages: number
  failed_messages: number
  total_messages_scanned: number
  latest_synced_at: string | null
}

export interface EmailListParams {
  category?: string
  priority?: number
  limit?: number
  offset?: number
}

// ---------------------------------------------------------------------------
// API Methods
// ---------------------------------------------------------------------------

export async function syncEmailApi(maxResults = 20, query = ""): Promise<EmailSyncResponse> {
  return apiClient.post<EmailSyncResponse>("/api/v1/email/sync", {
    max_results: maxResults,
    query,
  })
}

export async function fetchEmailListApi(params?: EmailListParams): Promise<{ emails: EmailListItem[]; count: number }> {
  const queryParts: string[] = []
  if (params?.category) queryParts.push(`category=${encodeURIComponent(params.category)}`)
  if (params?.priority !== undefined) queryParts.push(`priority=${params.priority}`)
  if (params?.limit !== undefined) queryParts.push(`limit=${params.limit}`)
  if (params?.offset !== undefined) queryParts.push(`offset=${params.offset}`)

  const qs = queryParts.length > 0 ? `?${queryParts.join("&")}` : ""
  return apiClient.get<{ emails: EmailListItem[]; count: number }>(`/api/v1/email/list${qs}`)
}

export async function fetchEmailDetailApi(emailId: number): Promise<EmailDetail> {
  return apiClient.get<EmailDetail>(`/api/v1/email/${emailId}`)
}

export async function classifyEmailApi(emailId: number): Promise<Record<string, unknown>> {
  return apiClient.post<Record<string, unknown>>(`/api/v1/email/${emailId}/classify`, {})
}

export async function summarizeEmailApi(emailId: number): Promise<Record<string, unknown>> {
  return apiClient.post<Record<string, unknown>>(`/api/v1/email/${emailId}/summarize`, {})
}

export async function extractActionsEmailApi(emailId: number): Promise<Record<string, unknown>> {
  return apiClient.post<Record<string, unknown>>(`/api/v1/email/${emailId}/extract-actions`, {})
}

export async function fetchEmailDigestApi(period: "today" | "week" = "today"): Promise<EmailDigest> {
  return apiClient.get<EmailDigest>(`/api/v1/email/digest?period=${period}`)
}

export interface GoogleAuthStatusResponse {
  connected: boolean
  email_address?: string
  expires_at?: string
  scopes?: string[]
}

export async function fetchGoogleAuthStatusApi(): Promise<GoogleAuthStatusResponse> {
  try {
    return await apiClient.get<GoogleAuthStatusResponse>("/api/v1/auth/google/status")
  } catch {
    return { connected: false }
  }
}

export async function fetchGoogleAuthUrlApi(): Promise<{ url: string; authorization_url?: string }> {
  const res = await apiClient.get<{ url?: string; authorization_url?: string }>("/api/v1/auth/google/url")
  return {
    url: res.url || res.authorization_url || "",
    authorization_url: res.authorization_url || res.url || "",
  }
}

export async function disconnectGoogleAuthApi(): Promise<void> {
  await apiClient.post("/api/v1/auth/google/disconnect")
}
