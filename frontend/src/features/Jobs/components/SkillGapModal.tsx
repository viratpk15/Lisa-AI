/**
 * Lisa AIOS — Skill Gap & Deep Analysis Modal
 * Uses real backend field names from SkillGapAnalysis and ResumeJobAnalysisResponse.
 */

import { useState } from "react"
import { motion } from "framer-motion"
import {
  X,
  CheckCircle2,
  AlertTriangle,
  Layers,
  BookOpen,
  Target,
  Loader2,
  Building2,
  Briefcase,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { useSkillGapMutation, useDeepAnalysisMutation } from "../queries"
import type { JobOpportunity, SkillGapAnalysis, ResumeJobAnalysisResponse } from "../types"

interface SkillGapModalProps {
  isOpen: boolean
  job: JobOpportunity
  onClose: () => void
}

export function SkillGapModal({ isOpen, job, onClose }: SkillGapModalProps) {
  const [activeView, setActiveView] = useState<"gap" | "deep">("gap")

  // Gap: takes jobId string; Deep: takes ResumeJobAnalysisRequest object
  const gapMutation = useSkillGapMutation()
  const deepMutation = useDeepAnalysisMutation()

  if (!isOpen) return null

  const gap: SkillGapAnalysis | undefined = gapMutation.data
  const deep: ResumeJobAnalysisResponse | undefined = deepMutation.data

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, scale: 0.96, y: 8 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.96 }}
        className="w-full max-w-3xl max-h-[90vh] flex flex-col rounded-2xl border border-border bg-card shadow-2xl overflow-hidden"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-border bg-card/60 shrink-0">
          <div className="min-w-0">
            <h2 className="text-lg font-semibold text-foreground line-clamp-1">{job.title}</h2>
            <div className="flex items-center gap-2 text-xs text-muted-foreground mt-0.5">
              <Building2 className="h-3.5 w-3.5" />
              <span>{job.company}</span>
              <span>·</span>
              <Briefcase className="h-3.5 w-3.5" />
              <span>{job.employment_type.replace("_", "-")}</span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors ml-4 shrink-0"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Tab Switch */}
        <div className="flex border-b border-border shrink-0">
          {(["gap", "deep"] as const).map((view) => (
            <button
              key={view}
              onClick={() => setActiveView(view)}
              className={`flex-1 text-sm font-medium py-2.5 border-b-2 transition-colors ${
                activeView === view
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              {view === "gap" ? "Skill Gap Analysis" : "Deep Resume Analysis"}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* ─── GAP TAB ─── */}
          {activeView === "gap" && (
            <div className="space-y-5">
              {!gap && !gapMutation.isPending && !gapMutation.isError && (
                <div className="flex flex-col items-center justify-center py-12 gap-4">
                  <div className="p-4 rounded-full bg-primary/10 text-primary">
                    <Target className="h-8 w-8" />
                  </div>
                  <div className="text-center">
                    <h3 className="font-semibold text-foreground">Skill Gap Analysis</h3>
                    <p className="text-xs text-muted-foreground mt-1 max-w-xs">
                      Compares your saved profile skills against job requirements. Requires a saved candidate profile.
                    </p>
                  </div>
                  <Button onClick={() => gapMutation.mutate(job.id)} className="gap-2">
                    <Target className="h-4 w-4" />
                    Run Gap Analysis
                  </Button>
                </div>
              )}
              {gapMutation.isPending && (
                <div className="flex flex-col items-center justify-center py-16 gap-3">
                  <Loader2 className="h-8 w-8 animate-spin text-primary" />
                  <p className="text-sm text-muted-foreground">Comparing skills against job requirements...</p>
                </div>
              )}
              {gapMutation.isError && (
                <div className="flex flex-col items-center gap-3 py-8">
                  <div className="flex items-center gap-2 p-3 text-xs text-destructive rounded-lg bg-destructive/10 border border-destructive/20">
                    <AlertTriangle className="h-4 w-4 shrink-0" />
                    {gapMutation.error?.message || "Gap analysis failed. Ensure you have saved a candidate profile first."}
                  </div>
                  <Button variant="outline" size="sm" onClick={() => gapMutation.mutate(job.id)}>Retry</Button>
                </div>
              )}
              {gap && (
                <div className="space-y-5">
                  {/* Matched */}
                  <div className="space-y-2">
                    <h4 className="flex items-center gap-2 text-sm font-semibold text-emerald-600">
                      <CheckCircle2 className="h-4 w-4" />
                      Matched Skills ({gap.matched_skills.length})
                    </h4>
                    {gap.matched_skills.length > 0 ? (
                      <div className="flex flex-wrap gap-1.5">
                        {gap.matched_skills.map((s) => (
                          <span key={s} className="px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-700 text-xs border border-emerald-500/20 font-medium">✓ {s}</span>
                        ))}
                      </div>
                    ) : (
                      <p className="text-xs text-muted-foreground italic">No direct skill matches with saved profile.</p>
                    )}
                  </div>

                  {/* Missing */}
                  {gap.missing_skills.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="flex items-center gap-2 text-sm font-semibold text-red-600">
                        <AlertTriangle className="h-4 w-4" />
                        Missing Skills ({gap.missing_skills.length})
                      </h4>
                      <div className="flex flex-wrap gap-1.5">
                        {gap.missing_skills.map((s) => (
                          <span key={s} className="px-2.5 py-1 rounded-lg bg-red-500/10 text-red-700 text-xs border border-red-500/20 font-medium">△ {s}</span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Relevant Projects */}
                  {gap.relevant_projects.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="flex items-center gap-2 text-sm font-semibold text-blue-600">
                        <Layers className="h-4 w-4" />
                        Relevant Existing Projects
                      </h4>
                      <ul className="space-y-1">
                        {gap.relevant_projects.map((proj, idx) => (
                          <li key={idx} className="text-xs text-muted-foreground flex items-start gap-1.5">
                            <span className="text-blue-500 mt-0.5">•</span>{proj}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Preparation */}
                  {gap.recommended_preparation.length > 0 && (
                    <div className="rounded-xl bg-primary/5 border border-primary/20 p-4 space-y-2">
                      <h4 className="flex items-center gap-2 text-sm font-semibold text-primary">
                        <BookOpen className="h-4 w-4" />
                        Recommended Preparation
                      </h4>
                      <ul className="space-y-2">
                        {gap.recommended_preparation.map((item, idx) => (
                          <li key={idx} className="text-xs text-foreground flex items-start gap-2">
                            <span className="font-bold text-primary mt-0.5 shrink-0">{idx + 1}.</span>{item}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* ─── DEEP ANALYSIS TAB ─── */}
          {activeView === "deep" && (
            <div className="space-y-5">
              {!deep && !deepMutation.isPending && !deepMutation.isError && (
                <div className="flex flex-col items-center justify-center py-12 gap-4">
                  <div className="p-4 rounded-full bg-primary/10 text-primary">
                    <BookOpen className="h-8 w-8" />
                  </div>
                  <div className="text-center">
                    <h3 className="font-semibold text-foreground">Deep Resume-to-Job Analysis</h3>
                    <p className="text-xs text-muted-foreground mt-1 max-w-xs">
                      Detailed comparison of your full profile vs this job: strengths, gaps, interview prep, and keywords.
                    </p>
                  </div>
                  <Button onClick={() => deepMutation.mutate({ job_id: job.id })} className="gap-2">
                    <BookOpen className="h-4 w-4" />
                    Run Deep Analysis
                  </Button>
                </div>
              )}
              {deepMutation.isPending && (
                <div className="flex flex-col items-center justify-center py-16 gap-3">
                  <Loader2 className="h-8 w-8 animate-spin text-primary" />
                  <p className="text-sm text-muted-foreground">Performing detailed resume-to-job evaluation...</p>
                </div>
              )}
              {deepMutation.isError && (
                <div className="flex flex-col items-center gap-3 py-8">
                  <div className="flex items-center gap-2 p-3 text-xs text-destructive rounded-lg bg-destructive/10 border border-destructive/20">
                    <AlertTriangle className="h-4 w-4 shrink-0" />
                    {deepMutation.error?.message || "Deep analysis failed."}
                  </div>
                  <Button variant="outline" size="sm" onClick={() => deepMutation.mutate({ job_id: job.id })}>Retry</Button>
                </div>
              )}
              {deep && (
                <div className="space-y-5 text-sm">
                  {deep.strengths.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="font-semibold text-emerald-600 flex items-center gap-2"><CheckCircle2 className="h-4 w-4" />Strengths</h4>
                      <ul className="space-y-1.5">{deep.strengths.map((s, i) => (
                        <li key={i} className="flex items-start gap-2 text-xs text-foreground"><span className="text-emerald-500 shrink-0 mt-0.5">✓</span>{s}</li>
                      ))}</ul>
                    </div>
                  )}
                  {deep.missing_requirements.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="font-semibold text-red-600 flex items-center gap-2"><AlertTriangle className="h-4 w-4" />Missing Requirements</h4>
                      <ul className="space-y-1.5">{deep.missing_requirements.map((s, i) => (
                        <li key={i} className="flex items-start gap-2 text-xs text-foreground"><span className="text-red-500 shrink-0 mt-0.5">△</span>{s}</li>
                      ))}</ul>
                    </div>
                  )}
                  {deep.resume_keywords_to_consider.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="font-semibold text-blue-600">Resume Keywords to Add</h4>
                      <div className="flex flex-wrap gap-1.5">{deep.resume_keywords_to_consider.map((kw) => (
                        <span key={kw} className="text-xs px-2 py-0.5 rounded bg-blue-500/10 text-blue-700 border border-blue-500/20">{kw}</span>
                      ))}</div>
                    </div>
                  )}
                  {deep.interview_preparation_topics.length > 0 && (
                    <div className="rounded-xl bg-primary/5 border border-primary/20 p-4 space-y-2">
                      <h4 className="font-semibold text-primary flex items-center gap-2"><BookOpen className="h-4 w-4" />Interview Preparation Topics</h4>
                      <ul className="space-y-1.5">{deep.interview_preparation_topics.map((t, i) => (
                        <li key={i} className="text-xs text-foreground flex items-start gap-2"><span className="text-primary font-bold mt-0.5 shrink-0">{i + 1}.</span>{t}</li>
                      ))}</ul>
                    </div>
                  )}
                  {deep.transparent_assessment && (
                    <div className="rounded-xl border border-border/60 bg-muted/30 p-4 text-xs text-muted-foreground italic">
                      {deep.transparent_assessment}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="flex justify-end px-6 py-4 border-t border-border bg-card/80 shrink-0">
          <Button variant="outline" onClick={onClose}>Close</Button>
        </div>
      </motion.div>
    </div>
  )
}
