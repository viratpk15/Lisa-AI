/**
 * Lisa AIOS — Resume Upload & Extraction Confirmation Modal
 * Uses real backend CandidateProfile schema fields.
 * STRICT: Never saves extracted data without user explicit confirmation.
 * is_confirmed_by_user starts false; only set to true on explicit user confirmation.
 */

import { useState, useRef } from "react"
import { motion } from "framer-motion"
import {
  UploadCloud,
  FileText,
  AlertCircle,
  CheckCircle2,
  X,
  Sparkles,
  Loader2,
  GraduationCap,
  Code2,
  Briefcase,
  Layers,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useExtractResumeMutation, useSaveCandidateProfileMutation } from "../queries"
import type { CandidateProfile } from "../types"

interface ResumeUploadModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: (profile: CandidateProfile) => void
}

export function ResumeUploadModal({ isOpen, onClose, onSuccess }: ResumeUploadModalProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [dragOver, setDragOver] = useState(false)
  const [extractedProfile, setExtractedProfile] = useState<CandidateProfile | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const extractMutation = useExtractResumeMutation()
  const saveMutation = useSaveCandidateProfileMutation()

  if (!isOpen) return null

  const validateAndSetFile = (file: File) => {
    setErrorMessage(null)
    const ext = "." + (file.name.split(".").pop()?.toLowerCase() ?? "")
    if (![".pdf", ".docx", ".txt"].includes(ext)) {
      setErrorMessage("Please select a PDF, DOCX, or TXT file.")
      return
    }
    if (file.size > 10 * 1024 * 1024) {
      setErrorMessage("Resume file must be under 10MB.")
      return
    }
    setSelectedFile(file)
  }

  const handleStartExtraction = async () => {
    if (!selectedFile) return
    setErrorMessage(null)
    try {
      const result = await extractMutation.mutateAsync(selectedFile)
      // Backend returns CandidateProfile with is_confirmed_by_user = false
      setExtractedProfile(result)
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : "Failed to parse resume")
    }
  }

  const handleConfirmAndSave = async () => {
    if (!extractedProfile) return
    setErrorMessage(null)
    // User explicitly confirmed — set flag before saving
    const confirmedProfile: CandidateProfile = {
      ...extractedProfile,
      is_confirmed_by_user: true,
    }
    try {
      const saved = await saveMutation.mutateAsync(confirmedProfile)
      onSuccess(saved)
      onClose()
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : "Failed to save confirmed profile")
    }
  }

  const allSkills = extractedProfile?.all_normalized_skills ?? []

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.96 }}
        className="relative w-full max-w-3xl max-h-[90vh] flex flex-col rounded-2xl border border-border bg-card shadow-2xl overflow-hidden"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-border bg-card/60">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10 text-primary">
              <FileText className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-foreground">
                {extractedProfile ? "Review Extracted Profile" : "Upload Resume / CV"}
              </h2>
              <p className="text-xs text-muted-foreground">
                {extractedProfile
                  ? "Verify every field below. Nothing is saved until you click Confirm."
                  : "PDF, DOCX, or TXT — Lisa extracts; you review and confirm."}
              </p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {errorMessage && (
            <div className="flex items-center gap-2 p-3 text-xs text-destructive rounded-lg bg-destructive/10 border border-destructive/20">
              <AlertCircle className="h-4 w-4 shrink-0" />
              {errorMessage}
            </div>
          )}

          {!extractedProfile ? (
            /* ── Upload Step ── */
            <div className="space-y-5">
              <div
                onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
                onDragLeave={() => setDragOver(false)}
                onDrop={(e) => { e.preventDefault(); setDragOver(false); if (e.dataTransfer.files[0]) validateAndSetFile(e.dataTransfer.files[0]) }}
                onClick={() => fileInputRef.current?.click()}
                className={`flex flex-col items-center justify-center p-8 border-2 border-dashed rounded-xl cursor-pointer transition-all ${
                  dragOver ? "border-primary bg-primary/5 scale-[1.01]" : "border-border/80 hover:border-primary/60 bg-muted/20 hover:bg-muted/40"
                }`}
              >
                <input ref={fileInputRef} type="file" accept=".pdf,.docx,.txt" className="hidden" onChange={(e) => { if (e.target.files?.[0]) validateAndSetFile(e.target.files[0]) }} />
                <div className="p-4 rounded-full bg-primary/10 text-primary mb-3">
                  <UploadCloud className="h-8 w-8" />
                </div>
                <span className="text-sm font-medium text-foreground">
                  {selectedFile ? selectedFile.name : "Click to select or drag & drop"}
                </span>
                <span className="text-xs text-muted-foreground mt-1">PDF, DOCX, TXT (up to 10MB)</span>
                {selectedFile && (
                  <span className="mt-2 text-xs font-mono text-emerald-500 font-medium">
                    ✓ {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                  </span>
                )}
              </div>

              <div className="flex items-start gap-2.5 p-3.5 rounded-lg bg-secondary/40 border border-border/60 text-xs text-muted-foreground">
                <Sparkles className="h-4 w-4 text-primary shrink-0 mt-0.5" />
                <span>
                  <span className="font-semibold text-foreground">Verification guarantee: </span>
                  Lisa extracts and normalizes your credentials. You review every field before anything is saved. Lisa never submits on your behalf.
                </span>
              </div>

              <div className="flex justify-end gap-3">
                <Button variant="ghost" onClick={onClose}>Cancel</Button>
                <Button onClick={handleStartExtraction} disabled={!selectedFile || extractMutation.isPending} className="gap-2">
                  {extractMutation.isPending ? <><Loader2 className="h-4 w-4 animate-spin" />Extracting...</> : <><FileText className="h-4 w-4" />Extract Profile</>}
                </Button>
              </div>
            </div>
          ) : (
            /* ── Review Step ── */
            <div className="space-y-6">
              <div className="flex items-center justify-between text-xs text-muted-foreground bg-amber-500/10 p-3 rounded-lg border border-amber-500/20">
                <span className="flex items-center gap-1.5 font-semibold text-amber-700">
                  <AlertCircle className="h-4 w-4" />
                  This data has NOT been saved yet. Review below, then click Confirm.
                </span>
                <Button variant="ghost" size="sm" onClick={() => setExtractedProfile(null)} className="h-7 text-xs">
                  Re-upload
                </Button>
              </div>

              {/* Personal */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {[
                  { label: "Name", key: "name" as const },
                  { label: "Email", key: "email" as const },
                  { label: "Phone", key: "phone" as const },
                ].map(({ label, key }) => (
                  <div key={key}>
                    <label className="text-xs font-semibold text-muted-foreground">{label}</label>
                    <Input
                      value={(extractedProfile[key] as string) || ""}
                      onChange={(e) => setExtractedProfile({ ...extractedProfile, [key]: e.target.value })}
                      className="mt-1 h-9 text-sm"
                      placeholder={label}
                    />
                  </div>
                ))}
              </div>

              {/* Education */}
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
                  <GraduationCap className="h-4 w-4 text-primary" />
                  Education ({extractedProfile.education.length})
                </div>
                {extractedProfile.education.map((edu, idx) => (
                  <div key={idx} className="p-3 rounded-lg border border-border/70 bg-card/40 text-xs space-y-1">
                    <div className="flex justify-between font-semibold text-foreground text-sm">
                      <span>{edu.degree || "Degree"}{edu.branch ? ` — ${edu.branch}` : ""}</span>
                      <span className="font-mono text-muted-foreground">{edu.graduation_year || ""}</span>
                    </div>
                    <div className="text-muted-foreground">{edu.college}</div>
                    {edu.cgpa && <div className="text-emerald-500 font-mono">CGPA: {edu.cgpa}</div>}
                  </div>
                ))}
              </div>

              {/* Normalized Skills */}
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
                  <Code2 className="h-4 w-4 text-primary" />
                  Normalized Skills ({allSkills.length})
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {allSkills.map((skill) => (
                    <span
                      key={skill}
                      className="flex items-center gap-1 text-xs px-2.5 py-0.5 rounded-full bg-secondary border border-border/60 text-foreground"
                    >
                      {skill}
                      <button
                        onClick={() =>
                          setExtractedProfile({
                            ...extractedProfile,
                            all_normalized_skills: allSkills.filter((s) => s !== skill),
                          })
                        }
                        className="text-muted-foreground hover:text-destructive transition-colors"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              {/* Projects */}
              {extractedProfile.projects.length > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
                    <Layers className="h-4 w-4 text-primary" />
                    Projects ({extractedProfile.projects.length})
                  </div>
                  {extractedProfile.projects.map((proj, idx) => (
                    <div key={idx} className="p-3 rounded-lg border border-border/70 bg-card/40 text-xs space-y-1">
                      <div className="font-semibold text-foreground text-sm">{proj.title}</div>
                      <p className="text-muted-foreground line-clamp-2">{proj.description}</p>
                      {/* Backend: tech_stack not technologies */}
                      {proj.tech_stack.length > 0 && (
                        <div className="flex flex-wrap gap-1 pt-1">
                          {proj.tech_stack.map((t) => (
                            <span key={t} className="px-1.5 py-0.5 rounded bg-muted text-[10px] font-mono">{t}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Experiences */}
              {extractedProfile.experiences.length > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
                    <Briefcase className="h-4 w-4 text-primary" />
                    Experience ({extractedProfile.experiences.length})
                  </div>
                  {extractedProfile.experiences.map((exp, idx) => (
                    <div key={idx} className="p-3 rounded-lg border border-border/70 bg-card/40 text-xs space-y-1">
                      <div className="flex justify-between font-semibold text-foreground text-sm">
                        <span>{exp.role} @ {exp.company}</span>
                        <span className="font-mono text-muted-foreground">{exp.duration || (exp.is_internship ? "Internship" : "")}</span>
                      </div>
                      {exp.description && <p className="text-muted-foreground line-clamp-2">{exp.description}</p>}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        {extractedProfile && (
          <div className="flex items-center justify-between px-6 py-4 border-t border-border bg-card/80">
            <span className="text-xs text-muted-foreground flex items-center gap-1.5">
              <CheckCircle2 className="h-3.5 w-3.5 text-muted-foreground" />
              {allSkills.length} skills extracted from resume
            </span>
            <div className="flex gap-3">
              <Button variant="outline" onClick={onClose}>Discard</Button>
              <Button onClick={handleConfirmAndSave} disabled={saveMutation.isPending} className="gap-2">
                {saveMutation.isPending ? <><Loader2 className="h-4 w-4 animate-spin" />Saving...</> : <><CheckCircle2 className="h-4 w-4" />Confirm & Save</>}
              </Button>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  )
}
