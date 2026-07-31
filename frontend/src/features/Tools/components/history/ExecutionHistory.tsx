import { History, Play, Trash2, Copy, CheckCircle2, AlertTriangle, ShieldAlert } from "lucide-react"
import { useToolConsoleStore } from "../../store/useToolConsoleStore"
import type { ToolResult } from "../../types/tools.types"

export function ExecutionHistory() {
  const executionHistory = useToolConsoleStore((s) => s.executionHistory)
  const clearExecutionHistory = useToolConsoleStore((s) => s.clearExecutionHistory)
  const setSelectedToolName = useToolConsoleStore((s) => s.setSelectedToolName)
  const setFormParameters = useToolConsoleStore((s) => s.setFormParameters)
  const setActiveTab = useToolConsoleStore((s) => s.setActiveTab)
  const setLatestResult = useToolConsoleStore((s) => s.setLatestResult)

  const handleReplay = (item: ToolResult) => {
    setSelectedToolName(item.tool_name)
    const params = item.metadata?.execution_args || item.structured_output || {}
    setFormParameters(params)
    setLatestResult(item)
    setActiveTab("runner")
  }

  const handleCopyParams = (item: ToolResult) => {
    const params = item.metadata?.execution_args || item.structured_output || {}
    navigator.clipboard.writeText(JSON.stringify(params, null, 2))
  }

  return (
    <div className="space-y-3 bg-secondary/15 border border-border/40 rounded-xl p-4">
      <div className="flex items-center justify-between border-b border-border/40 pb-3">
        <div className="flex items-center gap-2">
          <History className="h-4 w-4 text-cyan-400" />
          <h3 className="text-xs font-bold text-foreground">Session Execution History ({executionHistory.length})</h3>
        </div>

        {executionHistory.length > 0 && (
          <button
            onClick={clearExecutionHistory}
            className="inline-flex items-center gap-1 px-2.5 py-1 text-[11px] text-muted-foreground hover:text-rose-400 bg-secondary/30 hover:bg-rose-500/10 border border-border/40 rounded cursor-pointer transition-all"
          >
            <Trash2 className="h-3 w-3" />
            Clear History
          </button>
        )}
      </div>

      {executionHistory.length === 0 ? (
        <div className="p-8 text-center text-xs text-muted-foreground italic bg-secondary/10 rounded-lg border border-dashed border-border/40">
          No tool executions recorded in this session yet.
        </div>
      ) : (
        <div className="space-y-2 max-h-96 overflow-y-auto scrollbar-thin">
          {executionHistory.map((item, idx) => {
            const isSuccess = item.status === "SUCCESS"
            return (
              <div
                key={`${item.execution_id}_${idx}`}
                className="p-3 bg-secondary/20 hover:bg-secondary/40 border border-border/40 rounded-lg flex items-center justify-between text-xs transition-all"
              >
                <div className="flex items-center gap-3">
                  {isSuccess ? (
                    <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
                  ) : item.status === "PENDING_APPROVAL" ? (
                    <AlertTriangle className="h-4 w-4 text-amber-400 shrink-0" />
                  ) : (
                    <ShieldAlert className="h-4 w-4 text-rose-400 shrink-0" />
                  )}

                  <div>
                    <div className="font-bold text-foreground font-mono flex items-center gap-2">
                      <span>{item.tool_name}</span>
                      <span className="text-[10px] text-muted-foreground font-normal">
                        ({item.duration_ms.toFixed(1)}ms)
                      </span>
                    </div>
                    <span className="text-[10px] font-mono text-muted-foreground">ID: {item.execution_id}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleCopyParams(item)}
                    className="p-1 text-muted-foreground hover:text-foreground bg-secondary/40 hover:bg-secondary border border-border/40 rounded cursor-pointer transition-all"
                    title="Copy Parameters JSON"
                  >
                    <Copy className="h-3.5 w-3.5" />
                  </button>

                  <button
                    onClick={() => handleReplay(item)}
                    className="inline-flex items-center gap-1 px-2.5 py-1 text-[11px] font-bold bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 rounded cursor-pointer transition-all"
                    title="Replay Execution"
                  >
                    <Play className="h-3 w-3 fill-current" />
                    Replay
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
