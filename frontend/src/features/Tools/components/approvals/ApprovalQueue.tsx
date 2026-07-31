import { useState } from "react"
import { AlertTriangle, Check, X, ShieldAlert } from "lucide-react"
import { useToolConsoleStore } from "../../store/useToolConsoleStore"
import { executeTool } from "../../services/toolApi"
import { JsonViewer } from "../common/JsonViewer"
import type { PendingApprovalItem } from "../../types/tools.types"

export function ApprovalQueue() {
  const pendingApprovals = useToolConsoleStore((s) => s.pendingApprovals)
  const removePendingApproval = useToolConsoleStore((s) => s.removePendingApproval)
  const addExecutionHistory = useToolConsoleStore((s) => s.addExecutionHistory)
  const addConsoleLog = useToolConsoleStore((s) => s.addConsoleLog)
  const setLatestResult = useToolConsoleStore((s) => s.setLatestResult)

  const [processingId, setProcessingId] = useState<string | null>(null)

  const handleApprove = async (item: PendingApprovalItem) => {
    setProcessingId(item.execution_id)
    addConsoleLog("info", `Approving execution for tool '${item.tool_name}'...`)

    try {
      const res = await executeTool(item.tool_name, item.arguments, { is_approved: true })
      setLatestResult(res)
      addExecutionHistory(res)
      removePendingApproval(item.execution_id)

      if (res.status === "SUCCESS") {
        addConsoleLog("success", `Execution approved & completed for '${item.tool_name}' in ${res.duration_ms.toFixed(1)}ms.`)
      } else {
        addConsoleLog("stderr", `Approved execution failed: ${res.error}`)
      }
    } catch (err: any) {
      addConsoleLog("stderr", `Approval failed: ${err.message}`)
    } finally {
      setProcessingId(null)
    }
  }

  const handleReject = (item: PendingApprovalItem) => {
    removePendingApproval(item.execution_id)
    addConsoleLog("warning", `Execution rejected by user for tool '${item.tool_name}'.`)
  }

  return (
    <div className="space-y-3 bg-secondary/15 border border-border/40 rounded-xl p-4">
      <div className="flex items-center justify-between border-b border-border/40 pb-3">
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-amber-400" />
          <h3 className="text-xs font-bold text-foreground">Human-in-the-Loop Approval Queue ({pendingApprovals.length})</h3>
        </div>
      </div>

      {pendingApprovals.length === 0 ? (
        <div className="p-8 text-center text-xs text-muted-foreground italic bg-secondary/10 rounded-lg border border-dashed border-border/40">
          No pending approvals requiring user intervention.
        </div>
      ) : (
        <div className="space-y-3">
          {pendingApprovals.map((item) => (
            <div
              key={item.execution_id}
              className="p-4 bg-amber-500/5 border border-amber-500/30 rounded-xl space-y-3"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                  <ShieldAlert className="h-5 w-5 text-amber-400 shrink-0" />
                  <div>
                    <h4 className="text-xs font-bold text-foreground font-mono">{item.tool_name}</h4>
                    <span className="text-[10px] text-muted-foreground font-mono">ID: {item.execution_id}</span>
                  </div>
                </div>
                <span className="px-2 py-0.5 text-[10px] font-mono font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/40 rounded">
                  Requires Approval
                </span>
              </div>

              <div className="space-y-1">
                <span className="text-[10px] font-mono text-muted-foreground uppercase">Execution Payload Parameters</span>
                <JsonViewer data={item.arguments} title="Invocation Parameters" defaultExpanded={true} />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-amber-500/20">
                <button
                  onClick={() => handleReject(item)}
                  disabled={processingId === item.execution_id}
                  className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-semibold bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/40 rounded-lg cursor-pointer transition-all disabled:opacity-50"
                >
                  <X className="h-3.5 w-3.5" />
                  Reject Execution
                </button>

                <button
                  onClick={() => handleApprove(item)}
                  disabled={processingId === item.execution_id}
                  className="inline-flex items-center gap-1 px-4 py-1.5 text-xs font-bold bg-emerald-500 hover:bg-emerald-400 text-black rounded-lg cursor-pointer transition-all shadow-md disabled:opacity-50"
                >
                  <Check className="h-3.5 w-3.5" />
                  {processingId === item.execution_id ? "Approving..." : "Approve & Execute"}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
