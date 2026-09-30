import React, { useMemo } from "react"
import { RefreshCw, Inbox, AlertCircle, Mail } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { EmptyState } from "@/components/common/EmptyState"
import { SenderAuthBadge } from "./SenderAuthBadge"
import type { EmailListItem } from "./api"

interface InboxListProps {
  emails: EmailListItem[]
  selectedId: number | null
  onSelect: (id: number) => void
  isLoading: boolean
  isSyncing: boolean
  onSync: () => void
  selectedCategory: string | null
  onSelectCategory: (cat: string | null) => void
  isConnected?: boolean
  connectedEmail?: string
  isConnectingGmail?: boolean
  onConnectGmail?: () => void
}

function getCategoryColor(category: string | null): string {
  switch (category) {
    case "URGENT":
      return "bg-rose-500/15 text-rose-400 border-rose-500/30"
    case "PLACEMENT":
    case "INTERNSHIP":
      return "bg-cyan-500/15 text-cyan-300 border-cyan-500/30"
    case "FINANCE":
      return "bg-emerald-500/15 text-emerald-400 border-emerald-500/30"
    case "COLLEGE":
      return "bg-purple-500/15 text-purple-400 border-purple-500/30"
    case "BOOKING":
    case "TRAVEL":
      return "bg-amber-500/15 text-amber-400 border-amber-500/30"
    case "SPAM":
    case "SCAM":
      return "bg-red-900/20 text-red-400 border-red-800/40"
    default:
      return "bg-secondary/60 text-muted-foreground border-border/50"
  }
}

