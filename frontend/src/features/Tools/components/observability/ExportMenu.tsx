import { useState } from "react"
import { FileJson, FileSpreadsheet, Copy, Check } from "lucide-react"
import type { ToolResult } from "../../types/tools.types"

interface ExportMenuProps {
  history: ToolResult[]
}

export function ExportMenu({ history }: ExportMenuProps) {
  const [copied, setCopied] = useState(false)

  const handleExportJson = () => {
    const jsonStr = JSON.stringify(history, null, 2)
    const blob = new Blob([jsonStr], { type: "application/json" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `jarvis_observability_trace_${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  const handleExportCsv = () => {
    if (history.length === 0) return
    const headers = ["execution_id", "tool_name", "status", "duration_ms", "started_at"]
    const rows = history.map((h) => [
      h.execution_id,
      h.tool_name,
      h.status,
      h.duration_ms,
      h.started_at,
    ])

    const csvContent = [headers.join(","), ...rows.map((r) => r.join(","))].join("\n")
    const blob = new Blob([csvContent], { type: "text/csv" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `jarvis_observability_metrics_${Date.now()}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  const handleCopyTrace = () => {
    navigator.clipboard.writeText(JSON.stringify(history, null, 2))
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      <button
        onClick={handleExportJson}
        disabled={history.length === 0}
        className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-secondary/30 hover:bg-secondary/60 border border-border/40 text-foreground rounded-lg cursor-pointer transition-all disabled:opacity-30"
      >
        <FileJson className="h-3.5 w-3.5 text-cyan-400" />
        Export JSON
      </button>

      <button
        onClick={handleExportCsv}
        disabled={history.length === 0}
        className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-secondary/30 hover:bg-secondary/60 border border-border/40 text-foreground rounded-lg cursor-pointer transition-all disabled:opacity-30"
      >
        <FileSpreadsheet className="h-3.5 w-3.5 text-emerald-400" />
        Export CSV
      </button>

      <button
        onClick={handleCopyTrace}
        disabled={history.length === 0}
        className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-secondary/30 hover:bg-secondary/60 border border-border/40 text-foreground rounded-lg cursor-pointer transition-all disabled:opacity-30"
      >
        {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5 text-violet-400" />}
        {copied ? "Trace Copied" : "Copy Trace"}
      </button>
    </div>
  )
}
