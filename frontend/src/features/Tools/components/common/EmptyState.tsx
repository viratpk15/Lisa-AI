import { Wrench, RefreshCw } from "lucide-react"

interface EmptyStateProps {
  title?: string
  description?: string
  onReset?: () => void
}

export function EmptyState({
  title = "No Tools Found",
  description = "No registered tools matched your active search query or filter criteria.",
  onReset,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center bg-secondary/10 border border-border/40 rounded-xl">
      <div className="p-3 bg-secondary/40 rounded-full text-cyan-400 border border-border/50 mb-3">
        <Wrench className="h-6 w-6" />
      </div>
      <h3 className="text-sm font-bold text-foreground">{title}</h3>
      <p className="text-xs text-muted-foreground max-w-sm mt-1 leading-relaxed">{description}</p>
      {onReset && (
        <button
          onClick={onReset}
          className="mt-4 inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-400 border border-cyan-500/40 rounded-lg cursor-pointer transition-all"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          Reset Filters
        </button>
      )}
    </div>
  )
}
