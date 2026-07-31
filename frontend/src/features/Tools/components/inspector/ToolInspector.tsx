import { Wrench, Clock, ShieldCheck, FileCode, CheckCircle2, X } from "lucide-react"
import { useToolConsoleStore } from "../../store/useToolConsoleStore"
import { useToolDetailsQuery } from "../../services/toolApi"
import { StatusChip } from "../common/StatusChip"
import { JsonViewer } from "../common/JsonViewer"
import { LoadingSkeleton } from "../common/LoadingSkeleton"
import { ErrorState } from "../common/ErrorState"

export function ToolInspector() {
  const selectedToolName = useToolConsoleStore((s) => s.selectedToolName)
  const setSelectedToolName = useToolConsoleStore((s) => s.setSelectedToolName)

  const { data: details, isLoading, isError, refetch } = useToolDetailsQuery(selectedToolName)

  if (!selectedToolName) {
    return (
      <div className="flex flex-col items-center justify-center p-8 h-full text-center text-muted-foreground border border-dashed border-border/40 rounded-xl bg-secondary/10">
        <Wrench className="h-8 w-8 text-muted-foreground/60 mb-2" />
        <h4 className="text-xs font-bold text-foreground">No Tool Selected</h4>
        <p className="text-[11px] text-muted-foreground max-w-xs mt-1">
          Select a registered tool from the explorer on the left to inspect its schema, capabilities, and metadata.
        </p>
      </div>
    )
  }

  if (isLoading) return <LoadingSkeleton count={3} />
  if (isError || !details) return <ErrorState message={`Failed to load schema for '${selectedToolName}'.`} onRetry={refetch} />

  const { metadata, schema } = details

  return (
    <div className="space-y-4 bg-secondary/10 border border-border/40 rounded-xl p-4">
      {/* Header */}
      <div className="flex items-start justify-between border-b border-border/40 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 rounded-lg">
            <Wrench className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-foreground">{metadata.display_name || metadata.name}</h3>
            <span className="text-[11px] font-mono text-muted-foreground">v{metadata.version} • {metadata.author}</span>
          </div>
        </div>
        <button
          onClick={() => setSelectedToolName(null)}
          className="p-1 text-muted-foreground hover:text-foreground cursor-pointer rounded"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Description */}
      <p className="text-xs text-muted-foreground leading-relaxed">
        {metadata.description}
      </p>

      {/* Metadata Capabilities Grid */}
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="p-2.5 bg-secondary/30 border border-border/40 rounded-lg space-y-1">
          <span className="text-[10px] font-mono text-muted-foreground uppercase">Category</span>
          <div className="font-semibold text-foreground capitalize">{metadata.category}</div>
        </div>

        <div className="p-2.5 bg-secondary/30 border border-border/40 rounded-lg space-y-1">
          <span className="text-[10px] font-mono text-muted-foreground uppercase">Permission Level</span>
          <div><StatusChip type="permission" value={metadata.permission_level} /></div>
        </div>

        <div className="p-2.5 bg-secondary/30 border border-border/40 rounded-lg space-y-1">
          <span className="text-[10px] font-mono text-muted-foreground uppercase">Timeout</span>
          <div className="font-mono text-foreground flex items-center gap-1">
            <Clock className="h-3 w-3 text-cyan-400" />
            {metadata.timeout_seconds}s
          </div>
        </div>

        <div className="p-2.5 bg-secondary/30 border border-border/40 rounded-lg space-y-1">
          <span className="text-[10px] font-mono text-muted-foreground uppercase">Approval Req.</span>
          <div className="font-semibold text-foreground flex items-center gap-1">
            {metadata.requires_approval ? (
              <StatusChip type="approval" value={true} />
            ) : (
              <span className="text-[11px] text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="h-3 w-3" /> Standard
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Tags */}
      {metadata.tags && metadata.tags.length > 0 && (
        <div className="space-y-1">
          <span className="text-[10px] font-mono text-muted-foreground uppercase">Tags</span>
          <div className="flex flex-wrap gap-1">
            {metadata.tags.map((tag) => (
              <span key={tag} className="px-2 py-0.5 text-[10px] font-mono bg-secondary/50 border border-border/40 rounded text-muted-foreground">
                #{tag}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* OpenAPI Parameter JSON Schema */}
      <div className="space-y-1.5 pt-2">
        <span className="text-[11px] font-mono font-semibold text-foreground flex items-center gap-1">
          <FileCode className="h-3.5 w-3.5 text-cyan-400" />
          JSON Schema Contract
        </span>
        <JsonViewer data={schema} title="Parameter Schema" defaultExpanded={true} />
      </div>

      {/* Examples if present */}
      {metadata.examples && metadata.examples.length > 0 && (
        <div className="space-y-1.5 pt-2">
          <span className="text-[11px] font-mono font-semibold text-foreground flex items-center gap-1">
            <ShieldCheck className="h-3.5 w-3.5 text-violet-400" />
            Example Payload Invocations
          </span>
          <JsonViewer data={metadata.examples} title="Payload Examples" defaultExpanded={false} />
        </div>
      )}
    </div>
  )
}
