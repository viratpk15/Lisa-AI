import { Clock, CheckCircle2, AlertTriangle, ShieldAlert, Code } from "lucide-react"
import type { ToolResult } from "../../types/tools.types"
import { JsonViewer } from "../common/JsonViewer"

interface ResultPanelProps {
  result: ToolResult | null
}

export function ResultPanel({ result }: ResultPanelProps) {
  if (!result) {
    return (
      <div className="p-6 text-center text-xs text-muted-foreground bg-secondary/10 border border-dashed border-border/40 rounded-xl">
        No execution result available. Configure parameters and click "Execute Tool" above.
      </div>
    )
  }

  const isSuccess = result.status === "SUCCESS"
  const isPending = result.status === "PENDING_APPROVAL"

  return (
    <div className="space-y-3 bg-secondary/15 border border-border/40 rounded-xl p-4">
      {/* Result Status Header */}
      <div className="flex items-center justify-between border-b border-border/40 pb-2.5">
        <div className="flex items-center gap-2">
          {isSuccess ? (
            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
          ) : isPending ? (
            <AlertTriangle className="h-4 w-4 text-amber-400" />
          ) : (
            <ShieldAlert className="h-4 w-4 text-rose-400" />
          )}
          <span
            className={`text-xs font-bold font-mono ${
              isSuccess ? "text-emerald-400" : isPending ? "text-amber-400" : "text-rose-400"
            }`}
          >
            {result.status}
          </span>
        </div>

        <div className="flex items-center gap-3 text-xs font-mono text-muted-foreground">
          <span className="flex items-center gap-1">
            <Clock className="h-3 w-3 text-cyan-400" />
            {result.duration_ms.toFixed(1)} ms
          </span>
          <span className="text-[10px] bg-secondary/50 px-2 py-0.5 rounded border border-border/40">
            ID: {result.execution_id}
          </span>
        </div>
      </div>

      {/* Error Message if Present */}
      {result.error && (
        <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-lg text-xs text-rose-300 space-y-1">
          <div className="font-bold flex items-center gap-1.5">
            <AlertTriangle className="h-3.5 w-3.5 text-rose-400" />
            Execution Error
          </div>
          <p className="font-mono text-[11px] leading-relaxed">{result.error}</p>
        </div>
      )}

      {/* Main Output Content */}
      {result.output !== undefined && result.output !== null && (
        <div className="space-y-1">
          <span className="text-[10px] font-mono text-muted-foreground uppercase flex items-center gap-1">
            <Code className="h-3 w-3 text-cyan-400" />
            Execution Raw Output
          </span>
          {typeof result.output === "object" ? (
            <JsonViewer data={result.output} title="Output Object" defaultExpanded={true} />
          ) : (
            <div className="p-3 bg-[#0D1117] border border-border/40 rounded-lg text-xs font-mono text-[#C9D1D9] whitespace-pre-wrap break-all max-h-62.5 overflow-y-auto scrollbar-thin">
              {String(result.output)}
            </div>
          )}
        </div>
      )}

      {/* Structured Output if Different */}
      {result.structured_output && (
        <div className="space-y-1 pt-1">
          <span className="text-[10px] font-mono text-muted-foreground uppercase">Structured JSON</span>
          <JsonViewer data={result.structured_output} title="Structured Properties" defaultExpanded={false} />
        </div>
      )}
    </div>
  )
}
