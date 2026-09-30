/**
 * Lisa AIOS — Job Opportunity Card
 * Uses real backend field names from JobOpportunity and SkillMatchResult schemas.
 * Match score is 100% deterministic: 60% skill overlap + 20% exp + 20% location.
 * Salary shows real provider text or explicitly "Not specified".
 */

import { useState } from "react"
import { motion } from "framer-motion"
import {
  Building2,
  MapPin,
  Clock,
  ExternalLink,
  CheckCircle2,
  AlertTriangle,
  Bookmark,
  BookmarkCheck,
  Zap,
  Globe,
  ChevronDown,
  ChevronUp,
  TrendingUp,
  DollarSign,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import type { JobOpportunity, SkillMatchResult } from "../types"
import { cn } from "@/lib/utils"

interface JobOpportunityCardProps {
  job: JobOpportunity
  matchResult?: SkillMatchResult
  isTracked?: boolean
  onTrack: (job: JobOpportunity) => void
  onViewGap: (job: JobOpportunity) => void
  onDeepAnalysis: (job: JobOpportunity) => void
}

function formatPostedDate(dateStr?: string | null): string {
  if (!dateStr) return ""
  try {
    const d = new Date(dateStr)
    const now = new Date()
    const diffDays = Math.floor((now.getTime() - d.getTime()) / (1000 * 60 * 60 * 24))
    if (diffDays === 0) return "Today"
    if (diffDays === 1) return "Yesterday"
    if (diffDays < 7) return `${diffDays} days ago`
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
    return d.toLocaleDateString("en-IN", { month: "short", day: "numeric" })
  } catch {
    return dateStr
  }
}

function employmentTypeBadge(type: string): string {
  const map: Record<string, string> = {
    internship: "Internship",
    full_time: "Full-time",
    part_time: "Part-time",
    contract: "Contract",
    entry_level: "Entry-level",
    graduate: "Graduate",
  }
  return map[type] || type
}

export function JobOpportunityCard({
  job,
  matchResult,
  isTracked,
  onTrack,
  onViewGap,
  onDeepAnalysis,
}: JobOpportunityCardProps) {
  const [expanded, setExpanded] = useState(false)

  const hasMatch = matchResult !== undefined
  const matchScore = matchResult?.match_score ?? 0
  // Strong match: ≥70 points out of 100 (documented algorithm)
  const isStrongMatch = matchScore >= 70

  // Salary: show real provider text or null — never invent
  const salaryDisplay = job.salary_or_stipend ?? null

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        "group relative rounded-xl border bg-card shadow-xs hover:shadow-sm transition-all duration-200",
        isStrongMatch ? "border-primary/30" : "border-border/70"
      )}
    >
      {isStrongMatch && (
        <div className="absolute inset-x-0 top-0 h-0.5 rounded-t-xl bg-linear-to-r from-primary/60 via-primary to-primary/60" />
      )}

      <div className="p-5 space-y-4">
        {/* Top Row */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0 space-y-1">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-secondary text-secondary-foreground">
                {employmentTypeBadge(job.employment_type)}
              </span>
              {job.is_remote && (
                <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 border border-emerald-500/20 flex items-center gap-1">
                  <Globe className="h-3 w-3" />
                  Remote
                </span>
              )}
              {job.remote_type === "hybrid" && !job.is_remote && (
                <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-600 border border-blue-500/20">
                  Hybrid
                </span>
              )}
              <span className="text-xs text-muted-foreground font-mono">{job.source_provider}</span>
            </div>

            <h3 className="text-base font-semibold text-foreground leading-tight line-clamp-2">
              {job.title}
            </h3>

            <div className="flex items-center gap-4 text-xs text-muted-foreground flex-wrap">
              <span className="flex items-center gap-1">
                <Building2 className="h-3.5 w-3.5" />
                {job.company}
              </span>
              <span className="flex items-center gap-1">
                <MapPin className="h-3.5 w-3.5" />
                {job.location}
              </span>
              {job.posted_date && (
                <span className="flex items-center gap-1">
                  <Clock className="h-3.5 w-3.5" />
                  {formatPostedDate(job.posted_date)}
                </span>
              )}
            </div>
          </div>

          {/* Match Score — only shown when profile exists */}
          {hasMatch && (
            <div className="flex flex-col items-center gap-1 shrink-0">
              <div
                className={cn(
                  "flex items-center justify-center rounded-xl px-3 py-2 border text-center min-w-16",
                  isStrongMatch
                    ? "bg-primary/10 border-primary/30 text-primary"
                    : matchScore >= 50
                    ? "bg-amber-500/10 border-amber-500/20 text-amber-600"
                    : "bg-secondary border-border text-muted-foreground"
                )}
              >
                <div>
                  <div className="text-lg font-bold leading-none">{Math.round(matchScore)}%</div>
                  <div className="text-[9px] uppercase tracking-wider font-medium mt-0.5 opacity-80">
                    match
                  </div>
                </div>
              </div>
              {isStrongMatch && (
                <span className="text-[10px] text-primary font-medium flex items-center gap-0.5">
                  <TrendingUp className="h-3 w-3" />
                  Strong
                </span>
              )}
            </div>
          )}
        </div>

        {/* Salary — real text from provider or nothing */}
        {salaryDisplay && (
          <div className="flex items-center gap-1.5 text-sm font-semibold text-emerald-600">
            <DollarSign className="h-4 w-4" />
            <span>{salaryDisplay}</span>
          </div>
        )}

        {/* Required Skills */}
        {job.required_skills.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {job.required_skills.slice(0, 8).map((skill) => (
              <span
                key={skill}
                className={cn(
                  "text-[11px] px-2 py-0.5 rounded-md font-medium border",
                  matchResult?.matched_required_skills?.includes(skill)
                    ? "bg-emerald-500/10 text-emerald-700 border-emerald-500/20"
                    : "bg-secondary text-muted-foreground border-border/60"
                )}
              >
                {skill}
              </span>
            ))}
            {job.required_skills.length > 8 && (
              <span className="text-[11px] text-muted-foreground px-2 py-0.5">
                +{job.required_skills.length - 8} more
              </span>
            )}
          </div>
        )}

        {/* Match Breakdown Expander */}
        {hasMatch && (
          <button
            onClick={() => setExpanded((prev) => !prev)}
            className="w-full flex items-center justify-between text-xs text-muted-foreground hover:text-foreground transition-colors py-1"
          >
            <span className="flex items-center gap-1.5 font-medium">
              <Zap className="h-3.5 w-3.5 text-primary" />
              Match breakdown (60% skill + 20% exp + 20% location)
            </span>
            {expanded ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
          </button>
        )}

        {expanded && matchResult && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            className="rounded-lg bg-muted/40 border border-border/60 p-4 space-y-3 text-xs"
          >
            {/* Score Breakdown */}
            <div className="grid grid-cols-3 gap-2">
              <div className="text-center p-2 rounded-lg bg-card border border-border/50">
                <div className="font-bold text-base text-foreground">
                  {matchResult.score_breakdown.skill_overlap_pts}/{matchResult.score_breakdown.skill_overlap_max}
                </div>
                <div className="text-muted-foreground mt-0.5">Skill Overlap</div>
              </div>
              <div className="text-center p-2 rounded-lg bg-card border border-border/50">
                <div className="font-bold text-base text-foreground">
                  {matchResult.score_breakdown.experience_match_pts}/{matchResult.score_breakdown.experience_match_max}
                </div>
                <div className="text-muted-foreground mt-0.5">Experience</div>
              </div>
              <div className="text-center p-2 rounded-lg bg-card border border-border/50">
                <div className="font-bold text-base text-foreground">
                  {matchResult.score_breakdown.location_match_pts}/{matchResult.score_breakdown.location_match_max}
                </div>
                <div className="text-muted-foreground mt-0.5">Location</div>
              </div>
            </div>

            {/* Match Reasons */}
            {matchResult.match_reasons.length > 0 && (
              <div className="space-y-1">
                <div className="font-semibold text-emerald-600 flex items-center gap-1.5">
                  <CheckCircle2 className="h-3.5 w-3.5" />
                  Why this matches
                </div>
                {matchResult.match_reasons.map((r, i) => (
                  <div key={i} className="text-foreground">{r}</div>
                ))}
              </div>
            )}

            {/* Gaps */}
            {matchResult.potential_gaps.length > 0 && (
              <div className="space-y-1">
                <div className="font-semibold text-amber-600 flex items-center gap-1.5">
                  <AlertTriangle className="h-3.5 w-3.5" />
                  Potential gaps
                </div>
                {matchResult.potential_gaps.map((g, i) => (
                  <div key={i} className="text-muted-foreground">{g}</div>
                ))}
              </div>
            )}
          </motion.div>
        )}

        {/* Actions */}
        <div className="flex items-center gap-2 pt-1">
          <Button asChild variant="default" size="sm" className="flex-1 gap-1.5">
            <a href={job.apply_url} target="_blank" rel="noopener noreferrer">
              <ExternalLink className="h-3.5 w-3.5" />
              Apply Now
            </a>
          </Button>
          <Button variant="outline" size="sm" onClick={() => onViewGap(job)} className="text-xs">
            Skill Gap
          </Button>
          <Button variant="ghost" size="sm" onClick={() => onDeepAnalysis(job)} className="text-xs px-2">
            Analysis
          </Button>
          <button
            onClick={() => onTrack(job)}
            className={cn(
              "p-2 rounded-lg border transition-colors",
              isTracked
                ? "border-primary/40 bg-primary/10 text-primary"
                : "border-border text-muted-foreground hover:border-primary/40 hover:text-primary"
            )}
            title={isTracked ? "Saved to tracker" : "Save job"}
          >
            {isTracked ? <BookmarkCheck className="h-4 w-4" /> : <Bookmark className="h-4 w-4" />}
          </button>
        </div>
      </div>
    </motion.div>
  )
}
