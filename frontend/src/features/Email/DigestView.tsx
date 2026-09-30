// frontend/src/features/Email/DigestView.tsx
import React, { useState } from "react"
import {
  PieChart,
  Flame,
  ListTodo,
  ExternalLink,
  Clock,
  Sparkles,
  ArrowRight,
} from "lucide-react"
import { Skeleton } from "@/components/ui/skeleton"
import { EmptyState } from "@/components/common/EmptyState"
import { useEmailDigest } from "./queries"

interface DigestViewProps {
  onSelectEmail?: (id: number) => void
}

export const DigestView: React.FC<DigestViewProps> = ({ onSelectEmail }) => {
  const [period, setPeriod] = useState<"today" | "week">("today")
  const { data: digest, isLoading } = useEmailDigest(period)

  if (isLoading) {
    return (
      <div className="p-6 space-y-6 h-full overflow-y-auto">
        <div className="flex justify-between items-center">
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-8 w-36" />
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-20 rounded-xl" />
          ))}
        </div>
        <Skeleton className="h-48 w-full rounded-xl" />
        <Skeleton className="h-48 w-full rounded-xl" />
      </div>
    )
  }

  if (!digest) {
    return (
      <div className="h-full flex items-center justify-center p-6">
        <EmptyState
          icon={PieChart}
          title="Digest unavailable"
          description="Could not compile email intelligence digest."
        />
      </div>
    )
  }

  const categoryEntries = Object.entries(digest.counts_by_category || {})

  return (
    <div className="h-full flex flex-col overflow-hidden bg-background">
      {/* Digest Header */}
      <div className="p-5 border-b border-border/60 shrink-0 bg-card/20 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-base font-semibold text-foreground tracking-tight flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-primary" />
            <span>Email Intelligence Digest</span>
          </h2>
          <p className="text-xs text-muted-foreground mt-0.5">
            Synthesized across incoming emails for {period === "today" ? "the last 24 hours" : "the last 7 days"}.
          </p>
        </div>

        {/* Period Switcher */}
        <div className="flex items-center gap-1 bg-secondary/40 p-1 rounded-lg border border-border/50">
          <button
            onClick={() => setPeriod("today")}
            className={`px-3 py-1 rounded-md text-xs font-medium transition-all cursor-pointer ${
              period === "today"
                ? "bg-primary text-primary-foreground font-semibold shadow-xs"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Today (24h)
          </button>
          <button
            onClick={() => setPeriod("week")}
            className={`px-3 py-1 rounded-md text-xs font-medium transition-all cursor-pointer ${
              period === "week"
                ? "bg-primary text-primary-foreground font-semibold shadow-xs"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Past Week (7d)
          </button>
        </div>
      </div>

      {/* Digest Scrollable Content */}
      <div className="flex-1 overflow-y-auto p-5 space-y-6">
        {/* 1. Category Distribution Cards */}
        <div className="space-y-3">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
            <PieChart className="w-3.5 h-3.5 text-cyan-400" />
            <span>Category Volume</span>
          </h3>

          {categoryEntries.length > 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
              {categoryEntries.map(([cat, count]) => (
                <div
                  key={cat}
                  className="p-3 rounded-xl border border-border/50 bg-secondary/15 flex items-center justify-between"
                >
                  <span className="text-xs font-medium text-foreground">{cat}</span>
                  <span className="text-sm font-bold font-mono text-primary bg-primary/10 px-2 py-0.5 rounded-md">
                    {count}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-muted-foreground italic">No categorized emails in this timeframe.</p>
          )}
        </div>

        {/* 2. Top 5 Urgent Emails */}
        <div className="space-y-3">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
            <Flame className="w-3.5 h-3.5 text-rose-400" />
            <span>Top Urgent Priorities</span>
          </h3>

          {digest.top_urgent && digest.top_urgent.length > 0 ? (
            <div className="space-y-2.5">
              {digest.top_urgent.map((item) => (
                <div
                  key={item.email_id}
                  onClick={() => onSelectEmail && onSelectEmail(item.email_id)}
                  className="p-3.5 rounded-xl border border-rose-500/30 bg-rose-950/10 hover:bg-rose-950/20 transition-all cursor-pointer flex items-start justify-between gap-3 group"
                >
                  <div className="space-y-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono font-bold text-rose-400 bg-rose-500/15 px-1.5 py-0.2 rounded">
                        P{item.priority_score}
                      </span>
                      <span className="text-xs font-semibold text-foreground truncate">
                        {item.subject}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground line-clamp-1 leading-relaxed">
                      {item.one_line_summary || "No summary generated"}
                    </p>
                    <div className="text-[10px] text-muted-foreground font-mono flex items-center gap-2 pt-0.5">
                      <span>{item.sender}</span>
                      <span>•</span>
                      <span>{item.category}</span>
                    </div>
                  </div>

                  <ArrowRight className="w-4 h-4 text-muted-foreground group-hover:text-foreground group-hover:translate-x-0.5 transition-all shrink-0 mt-1" />
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-muted-foreground italic">No urgent items detected in this timeframe.</p>
          )}
        </div>

        {/* 3. Aggregated Action Items & Deadlines */}
        <div className="space-y-3">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
            <ListTodo className="w-3.5 h-3.5 text-emerald-400" />
            <span>Aggregated Action Items</span>
          </h3>

          {digest.action_items && digest.action_items.length > 0 ? (
            <div className="space-y-3">
              {digest.action_items.map((action, idx) => (
                <div key={idx} className="p-3.5 rounded-xl border border-border/50 bg-secondary/15 space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-foreground truncate max-w-sm">
                      {action.subject}
                    </span>
                    {action.deadline && (
                      <span className="text-[11px] font-mono text-cyan-300 bg-cyan-500/10 border border-cyan-500/20 px-2 py-0.5 rounded flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        <span>Due: {action.deadline}</span>
                      </span>
                    )}
                  </div>

                  <ul className="space-y-1">
                    {action.tasks.map((task, tIdx) => (
                      <li key={tIdx} className="text-xs text-muted-foreground flex items-start gap-2">
                        <span className="text-emerald-400 font-bold">•</span>
                        <span>{task}</span>
                      </li>
                    ))}
                  </ul>

                  {action.links && action.links.length > 0 && (
                    <div className="flex flex-wrap gap-2 pt-1 border-t border-border/30">
                      {action.links.map((link, lIdx) => (
                        <a
                          key={lIdx}
                          href={link}
                          target="_blank"
                          rel="noreferrer noopener"
                          className="text-[11px] text-cyan-400 hover:text-cyan-300 hover:underline flex items-center gap-1"
                        >
                          <ExternalLink className="w-3 h-3" />
                          <span className="truncate max-w-xs">{link}</span>
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-muted-foreground italic">No action items pending in this timeframe.</p>
          )}
        </div>
      </div>
    </div>
  )
}
