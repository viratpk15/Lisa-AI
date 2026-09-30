/**
 * Lisa AIOS — Application Tracker Tab
 * Uses real backend ApplicationTrackItem field names:
 *   job_id, title, company, location, apply_url, status, saved_at, applied_at, notes
 * Status transitions are ONLY user-initiated.
 */

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import {
  Bookmark,
  Send,
  MessageSquare,
  XCircle,
  Trophy,
  ExternalLink,
  Trash2,
  ChevronDown,
  Loader2,
  ClipboardList,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  useTrackedApplicationsQuery,
  useUpdateApplicationStatusMutation,
  useDeleteTrackedJobMutation,
} from "../queries"
import type { ApplicationTrackItem, ApplicationStatusEnum } from "../types"
import { cn } from "@/lib/utils"

const STATUS_CONFIG: Record<
  ApplicationStatusEnum,
  { label: string; icon: typeof Bookmark; colorClass: string; bgClass: string; borderClass: string }
> = {
  saved: { label: "Saved", icon: Bookmark, colorClass: "text-slate-600", bgClass: "bg-slate-500/10", borderClass: "border-slate-500/20" },
  applied: { label: "Applied", icon: Send, colorClass: "text-blue-600", bgClass: "bg-blue-500/10", borderClass: "border-blue-500/20" },
  interview: { label: "Interview", icon: MessageSquare, colorClass: "text-amber-600", bgClass: "bg-amber-500/10", borderClass: "border-amber-500/20" },
  rejected: { label: "Rejected", icon: XCircle, colorClass: "text-red-600", bgClass: "bg-red-500/10", borderClass: "border-red-500/20" },
  offer: { label: "Offer", icon: Trophy, colorClass: "text-emerald-600", bgClass: "bg-emerald-500/10", borderClass: "border-emerald-500/20" },
}

const STATUS_ORDER: ApplicationStatusEnum[] = ["saved", "applied", "interview", "rejected", "offer"]

function ApplicationCard({ item }: { item: ApplicationTrackItem }) {
  const [showStatusMenu, setShowStatusMenu] = useState(false)
  const updateMutation = useUpdateApplicationStatusMutation()
  const deleteMutation = useDeleteTrackedJobMutation()

  const config = STATUS_CONFIG[item.status]
  const Icon = config.icon

  const handleStatusChange = async (newStatus: ApplicationStatusEnum) => {
    await updateMutation.mutateAsync({ jobId: item.job_id, req: { status: newStatus } })
    setShowStatusMenu(false)
  }

  const handleDelete = async () => {
    if (window.confirm(`Remove "${item.title}" at ${item.company} from tracker?`)) {
      await deleteMutation.mutateAsync(item.job_id)
    }
  }

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.97 }}
      className="group rounded-xl border border-border/70 bg-card p-4 space-y-3 hover:shadow-sm transition-shadow"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0 space-y-0.5">
          {/* Backend field: title (not job_title) */}
          <h4 className="text-sm font-semibold text-foreground line-clamp-1">{item.title}</h4>
          <p className="text-xs text-muted-foreground">{item.company} · {item.location}</p>
          {item.saved_at && (
            <p className="text-[11px] text-muted-foreground/60">Saved: {item.saved_at}</p>
          )}
        </div>

        {/* Status Badge with Dropdown */}
        <div className="relative shrink-0">
          <button
            onClick={() => setShowStatusMenu((prev) => !prev)}
            className={cn(
              "flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold border transition-colors",
              config.bgClass, config.borderClass, config.colorClass, "hover:opacity-80"
            )}
          >
            <Icon className="h-3.5 w-3.5" />
            {config.label}
            <ChevronDown className="h-3 w-3 ml-0.5" />
          </button>

          <AnimatePresence>
            {showStatusMenu && (
              <motion.div
                initial={{ opacity: 0, y: -4, scale: 0.97 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -4, scale: 0.97 }}
                className="absolute right-0 top-full mt-1 z-50 rounded-xl border border-border bg-card shadow-xl p-1.5 min-w-35"
              >
                {STATUS_ORDER.map((status) => {
                  const cfg = STATUS_CONFIG[status]
                  const StatusIcon = cfg.icon
                  return (
                    <button
                      key={status}
                      disabled={status === item.status || updateMutation.isPending}
                      onClick={() => handleStatusChange(status)}
                      className={cn(
                        "w-full flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors",
                        status === item.status
                          ? cn(cfg.bgClass, cfg.colorClass, "opacity-70 cursor-not-allowed")
                          : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                      )}
                    >
                      <StatusIcon className="h-3.5 w-3.5" />
                      {cfg.label}
                    </button>
                  )
                })}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {item.notes && (
        <p className="text-xs text-muted-foreground italic line-clamp-1 bg-muted/30 rounded px-2 py-1">
          "{item.notes}"
        </p>
      )}

      <div className="flex items-center gap-2">
        <Button asChild variant="outline" size="sm" className="flex-1 h-8 text-xs gap-1">
          <a href={item.apply_url} target="_blank" rel="noopener noreferrer">
            <ExternalLink className="h-3.5 w-3.5" />
            Open Posting
          </a>
        </Button>
        <button
          onClick={handleDelete}
          disabled={deleteMutation.isPending}
          className="p-1.5 rounded-lg border border-border text-muted-foreground hover:text-destructive hover:border-destructive/40 transition-colors"
          title="Remove from tracker"
        >
          {deleteMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
        </button>
      </div>
    </motion.div>
  )
}

export function ApplicationTrackerTab() {
  const { data: applications = [], isLoading, isError } = useTrackedApplicationsQuery()

  const grouped = STATUS_ORDER.reduce(
    (acc, status) => {
      acc[status] = applications.filter((a) => a.status === status)
      return acc
    },
    {} as Record<ApplicationStatusEnum, ApplicationTrackItem[]>
  )

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16 gap-3">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        <span className="text-sm text-muted-foreground">Loading application tracker...</span>
      </div>
    )
  }

  if (isError) {
    return <div className="text-center py-12 text-sm text-destructive">Failed to load tracker.</div>
  }

  if (applications.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-4 text-center">
        <div className="p-4 rounded-full bg-secondary text-muted-foreground">
          <ClipboardList className="h-8 w-8" />
        </div>
        <div>
          <h3 className="font-semibold text-foreground">No Applications Tracked</h3>
          <p className="text-sm text-muted-foreground mt-1 max-w-xs">
            Save jobs from the search results to start tracking your applications here.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {STATUS_ORDER.map((status) => {
        const items = grouped[status]
        if (items.length === 0) return null
        const config = STATUS_CONFIG[status]
        const Icon = config.icon
        return (
          <div key={status} className="space-y-3">
            <div className="flex items-center gap-2">
              <div className={cn("p-1.5 rounded-lg border", config.bgClass, config.borderClass, config.colorClass)}>
                <Icon className="h-4 w-4" />
              </div>
              <h3 className={cn("text-sm font-semibold", config.colorClass)}>{config.label}</h3>
              <span className="text-xs font-mono text-muted-foreground bg-muted rounded-full px-2 py-0.5">{items.length}</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <AnimatePresence mode="popLayout">
                {items.map((item) => (
                  <ApplicationCard key={item.job_id} item={item} />
                ))}
              </AnimatePresence>
            </div>
          </div>
        )
      })}
    </div>
  )
}
