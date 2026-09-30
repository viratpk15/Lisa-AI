/**
 * Lisa AIOS — Jobs & Internship Finder Domain Types
 * Aligned exactly with backend Pydantic schemas.
 */

// ── Candidate Profile ─────────────────────────────────────────────────────

export interface EducationItem {
  college: string
  degree: string
  branch?: string | null
  graduation_year?: number | null
  cgpa?: number | null
  current_semester?: string | null
}

export interface ProjectItem {
  title: string
  description: string
  tech_stack: string[]
  github_url?: string | null
  live_url?: string | null
}

export interface ExperienceItem {
  company: string
  role: string
  duration?: string | null
  description?: string | null
  is_internship: boolean
  skills_used: string[]
}

export interface SkillCategory {
  programming_languages: string[]
  ai_ml_skills: string[]
  frameworks: string[]
  databases: string[]
  cloud_devops: string[]
  tools: string[]
}

export interface CandidateProfile {
  name: string
  email?: string | null
  phone?: string | null
  education: EducationItem[]
  skills: SkillCategory
  all_normalized_skills: string[]
  projects: ProjectItem[]
  experiences: ExperienceItem[]
  certifications: string[]
  achievements: string[]
  // Preferences
  preferred_roles: string[]
  preferred_locations: string[]
  remote_preference: string
  expected_salary_or_stipend?: string | null
  availability?: string | null
  experience_level: string
  // Metadata
  raw_resume_text?: string | null
  extracted_from_resume: boolean
  is_confirmed_by_user: boolean
}

// ── Job Opportunity ────────────────────────────────────────────────────────

export interface JobOpportunity {
  id: string
  title: string
  company: string
  location: string
  is_remote: boolean
  remote_type: string
  employment_type: string
  experience_level: string
  salary_or_stipend?: string | null  // null when provider did not supply
  salary_currency?: string | null
  salary_min?: number | null
  salary_max?: number | null
  posted_date?: string | null
  deadline?: string | null
  description: string
  required_skills: string[]
  preferred_skills: string[]
  apply_url: string
  source_provider: string
  company_logo?: string | null
}

// ── Search ────────────────────────────────────────────────────────────────

export interface JobSearchFilters {
  role?: string
  location?: string
  is_remote?: boolean
  employment_type?: string
  experience_level?: string
  skills?: string[]
  company?: string
  sort_by?: "relevance" | "newest" | "salary"
  limit?: number
}

export interface JobSearchResponse {
  query: string
  total_results: number
  jobs: JobOpportunity[]
  provider_used: string
  has_live_results: boolean
  status_message?: string | null
  disclaimer: string
}

// ── Skill Matching ────────────────────────────────────────────────────────

export interface SkillMatchResult {
  job_id: string
  matched_required_skills: string[]
  missing_required_skills: string[]
  matched_preferred_skills: string[]
  missing_preferred_skills: string[]
  match_score: number          // documented: 60% skill + 20% exp + 20% location
  match_reasons: string[]
  potential_gaps: string[]
  score_breakdown: {
    skill_overlap_pts: number
    skill_overlap_max: number
    experience_match_pts: number
    experience_match_max: number
    location_match_pts: number
    location_match_max: number
    algorithm: string
  }
}

export interface JobSearchWithMatchesResponse {
  search_response: JobSearchResponse
  matches: Record<string, SkillMatchResult>
}

// ── Skill Gap ─────────────────────────────────────────────────────────────

export interface SkillGapAnalysis {
  job_id: string
  job_title: string
  company: string
  user_skills: string[]
  required_skills: string[]
  matched_skills: string[]
  missing_skills: string[]
  relevant_projects: string[]
  recommended_preparation: string[]
}

// ── Deep Analysis ─────────────────────────────────────────────────────────

export interface ResumeJobAnalysisRequest {
  job_id: string
  custom_resume_text?: string | null
}

export interface ResumeJobAnalysisResponse {
  job_id: string
  job_title: string
  company: string
  strengths: string[]
  missing_requirements: string[]
  relevant_projects: string[]
  resume_keywords_to_consider: string[]
  potential_weaknesses: string[]
  interview_preparation_topics: string[]
  transparent_assessment: string
}

// ── Application Tracker ───────────────────────────────────────────────────

export type ApplicationStatusEnum = "saved" | "applied" | "interview" | "rejected" | "offer"

export interface ApplicationTrackItem {
  job_id: string
  title: string
  company: string
  location: string
  apply_url: string
  status: ApplicationStatusEnum
  saved_at: string
  applied_at?: string | null
  interview_date?: string | null
  notes?: string | null
  is_user_confirmed: boolean
}

export interface UpdateApplicationStatusRequest {
  status: ApplicationStatusEnum
  notes?: string | null
  interview_date?: string | null
}