export const InboxList: React.FC<InboxListProps> = ({
  emails,
  selectedId,
  onSelect,
  isLoading,
  isSyncing,
  onSync,
  selectedCategory,
  onSelectCategory,
  isConnected = false,
  connectedEmail,
  isConnectingGmail = false,
  onConnectGmail,
}) => {
  // Sort emails priority-grouped: URGENT / highest priority score first
  const sortedEmails = useMemo(() => {
    return [...emails].sort((a, b) => {
      // Urgent category always comes first
      const aIsUrgent = a.category === "URGENT" ? 1 : 0
      const bIsUrgent = b.category === "URGENT" ? 1 : 0
      if (aIsUrgent !== bIsUrgent) return bIsUrgent - aIsUrgent

      // Then sort by priority_score descending
      const aScore = a.priority_score ?? 0
      const bScore = b.priority_score ?? 0
      if (aScore !== bScore) return bScore - aScore

      // Otherwise sort by received_at descending
      return new Date(b.received_at).getTime() - new Date(a.received_at).getTime()
    })
  }, [emails])

  const categories = useMemo(() => {
    const set = new Set<string>()
    emails.forEach((e) => {
      if (e.category) set.add(e.category)
    })
    return Array.from(set)
  }, [emails])

  return (
    <div className="flex flex-col h-full bg-card/40">
      {/* Header with Connection Status & Sync Action */}
      <div className="p-3 border-b border-border/60 flex items-center justify-between gap-2 shrink-0">
        <div>
          <h2 className="text-sm font-semibold tracking-tight text-foreground flex items-center gap-1.5">
            <Inbox className="w-4 h-4 text-primary" />
            <span>Inbox</span>
            <span className="text-[11px] font-mono text-muted-foreground bg-secondary/80 px-1.5 py-0.2 rounded-md">
              {emails.length}
            </span>
          </h2>
        </div>

        <div className="flex items-center gap-1.5">
          {isConnected ? (
            <div className="flex items-center gap-1.5">
              <span
                className="hidden sm:inline-flex items-center gap-1 text-[10px] text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full"
                title={connectedEmail ? `Connected: ${connectedEmail}` : "Gmail Connected"}
              >
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                <span className="truncate max-w-22.5">{connectedEmail || "Gmail"}</span>
              </span>
              <Button
                onClick={onSync}
                disabled={isSyncing}
                variant="outline"
                size="sm"
                className="h-7 text-xs gap-1.5 cursor-pointer font-medium"
              >
                <RefreshCw className={`w-3 h-3 ${isSyncing ? "animate-spin text-primary" : ""}`} />
                <span>{isSyncing ? "Syncing..." : "Sync"}</span>
              </Button>
            </div>
          ) : (
            <Button
              onClick={onConnectGmail}
              disabled={isConnectingGmail}
              size="sm"
              className="h-7 text-xs gap-1.5 cursor-pointer font-medium bg-linear-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white shadow-xs"
            >
              <Mail className="w-3.5 h-3.5" />
              <span>{isConnectingGmail ? "Connecting..." : "Connect Gmail"}</span>
            </Button>
          )}
        </div>
      </div>

      {/* Category Filter Bar */}
      {categories.length > 0 && (
        <div className="px-3 py-2 border-b border-border/40 flex items-center gap-1.5 overflow-x-auto scrollbar-none shrink-0 text-xs">
          <button
            onClick={() => onSelectCategory(null)}
            className={`px-2 py-0.5 rounded-md text-[11px] font-medium transition-colors cursor-pointer ${
              selectedCategory === null
                ? "bg-primary text-primary-foreground font-semibold"
                : "bg-secondary/40 text-muted-foreground hover:text-foreground"
            }`}
          >
            All
          </button>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => onSelectCategory(cat === selectedCategory ? null : cat)}
              className={`px-2 py-0.5 rounded-md text-[11px] font-medium transition-colors cursor-pointer ${
                cat === selectedCategory
                  ? "bg-primary text-primary-foreground font-semibold"
                  : "bg-secondary/40 text-muted-foreground hover:text-foreground"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      )}

      {/* List Content */}
      <div className="flex-1 overflow-y-auto divide-y divide-border/30">
        {isLoading && (
          <div className="p-4 space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="space-y-2 p-3 rounded-lg border border-border/30 bg-secondary/10">
                <div className="flex justify-between items-center">
                  <Skeleton className="h-3.5 w-24" />
                  <Skeleton className="h-3 w-14" />
                </div>
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-3 w-full" />
              </div>
            ))}
          </div>
        )}

        {!isLoading && sortedEmails.length === 0 && (
          <div className="p-6">
            {!isConnected ? (
              <EmptyState
                icon={Mail}
                title="Gmail Not Connected"
                description="Connect your Gmail account to view your inbox, analyze threads, and extract action items directly inside Lisa."
                actionText={isConnectingGmail ? "Redirecting to Google..." : "Connect Gmail Account"}
                onAction={onConnectGmail}
              />
            ) : (
              <EmptyState
                icon={Inbox}
                title="No emails found"
                description={
                  selectedCategory
                    ? `No emails matching category '${selectedCategory}'`
                    : "Your inbox is clear. Sync your Gmail account to ingest recent messages."
                }
                actionText={isSyncing ? "Syncing..." : "Sync Gmail Now"}
                onAction={onSync}
              />
            )}
          </div>
        )}

        {!isLoading &&
          sortedEmails.map((email) => {
            const isSelected = email.id === selectedId
            const isUrgent = email.category === "URGENT"

            return (
              <div
                key={email.id}
                onClick={() => onSelect(email.id)}
                className={`p-3 text-left transition-colors cursor-pointer border-l-2 ${
                  isSelected
                    ? "bg-secondary/50 border-primary"
                    : isUrgent
                    ? "bg-rose-950/10 border-rose-500/70 hover:bg-secondary/30"
                    : "border-transparent hover:bg-secondary/20"
                }`}
              >
                {/* Row 1: Sender & Time & Verification */}
                <div className="flex items-center justify-between gap-1 mb-1">
                  <span className="text-xs font-semibold text-foreground truncate max-w-45">
                    {email.sender}
                  </span>
                  <div className="flex items-center gap-1.5 shrink-0">
                    <SenderAuthBadge isVerified={email.is_verified} />
                    <span className="text-[10px] text-muted-foreground font-mono">
                      {new Date(email.received_at).toLocaleDateString(undefined, {
                        month: "short",
                        day: "numeric",
                      })}
                    </span>
                  </div>
                </div>

                {/* Row 2: Subject */}
                <h4 className="text-xs font-medium text-foreground/90 truncate mb-1">
                  {email.subject || "(No Subject)"}
                </h4>

                {/* Row 3: 1-Line Summary or Snippet */}
                <p className="text-[11px] text-muted-foreground line-clamp-2 leading-relaxed mb-2">
                  {email.one_line_summary || email.snippet}
                </p>

                {/* Row 4: Chips (Category, Priority, Deadline) */}
                <div className="flex flex-wrap items-center gap-1.5">
                  {email.category && (
                    <span
                      className={`inline-flex items-center px-1.5 py-0.2 rounded text-[10px] font-semibold border ${getCategoryColor(
                        email.category
                      )}`}
                    >
                      {email.category}
                    </span>
                  )}
                  {email.priority_score !== null && email.priority_score !== undefined && (
                    <span
                      className={`text-[10px] font-mono px-1 py-0.2 rounded ${
                        email.priority_score >= 80
                          ? "text-rose-400 bg-rose-500/10"
                          : email.priority_score >= 50
                          ? "text-amber-400 bg-amber-500/10"
                          : "text-muted-foreground bg-secondary/50"
                      }`}
                    >
                      P{email.priority_score}
                    </span>
                  )}
                  {email.deadline && (
                    <span className="text-[10px] font-mono text-cyan-300 bg-cyan-500/10 border border-cyan-500/20 px-1 py-0.2 rounded flex items-center gap-0.5">
                      <AlertCircle className="w-2.5 h-2.5" />
                      <span>{email.deadline}</span>
                    </span>
                  )}
                </div>
              </div>
            )
          })}
      </div>
    </div>
  )
}
