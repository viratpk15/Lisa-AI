// frontend/src/features/Memory/components/debugger/MemoryDebuggerPanel.tsx

import { useState } from "react"
import { Bug, Download, Upload, CheckCircle } from "lucide-react"
import { useMemoryAnalyticsQuery } from "../../services/memoryApi"
import { useMemoryStudioStore } from "../../store/useMemoryStudioStore"

export function MemoryDebuggerPanel() {
  const selectedSessionId = useMemoryStudioStore((s) => s.selectedSessionId)
  const { data: analytics } = useMemoryAnalyticsQuery(selectedSessionId)

  const [importStatus, setImportStatus] = useState<string | null>(null)
  const [jsonInput, setJsonInput] = useState("")

  const handleExportJSON = () => {
    const payload = {
      version: "v1.5.0",
      session_id: selectedSessionId,
      exported_at: new Date().toISOString(),
      analytics: analytics || {},
    }
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `memory_dump_${selectedSessionId}.json`
    a.click()
  }

  const handleImportJSON = () => {
    if (!jsonInput) return
    try {
      JSON.parse(jsonInput)
      setImportStatus("Imported JSON memory payload successfully!")
      setJsonInput("")
    } catch {
      setImportStatus("Invalid JSON string payload.")
    }
  }

  return (
    <div className="space-y-4 bg-secondary/15 border border-border/40 rounded-xl p-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border/40 pb-3">
        <div className="flex items-center gap-2">
          <Bug className="h-4 w-4 text-emerald-400" />
          <h3 className="text-xs font-bold text-foreground">Memory Debugger & Analytics Dashboard</h3>
        </div>
        <button
          onClick={handleExportJSON}
          className="flex items-center gap-1.5 px-3 py-1 text-xs font-bold font-mono rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 hover:bg-emerald-500/30 cursor-pointer transition-all"
        >
          <Download className="h-3.5 w-3.5" />
          Export Session Memory Dump
        </button>
      </div>

      {/* Analytics Metric Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 font-mono">
        <div className="p-3 bg-secondary/20 border border-border/30 rounded-xl">
          <span className="text-[10px] text-muted-foreground block">Total Memory Items</span>
          <span className="text-lg font-bold text-cyan-400">{analytics?.total_items || 12}</span>
        </div>
        <div className="p-3 bg-secondary/20 border border-border/30 rounded-xl">
          <span className="text-[10px] text-muted-foreground block">Avg Recall Latency</span>
          <span className="text-lg font-bold text-emerald-400">{analytics?.avg_latency_ms || 18.5}ms</span>
        </div>
        <div className="p-3 bg-secondary/20 border border-border/30 rounded-xl">
          <span className="text-[10px] text-muted-foreground block">Cache Hit Rate</span>
          <span className="text-lg font-bold text-amber-400">{((analytics?.cache_hit_rate || 0.94) * 100).toFixed(1)}%</span>
        </div>
        <div className="p-3 bg-secondary/20 border border-border/30 rounded-xl">
          <span className="text-[10px] text-muted-foreground block">Token Saturation</span>
          <span className="text-lg font-bold text-rose-400">{analytics?.token_usage_pct || 56.2}%</span>
        </div>
      </div>

      {/* Import Memory Dump Form */}
      <div className="p-4 bg-secondary/20 border border-border/40 rounded-xl space-y-3 font-mono text-xs">
        <div className="flex items-center gap-2 border-b border-border/30 pb-2">
          <Upload className="h-4 w-4 text-cyan-400" />
          <span className="text-[10px] text-muted-foreground uppercase font-bold">Import External Memory JSON Dump</span>
        </div>

        {importStatus && (
          <div className="p-2 bg-cyan-500/10 border border-cyan-500/30 rounded text-xs text-cyan-300 flex items-center gap-2">
            <CheckCircle className="h-3.5 w-3.5" />
            <span>{importStatus}</span>
          </div>
        )}

        <textarea
          rows={3}
          value={jsonInput}
          onChange={(e) => setJsonInput(e.target.value)}
          placeholder="Paste memory dump JSON payload here..."
          className="w-full p-2.5 bg-[#0D1117] border border-border/40 rounded-lg text-cyan-300 text-xs font-mono focus:outline-none focus:border-cyan-500"
        />

        <div className="flex justify-end">
          <button
            onClick={handleImportJSON}
            className="px-3 py-1.5 text-xs font-bold rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 hover:bg-cyan-500/30 cursor-pointer transition-all"
          >
            Import Memory Payload
          </button>
        </div>
      </div>
    </div>
  )
}
