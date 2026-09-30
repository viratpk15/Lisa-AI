/**
 * Lisa AIOS — Jobs & Internship Finder React Query Hooks
 * Aligned to real backend API shapes.
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import {
  extractResumeApi,
  getCandidateProfileApi,
  saveCandidateProfileApi,
  searchJobsApi,
  getJobDetailsApi,
  analyzeSkillGapApi,
  analyzeResumeJobApi,
  listTrackedJobsApi,
  trackJobApi,
  updateApplicationStatusApi,
  deleteTrackedJobApi,
} from "./api"
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

export const jobsQueryKeys = {
  all: () => ["jobs"] as const,
  profile: () => [...jobsQueryKeys.all(), "profile"] as const,
  job: (id: string) => [...jobsQueryKeys.all(), "job", id] as const,
  tracked: () => [...jobsQueryKeys.all(), "tracked"] as const,
}

// ── Profile ────────────────────────────────────────────────────────────────

export function useCandidateProfileQuery() {
  return useQuery<CandidateProfile>({
    queryKey: jobsQueryKeys.profile(),
    queryFn: getCandidateProfileApi,
    staleTime: 5 * 60_000,
  })
}

export function useSaveCandidateProfileMutation() {
  const queryClient = useQueryClient()
  return useMutation<CandidateProfile, Error, CandidateProfile>({
    mutationFn: saveCandidateProfileApi,
    onSuccess: (data) => {
      queryClient.setQueryData(jobsQueryKeys.profile(), data)
    },
  })
}

/**
 * Resume extraction mutation (Method B — file upload).
 * Returns a CandidateProfile with is_confirmed_by_user = false.
 * The user MUST review and explicitly save the result.
 */
export function useExtractResumeMutation() {
  return useMutation<CandidateProfile, Error, File>({
    mutationFn: extractResumeApi,
  })
}

// ── Job Search ─────────────────────────────────────────────────────────────

export function useJobSearchMutation() {
  return useMutation<JobSearchWithMatchesResponse, Error, JobSearchFilters>({
    mutationFn: searchJobsApi,
  })
}

export function useJobDetailsQuery(jobId: string | null) {
  return useQuery<JobOpportunity>({
    queryKey: jobsQueryKeys.job(jobId ?? ""),
    queryFn: () => getJobDetailsApi(jobId!),
    enabled: Boolean(jobId),
  })
}

// ── Skill Analysis ─────────────────────────────────────────────────────────

export function useSkillGapMutation() {
  return useMutation<SkillGapAnalysis, Error, string>({
    mutationFn: analyzeSkillGapApi,
  })
}

export function useDeepAnalysisMutation() {
  return useMutation<ResumeJobAnalysisResponse, Error, ResumeJobAnalysisRequest>({
    mutationFn: analyzeResumeJobApi,
  })
}

// ── Application Tracker ────────────────────────────────────────────────────

export function useTrackedApplicationsQuery() {
  return useQuery<ApplicationTrackItem[]>({
    queryKey: jobsQueryKeys.tracked(),
    queryFn: listTrackedJobsApi,
    staleTime: 30_000,
  })
}

export function useTrackJobMutation() {
  const queryClient = useQueryClient()
  return useMutation<
    ApplicationTrackItem,
    Error,
    { jobId: string; status?: ApplicationStatusEnum }
  >({
    mutationFn: ({ jobId, status }) => trackJobApi(jobId, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: jobsQueryKeys.tracked() })
    },
  })
}

export function useUpdateApplicationStatusMutation() {
  const queryClient = useQueryClient()
  return useMutation<
    ApplicationTrackItem,
    Error,
    { jobId: string; req: UpdateApplicationStatusRequest }
  >({
    mutationFn: ({ jobId, req }) => updateApplicationStatusApi(jobId, req),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: jobsQueryKeys.tracked() })
    },
  })
}

export function useDeleteTrackedJobMutation() {
  const queryClient = useQueryClient()
  return useMutation<{ deleted: boolean }, Error, string>({
    mutationFn: deleteTrackedJobApi,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: jobsQueryKeys.tracked() })
    },
  })
}
