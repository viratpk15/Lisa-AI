/**
 * Lisa AIOS — Jobs & Internship Finder API Client
 * Aligned to real backend FastAPI route signatures.
 *
 * Route prefix: /api/v1/jobs (mounted in main.py)
 * All endpoints require Bearer token authentication.
 */

import { apiClient } from "@/services/api/apiClient"
import type {
  CandidateProfile,
  JobSearchFilters,
  JobSearchWithMatchesResponse,
  JobOpportunity,
  SkillGapAnalysis,
  ResumeJobAnalysisRequest,
  ResumeJobAnalysisResponse,
  ApplicationTrackItem,
  UpdateApplicationStatusRequest,
  ApplicationStatusEnum,
} from "./types"

const BASE = "/api/v1/jobs"

// ── Profile ────────────────────────────────────────────────────────────────

/**
 * Upload resume file (PDF, DOCX, TXT) → backend parses → returns raw CandidateProfile.
 * is_confirmed_by_user will be false — user must review before saving.
 */
export async function extractResumeApi(file: File): Promise<CandidateProfile> {
  const formData = new FormData()
  formData.append("file", file)
  return apiClient.post<CandidateProfile>(`${BASE}/profile/extract-resume`, formData, {
    timeoutMs: 60000,
  })
}

/**
 * GET current authenticated user's saved CandidateProfile.
 * Returns an empty initialized profile when none exists.
 */
export async function getCandidateProfileApi(): Promise<CandidateProfile> {
  return apiClient.get<CandidateProfile>(`${BASE}/profile`)
}

/**
 * POST/save candidate profile for authenticated user.
 * Backend normalizes all skills before persisting.
 */
export async function saveCandidateProfileApi(profile: CandidateProfile): Promise<CandidateProfile> {
  return apiClient.post<CandidateProfile>(`${BASE}/profile`, profile)
}

// ── Job Search ─────────────────────────────────────────────────────────────

/**
 * POST search live job providers (RemoteOK + Arbeitnow + optional Adzuna).
 * Returns JobSearchWithMatchesResponse: { search_response, matches }
 * Zero fabrication: empty results returned honestly if providers are down.
 */
export async function searchJobsApi(
  filters: JobSearchFilters
): Promise<JobSearchWithMatchesResponse> {
  return apiClient.post<JobSearchWithMatchesResponse>(`${BASE}/search`, filters, {
    timeoutMs: 30000,
  })
}

/**
 * GET a single job opportunity by its provider-prefixed ID.
 * Only available for jobs returned in a prior search (in-memory cache).
 */
export async function getJobDetailsApi(jobId: string): Promise<JobOpportunity> {
  return apiClient.get<JobOpportunity>(`${BASE}/${jobId}`)
}

// ── Skill Analysis ─────────────────────────────────────────────────────────

/**
 * GET skill gap analysis: compares saved profile skills vs. job requirements.
 * Returns matched, missing required, missing preferred, projects, preparation roadmap.
 */
export async function analyzeSkillGapApi(jobId: string): Promise<SkillGapAnalysis> {
  return apiClient.get<SkillGapAnalysis>(`${BASE}/${jobId}/skill-gap`)
}

/**
 * POST deep resume-to-job analysis using LLM evaluation.
 * Optionally accepts custom resume text (overrides saved profile).
 */
export async function analyzeResumeJobApi(
  req: ResumeJobAnalysisRequest
): Promise<ResumeJobAnalysisResponse> {
  return apiClient.post<ResumeJobAnalysisResponse>(`${BASE}/analyze-resume-job`, req, {
    timeoutMs: 60000,
  })
}

// ── Application Tracker ────────────────────────────────────────────────────

/**
 * GET all tracked job applications for the current user.
 */
export async function listTrackedJobsApi(): Promise<ApplicationTrackItem[]> {
  return apiClient.get<ApplicationTrackItem[]>(`${BASE}/applications/all`)
}

/**
 * POST track a new job. Requires the job to be in the provider's in-memory cache.
 */
export async function trackJobApi(
  jobId: string,
  status: ApplicationStatusEnum = "saved"
): Promise<ApplicationTrackItem> {
  return apiClient.post<ApplicationTrackItem>(`${BASE}/applications`, {
    job_id: jobId,
    status,
  })
}

/**
 * PATCH update a tracked application status or notes.
 */
export async function updateApplicationStatusApi(
  jobId: string,
  req: UpdateApplicationStatusRequest
): Promise<ApplicationTrackItem> {
  return apiClient.patch<ApplicationTrackItem>(
    `${BASE}/applications/${jobId}/status`,
    req
  )
}

/**
 * DELETE a tracked application.
 */
export async function deleteTrackedJobApi(jobId: string): Promise<{ deleted: boolean }> {
  return apiClient.del<{ deleted: boolean }>(`${BASE}/applications/${jobId}`)
}
