// frontend/src/features/Email/EmailDetail.tsx
import React, { useState } from "react"
import {
  Tag,
  Sparkles,
  ListTodo,
  ExternalLink,
  ShieldCheck,
  ShieldAlert,
  Calendar,
  Clock,
  User,
  Mail,
  CheckCircle2,
  Circle,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { EmptyState } from "@/components/common/EmptyState"
import { SenderAuthBadge } from "./SenderAuthBadge"
import type { EmailDetail as EmailDetailType } from "./api"

interface EmailDetailProps {
  email: EmailDetailType | null
  isLoading: boolean
  onClassify: () => void
  isClassifying: boolean
  onSummarize: () => void
  isSummarizing: boolean
  onExtractActions: () => void
  isExtractingActions: boolean
}

export const EmailDetail: React.FC<EmailDetailProps> = ({
  email,
  isLoading,
  onClassify,
  isClassifying,
  onSummarize,
  isSummarizing,
  onExtractActions,
  isExtractingActions,
}) => {
  const [viewOriginal, setViewOriginal] = useState(false)
  const [completedTasks, setCompletedTasks] = useState<Record<string, boolean>>({})

  if (isLoading) {
    return (
      <div className="p-6 space-y-5 h-full overflow-y-auto">
        <div className="space-y-2 border-b border-border/40 pb-4">
          <Skeleton className="h-6 w-3/4" />
          <div className="flex gap-3">
            <Skeleton className="h-4 w-40" />
            <Skeleton className="h-4 w-28" />
          </div>
        </div>
        <div className="flex gap-2">
          <Skeleton className="h-8 w-24" />
          <Skeleton className="h-8 w-28" />
          <Skeleton className="h-8 w-32" />
        </div>
        <Skeleton className="h-32 w-full rounded-xl" />
        <Skeleton className="h-40 w-full rounded-xl" />
      </div>
    )
  }

  if (!email) {
    return (
      <div className="h-full flex items-center justify-center p-6">
        <EmptyState
          icon={Mail}
          title="No email selected"
          description="Select an email from your inbox to inspect AI summaries, action items, deadlines, and cryptographic sender verification."
        />
      </div>
    )
  }

  const analysis = email.analysis
  const verification = email.verification
  const actionItems = analysis?.action_items

  // Extract key points from summary text if present
  let oneLineSummary = ""
  let keyPoints: string[] = []
  if (analysis?.summary_text) {
    const parts = analysis.summary_text.split("\n\n")
    oneLineSummary = parts[0].trim()
    if (parts.length > 1) {
      keyPoints = parts[1]
        .split("\n")
        .map((p) => p.replace(/^-\s*/, "").trim())
        .filter(Boolean)
    }
  }

  const toggleTask = (task: string) => {
    setCompletedTasks((prev) => ({
      ...prev,
      [task]: !prev[task],
    }))
  }

  return (
    <div className="h-full flex flex-col overflow-hidden bg-background">
      {/* Detail Header */}
      <div className="p-5 border-b border-border/60 shrink-0 bg-card/20 space-y-3">
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-1">
            <h2 className="text-base font-semibold text-foreground tracking-tight leading-snug">
              {email.subject || "(No Subject)"}
            </h2>
            <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground font-mono">
              <span className="flex items-center gap-1 text-foreground/90">
                <User className="w-3.5 h-3.5 text-primary" />
                <span>{email.sender}</span>
              </span>
              <span className="flex items-center gap-1">
                <Clock className="w-3.5 h-3.5" />
                <span>{new Date(email.received_at).toLocaleString()}</span>
              </span>
            </div>
          </div>
          <div className="shrink-0">
            <SenderAuthBadge
              isVerified={verification?.is_verified ?? false}
              spfStatus={verification?.spf_status}
              dkimStatus={verification?.dkim_status}
              dmarcStatus={verification?.dmarc_status}
            />
          </div>
        </div>

        {/* Action Button Toolbar */}
        <div className="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-border/30">
          <div className="flex flex-wrap items-center gap-2">
            <Button
              onClick={onClassify}
              disabled={isClassifying}
              variant="outline"
              size="sm"
              className="h-7 text-xs gap-1.5 cursor-pointer"
            >
              <Tag className="w-3 h-3 text-cyan-400" />
              <span>{isClassifying ? "Classifying..." : "Classify"}</span>
            </Button>
            <Button
              onClick={onSummarize}
              disabled={isSummarizing}
              variant="outline"
              size="sm"
              className="h-7 text-xs gap-1.5 cursor-pointer"
            >
              <Sparkles className="w-3 h-3 text-amber-400" />
              <span>{isSummarizing ? "Summarizing..." : "Summarize"}</span>
            </Button>
            <Button
              onClick={onExtractActions}
              disabled={isExtractingActions}
              variant="outline"
              size="sm"
              className="h-7 text-xs gap-1.5 cursor-pointer"
            >
              <ListTodo className="w-3 h-3 text-emerald-400" />
              <span>{isExtractingActions ? "Extracting..." : "Extract Actions"}</span>
            </Button>
          </div>

          <Button
            onClick={() => setViewOriginal(!viewOriginal)}
            variant="ghost"
            size="sm"
            className="h-7 text-xs font-mono text-muted-foreground hover:text-foreground cursor-pointer"
          >
            {viewOriginal ? "Show AI Summary" : "Open Original Message"}
          </Button>
        </div>
      </div>

      {/* Detail Body */}
      <div className="flex-1 overflow-y-auto p-5 space-y-5">
        {viewOriginal ? (
          /* Original Raw Email Body */
          <div className="p-4 rounded-xl border border-border/50 bg-secondary/15 font-mono text-xs whitespace-pre-wrap leading-relaxed text-foreground/90 selection:bg-primary/30">
            {email.body_text || email.snippet || "(Empty body)"}
          </div>
        ) : (
          /* Structured AI Intelligence Views */
          <div className="space-y-5">
            {/* 1. Sender Cryptographic Verification Panel */}
            {verification && (
              <div className="p-3.5 rounded-xl border border-border/50 bg-secondary/15 space-y-2">
                <div className="flex items-center justify-between text-xs font-medium">
                  <span className="flex items-center gap-1.5 text-foreground">
                    {verification.is_verified ? (
                      <ShieldCheck className="w-4 h-4 text-emerald-400" />
                    ) : (
                      <ShieldAlert className="w-4 h-4 text-amber-400" />
                    )}
                    <span>Cryptographic Authentication Evidence</span>
                  </span>
                  <span className="text-[11px] font-mono text-muted-foreground">
                    Domain: {email.sender_domain}
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-2 font-mono text-xs">
                  <div className="p-2 rounded bg-card/60 border border-border/40 flex justify-between">
                    <span className="text-muted-foreground">SPF:</span>
                    <span
                      className={`font-semibold uppercase ${
                        verification.spf_status === "pass" ? "text-emerald-400" : "text-amber-400"
                      }`}
                    >
                      {verification.spf_status}
                    </span>
                  </div>
                  <div className="p-2 rounded bg-card/60 border border-border/40 flex justify-between">
                    <span className="text-muted-foreground">DKIM:</span>
                    <span
                      className={`font-semibold uppercase ${
                        verification.dkim_status === "pass" ? "text-emerald-400" : "text-amber-400"
                      }`}
                    >
                      {verification.dkim_status}
                    </span>
                  </div>
                  <div className="p-2 rounded bg-card/60 border border-border/40 flex justify-between">
                    <span className="text-muted-foreground">DMARC:</span>
                    <span
                      className={`font-semibold uppercase ${
                        verification.dmarc_status === "pass" ? "text-emerald-400" : "text-amber-400"
                      }`}
                    >
                      {verification.dmarc_status}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* 2. Executive Summary & Key Points */}
            <div className="p-4 rounded-xl border border-border/50 bg-secondary/20 space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-primary" />
                  <span>Executive Summary</span>
                </h3>
                {analysis?.priority_score !== null && analysis?.priority_score !== undefined && (
                  <span className="text-xs font-mono px-2 py-0.5 rounded bg-primary/15 text-primary border border-primary/30">
                    Priority Score: {analysis.priority_score} / 100
                  </span>
                )}
              </div>

              {oneLineSummary ? (
                <div className="space-y-3">
                  <p className="text-sm font-medium text-foreground leading-relaxed">
                    {oneLineSummary}
                  </p>
                  {keyPoints.length > 0 && (
                    <ul className="space-y-1.5 pt-1 border-t border-border/30">
                      {keyPoints.map((point, idx) => (
                        <li key={idx} className="text-xs text-muted-foreground flex items-start gap-2">
                          <span className="text-primary font-bold">•</span>
                          <span className="leading-relaxed">{point}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              ) : (
                <p className="text-xs text-muted-foreground italic">
                  Not summarized yet. Click "Summarize" above to generate a concise summary.
                </p>
              )}
            </div>

            {/* 3. Action Items & Checklist */}
            <div className="p-4 rounded-xl border border-border/50 bg-secondary/20 space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                  <ListTodo className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Action Items & Tasks</span>
                </h3>
                {analysis?.deadline && (
                  <span className="text-xs font-mono px-2 py-0.5 rounded bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    <span>Due: {analysis.deadline}</span>
                  </span>
                )}
              </div>

              {actionItems?.tasks && actionItems.tasks.length > 0 ? (
                <div className="space-y-2">
                  {actionItems.tasks.map((task, idx) => {
                    const isChecked = Boolean(completedTasks[task])
                    return (
                      <div
                        key={idx}
                        onClick={() => toggleTask(task)}
                        className={`p-2.5 rounded-lg border flex items-center gap-2.5 transition-colors cursor-pointer text-xs ${
                          isChecked
                            ? "bg-emerald-950/15 border-emerald-500/30 text-muted-foreground line-through"
                            : "bg-card/50 border-border/40 text-foreground hover:bg-card/80"
                        }`}
                      >
                        {isChecked ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                        ) : (
                          <Circle className="w-4 h-4 text-muted-foreground shrink-0" />
                        )}
                        <span className="leading-relaxed">{task}</span>
                      </div>
                    )
                  })}
                </div>
              ) : (
                <p className="text-xs text-muted-foreground italic">
                  No action items extracted. Click "Extract Actions" above to scan for tasks and deadlines.
                </p>
              )}

              {/* Extracted Links */}
              {actionItems?.links && actionItems.links.length > 0 && (
                <div className="pt-2 border-t border-border/30 space-y-1.5">
                  <span className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider font-mono">
                    Extracted Links
                  </span>
                  <div className="flex flex-col gap-1">
                    {actionItems.links.map((link, idx) => (
                      <a
                        key={idx}
                        href={link}
                        target="_blank"
                        rel="noreferrer noopener"
                        className="text-xs text-cyan-400 hover:text-cyan-300 hover:underline flex items-center gap-1.5 truncate"
                      >
                        <ExternalLink className="w-3 h-3 shrink-0" />
                        <span className="truncate">{link}</span>
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
