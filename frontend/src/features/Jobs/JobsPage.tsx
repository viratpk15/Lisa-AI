/**
 * Lisa AIOS — Jobs & Internship Finder Master Page
 * Uses real backend response shapes: JobSearchWithMatchesResponse.
 */

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import {
  Briefcase,
  Search,
  User,
  UploadCloud,
  ClipboardList,
  AlertCircle,
  Loader2,
  Sparkles,
  Info,
  Target,
  MapPin,
  ShieldCheck,
  RefreshCw,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { JobSearchFiltersPanel } from "./components/JobSearchFilters"
import { JobOpportunityCard } from "./components/JobOpportunityCard"
import { ResumeUploadModal } from "./components/ResumeUploadModal"
import { SkillGapModal } from "./components/SkillGapModal"
import { ApplicationTrackerTab } from "./components/ApplicationTrackerTab"
import { CandidateProfileEditor } from "./components/CandidateProfileEditor"
import { useQueryClient } from "@tanstack/react-query"
import {
  useCandidateProfileQuery,
  useJobSearchMutation,
  useTrackJobMutation,
  jobsQueryKeys,
} from "./queries"
import type {
  JobOpportunity,
  JobSearchFilters,
  JobSearchWithMatchesResponse,
  CandidateProfile,
} from "./types"
import { cn } from "@/lib/utils"

type ActiveTab = "search" | "profile" | "tracker"

export default function JobsPage() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<ActiveTab>("search")
  const [showResumeUpload, setShowResumeUpload] = useState(false)
  const [selectedJobForGap, setSelectedJobForGap] = useState<JobOpportunity | null>(null)
  const [searchResults, setSearchResults] = useState<JobSearchWithMatchesResponse | null>(null)
  const [trackedJobIds, setTrackedJobIds] = useState<Set<string>>(new Set())
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [activeFilters, setActiveFilters] = useState<JobSearchFilters | null>(null)

  const profileQuery = useCandidateProfileQuery()
  const searchMutation = useJobSearchMutation()
  const trackMutation = useTrackJobMutation()

  const profile = profileQuery.data

  const handleSearch = async (filters: JobSearchFilters) => {
    setErrorMessage(null)
    try {
      const results = await searchMutation.mutateAsync(filters)
      setSearchResults(results)
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : "Search failed. Please try again.")
    }
  }

  const handleTrackJob = async (job: JobOpportunity) => {
    if (trackedJobIds.has(job.id)) return
    try {
      await trackMutation.mutateAsync({ jobId: job.id, status: "saved" })
      setTrackedJobIds((prev) => new Set([...prev, job.id]))
    } catch { /* silent — user can retry via tracker */ }
  }

  const handleFetchForProfile = (targetProfile?: CandidateProfile | null) => {
    const p = targetProfile || profile
    if (!p) {
      setActiveTab("profile")
      return
    }
    const roles = p.preferred_roles?.length ? p.preferred_roles.join(", ") : undefined
    const locations = p.preferred_locations?.length ? p.preferred_locations.join(", ") : undefined
    const isIntern = ["student", "intern"].includes(p.experience_level || "")
    const filters: JobSearchFilters = {
      role: roles,
      location: locations,
      experience_level: p.experience_level || undefined,
      is_remote: p.remote_preference === "remote_only" ? true : undefined,
      employment_type: isIntern ? "internship" : undefined,
      sort_by: "relevance",
      limit: 25,
    }
    setActiveFilters(filters)
    handleSearch(filters)
  }

  const handleProfileSaved = (savedProfile: CandidateProfile) => {
    setActiveTab("search")
    handleFetchForProfile(savedProfile)
  }

  const tabs: { id: ActiveTab; label: string; icon: typeof Briefcase }[] = [
    { id: "search", label: "Find Opportunities", icon: Search },
    { id: "profile", label: "My Profile", icon: User },
    { id: "tracker", label: "Application Tracker", icon: ClipboardList },
  ]

  // Real backend response shape: { search_response: {...}, matches: {...} }
  const jobs = searchResults?.search_response.jobs ?? []
  const totalResults = searchResults?.search_response.total_results ?? 0
  const matchMap = searchResults?.matches ?? {}
  const hasLiveResults = searchResults?.search_response.has_live_results ?? false
  const providerUsed = searchResults?.search_response.provider_used ?? ""

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="max-w-5xl mx-auto space-y-6 py-2"
    >
      {/* Page Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-primary/10 text-primary">
              <Briefcase className="h-6 w-6" />
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-foreground">
              Jobs & Internships
            </h1>
          </div>
          <p className="text-sm text-muted-foreground pl-14">
            Real opportunities from live sources. Zero fabricated postings. Zero phantom companies.
          </p>
        </div>
        <Button variant="outline" size="sm" className="gap-2 shrink-0" onClick={() => setShowResumeUpload(true)}>
          <UploadCloud className="h-4 w-4" />
          Upload Resume
        </Button>
      </div>

      {/* No Profile Notice */}
      {!profile && activeTab === "search" && !profileQuery.isLoading && (
        <div className="flex items-center gap-3 p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-sm">
          <Info className="h-4 w-4 text-amber-600 shrink-0" />
          <div className="flex-1">
            <span className="font-medium text-amber-800 dark:text-amber-400">No profile set up. </span>
            <span className="text-amber-700 dark:text-amber-500">Search works without a profile, but match scores require your saved skills.</span>
          </div>
          <Button variant="outline" size="sm" onClick={() => setActiveTab("profile")} className="text-xs border-amber-500/30 text-amber-700 hover:bg-amber-500/10 shrink-0">
            Set Up Profile
          </Button>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="flex border-b border-border">
        {tabs.map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors",
                activeTab === tab.id ? "border-primary text-primary" : "border-transparent text-muted-foreground hover:text-foreground"
              )}
            >
              <Icon className="h-4 w-4" />
              {tab.label}
            </button>
          )
        })}
      </div>

      <AnimatePresence mode="wait">
        <motion.div key={activeTab} initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -4 }} transition={{ duration: 0.15 }}>

          {/* ─── SEARCH TAB ─── */}
          {activeTab === "search" && (
            <div className="space-y-5">
              {/* Active Profile Match Spec Space */}
              {profile && (
                <div className="rounded-xl border border-primary/25 bg-primary/5 p-4 space-y-3">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-primary/15 pb-2.5">
                    <div className="flex items-center gap-2">
                      <div className="p-1.5 rounded-lg bg-primary/10 text-primary">
                        <Target className="h-4 w-4" />
                      </div>
                      <div>
                        <h3 className="text-xs font-semibold text-foreground tracking-tight flex items-center gap-1.5">
                          <span>Active Profile Match Criteria</span>
                          <span className="text-[10px] font-normal text-primary/80 bg-primary/10 px-2 py-0.2 rounded-full border border-primary/20">
                            Synced from Profile
                          </span>
                        </h3>
                        <p className="text-[11px] text-muted-foreground">
                          Opportunities are fetched and evaluated directly against your saved target roles, locations, and skills.
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 self-start sm:self-auto">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleFetchForProfile(profile)}
                        disabled={searchMutation.isPending}
                        className="text-xs h-7 px-2.5 gap-1.5 border-primary/30 text-primary hover:bg-primary/10 cursor-pointer"
                      >
                        <RefreshCw className={cn("h-3 w-3", searchMutation.isPending && "animate-spin")} />
                        <span>Fetch Matches</span>
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setActiveTab("profile")}
                        className="text-xs h-7 px-2 text-muted-foreground hover:text-foreground cursor-pointer"
                      >
                        Edit Profile
                      </Button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2.5 text-xs">
                    {/* Target Locations */}
                    <div className="p-2 rounded-lg bg-background/60 border border-border/50 space-y-0.5">
                      <span className="text-[10px] uppercase font-mono text-muted-foreground font-semibold flex items-center gap-1">
                        <MapPin className="h-3 w-3 text-sky-400" />
                        Target Locations
                      </span>
                      <div className="font-medium text-foreground truncate" title={profile.preferred_locations?.join(", ") || "Any location"}>
                        {profile.preferred_locations?.length ? profile.preferred_locations.join(", ") : "Any Location"}
                      </div>
                    </div>

                    {/* Target Roles */}
                    <div className="p-2 rounded-lg bg-background/60 border border-border/50 space-y-0.5">
                      <span className="text-[10px] uppercase font-mono text-muted-foreground font-semibold flex items-center gap-1">
                        <Briefcase className="h-3 w-3 text-indigo-400" />
                        Target Roles
                      </span>
                      <div className="font-medium text-foreground truncate" title={profile.preferred_roles?.join(", ") || "All Tech Roles"}>
                        {profile.preferred_roles?.length ? profile.preferred_roles.join(", ") : "All Tech Roles"}
                      </div>
                    </div>

                    {/* Experience & Mode */}
                    <div className="p-2 rounded-lg bg-background/60 border border-border/50 space-y-0.5">
                      <span className="text-[10px] uppercase font-mono text-muted-foreground font-semibold flex items-center gap-1">
                        <Sparkles className="h-3 w-3 text-amber-400" />
                        Experience & Mode
                      </span>
                      <div className="font-medium text-foreground capitalize">
                        {profile.experience_level?.replace("_", " ") || "Entry-level"} • {profile.remote_preference?.replace("_", " ") || "Any"}
                      </div>
                    </div>

                    {/* Evaluated Skills */}
                    <div className="p-2 rounded-lg bg-background/60 border border-border/50 space-y-0.5">
                      <span className="text-[10px] uppercase font-mono text-muted-foreground font-semibold flex items-center gap-1">
                        <ShieldCheck className="h-3 w-3 text-emerald-400" />
                        Skills Evaluated
                      </span>
                      <div className="font-medium text-emerald-400">
                        {profile.all_normalized_skills?.length || 0} normalized skills
                      </div>
                    </div>
                  </div>

                  {profile.all_normalized_skills?.length > 0 && (
                    <div className="flex flex-wrap items-center gap-1 pt-1">
                      <span className="text-[10px] text-muted-foreground mr-1">Skills:</span>
                      {profile.all_normalized_skills.slice(0, 10).map((sk) => (
                        <span key={sk} className="text-[10px] px-2 py-0.5 rounded-md bg-secondary/80 text-foreground border border-border/50">
                          {sk}
                        </span>
                      ))}
                      {profile.all_normalized_skills.length > 10 && (
                        <span className="text-[10px] text-muted-foreground">+{profile.all_normalized_skills.length - 10} more</span>
                      )}
                    </div>
                  )}
                </div>
              )}

              <JobSearchFiltersPanel
                onSearch={handleSearch}
                isLoading={searchMutation.isPending}
                activeFilters={activeFilters}
              />

              {errorMessage && (
                <div className="flex items-center gap-2 p-3 text-sm text-destructive rounded-lg bg-destructive/10 border border-destructive/20">
                  <AlertCircle className="h-4 w-4 shrink-0" />
                  {errorMessage}
                </div>
              )}

              {searchMutation.isPending && (
                <div className="flex flex-col items-center justify-center py-16 gap-3">
                  <Loader2 className="h-8 w-8 animate-spin text-primary" />
                  <p className="text-sm text-muted-foreground">Querying live job databases (RemoteOK, Arbeitnow)...</p>
                </div>
              )}

              {searchResults && !searchMutation.isPending && (
                <div className="space-y-4">
                  {/* Results Header */}
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold text-foreground">
                        {hasLiveResults ? `${totalResults} live opportunities` : "No live results"}
                      </span>
                      {profile && Object.keys(matchMap).length > 0 && (
                        <span className="text-xs text-primary bg-primary/10 px-2 py-0.5 rounded-full border border-primary/20 flex items-center gap-1">
                          <Sparkles className="h-3 w-3" />
                          Matched against {profile.all_normalized_skills.length} skills
                        </span>
                      )}
                    </div>
                    <span className="text-xs font-mono text-muted-foreground bg-secondary px-2 py-0.5 rounded-full border border-border/50">
                      {providerUsed}
                    </span>
                  </div>

                  {/* Disclaimer */}
                  {searchResults.search_response.disclaimer && (
                    <p className="text-xs text-muted-foreground italic">
                      {searchResults.search_response.disclaimer}
                    </p>
                  )}

                  {/* No results */}
                  {jobs.length === 0 && (
                    <div className="flex flex-col items-center justify-center py-16 gap-3 text-center">
                      <Search className="h-8 w-8 text-muted-foreground" />
                      <div>
                        <h3 className="font-semibold text-foreground">
                          {searchResults.search_response.status_message || "No matching opportunities were found."}
                        </h3>
                        <p className="text-xs text-muted-foreground mt-1 max-w-sm">
                          Lisa never displays fabricated results. Try broader keywords or verify external provider connectivity.
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Job Cards */}
                  <div className="grid grid-cols-1 gap-4">
                    {jobs.map((job) => (
                      <JobOpportunityCard
                        key={job.id}
                        job={job}
                        matchResult={matchMap[job.id]}
                        isTracked={trackedJobIds.has(job.id)}
                        onTrack={handleTrackJob}
                        onViewGap={(j) => setSelectedJobForGap(j)}
                        onDeepAnalysis={(j) => setSelectedJobForGap(j)}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Empty state — no search initiated */}
              {!searchResults && !searchMutation.isPending && (
                <div className="flex flex-col items-center justify-center py-20 gap-4 text-center">
                  <div className="p-5 rounded-2xl bg-primary/10 text-primary">
                    <Briefcase className="h-10 w-10" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground text-lg">Find Your Next Opportunity</h3>
                    <p className="text-sm text-muted-foreground mt-1.5 max-w-sm">
                      Search real job listings from RemoteOK, Arbeitnow, and Adzuna (if configured). Lisa compares them against your skill profile.
                    </p>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    💡 Try: "Machine Learning Engineer", "React Developer Internship", "Python Backend"
                  </p>
                </div>
              )}
            </div>
          )}

          {/* ─── PROFILE TAB ─── */}
          {activeTab === "profile" && (
            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-1 border-b border-border/60">
                <div>
                  <h2 className="text-base font-semibold text-foreground">Candidate Profile</h2>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    Build your profile manually or upload your resume. All data requires explicit save.
                  </p>
                </div>
                <div className="flex items-center gap-2 self-start sm:self-auto">
                  <Button
                    variant="outline"
                    size="sm"
                    className="gap-2 text-xs cursor-pointer"
                    onClick={() => void profileQuery.refetch()}
                    disabled={profileQuery.isFetching}
                    title="Re-sync profile from server"
                  >
                    <RefreshCw className={cn("h-3.5 w-3.5", profileQuery.isFetching && "animate-spin text-primary")} />
                    <span>{profileQuery.isFetching ? "Refreshing..." : "Refresh Profile"}</span>
                  </Button>

                  <Button variant="outline" size="sm" className="gap-2 text-xs cursor-pointer" onClick={() => setShowResumeUpload(true)}>
                    <UploadCloud className="h-4 w-4" />
                    Upload Resume
                  </Button>
                </div>
              </div>
              <CandidateProfileEditor existingProfile={profile} onSaved={handleProfileSaved} />
            </div>
          )}

          {/* ─── TRACKER TAB ─── */}
          {activeTab === "tracker" && (
            <div className="space-y-4">
              <div>
                <h2 className="text-base font-semibold text-foreground">Application Tracker</h2>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Status updates are always manual. Lisa never submits or auto-modifies applications.
                </p>
              </div>
              <ApplicationTrackerTab />
            </div>
          )}

        </motion.div>
      </AnimatePresence>

      {/* Modals */}
      <AnimatePresence>
        {showResumeUpload && (
          <ResumeUploadModal
            isOpen={showResumeUpload}
            onClose={() => setShowResumeUpload(false)}
            onSuccess={(savedProfile) => {
              setShowResumeUpload(false)
              setActiveTab("profile")
              queryClient.setQueryData(jobsQueryKeys.profile(), savedProfile)
              void profileQuery.refetch()
            }}
          />
        )}
      </AnimatePresence>
      <AnimatePresence>
        {selectedJobForGap && (
          <SkillGapModal isOpen={true} job={selectedJobForGap} onClose={() => setSelectedJobForGap(null)} />
        )}
      </AnimatePresence>
    </motion.div>
  )
}
