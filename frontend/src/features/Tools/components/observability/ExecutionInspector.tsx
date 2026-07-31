import { useState } from "react"
import { X, Code, FileText, Activity } from "lucide-react"
import type { ToolResult } from "../../types/tools.types"
import { JsonViewer } from "../common/JsonViewer"
import { TraceTimeline } from "./TraceTimeline"

interface ExecutionInspectorProps {
  result: ToolResult | null
  onClose: () => void
}

export function ExecutionInspector({ result, onClose }: ExecutionInspectorProps) {
  const [activeTab, setActiveTab] = useState<"summary" | "timeline" | "raw">("summary")

  if (!result) return null

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-xs flex justify-end z-50 p-0 animate-in fade-in duration-150">
      <div className="bg-[#121826] border-l border-border/40 w-full max-w-2xl h-full flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="h-12 px-4 bg-secondary/30 border-b border-border/40 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-cyan-400" />
            <h3 className="text-xs font-bold text-foreground">Execution Trace Inspector: {result.tool_name}</h3>
            <span className="text-[10px] font-mono bg-secondary/50 px-2 py-0.5 rounded text-muted-foreground">
              {result.execution_id}
            </span>
          </div>

          <button
            onClick={onClose}
            className="p-1 text-muted-foreground hover:text-foreground cursor-pointer rounded"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 px-4 py-2 bg-secondary/10 border-b border-border/40 text-xs">
          <button
            onClick={() => setActiveTab("summary")}
            className={`px-3 py-1 font-semibold rounded cursor-pointer transition-colors ${
              activeTab === "summary" ? "bg-cyan-500/20 text-cyan-400" : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Summary & Params
          </button>

          <button
            onClick={() => setActiveTab("timeline")}
            className={`px-3 py-1 font-semibold rounded cursor-pointer transition-colors ${
              activeTab === "timeline" ? "bg-cyan-500/20 text-cyan-400" : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Trace Timeline
          </button>

          <button
            onClick={() => setActiveTab("raw")}
            className={`px-3 py-1 font-semibold rounded cursor-pointer transition-colors ${
              activeTab === "raw" ? "bg-cyan-500/20 text-cyan-400" : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Raw ToolResult JSON
          </button>
        </div>

        {/* Inspector Body Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin">
          {activeTab === "summary" && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                <div className="p-2.5 bg-secondary/20 border border-border/40 rounded-lg space-y-1">
                  <span className="text-[10px] text-muted-foreground uppercase">Status Outcome</span>
                  <div className="font-bold text-emerald-400">{result.status}</div>
                </div>

                <div className="p-2.5 bg-secondary/20 border border-border/40 rounded-lg space-y-1">
                  <span className="text-[10px] text-muted-foreground uppercase">Duration</span>
                  <div className="font-bold text-cyan-400">{result.duration_ms.toFixed(1)} ms</div>
                </div>
              </div>

              <div className="space-y-1">
                <span className="text-xs font-bold text-foreground flex items-center gap-1">
                  <FileText className="h-3.5 w-3.5 text-cyan-400" />
                  Invocation Output
                </span>
                <JsonViewer data={result.output} title="Raw Output" defaultExpanded={true} />
              </div>

              {result.structured_output && (
                <div className="space-y-1">
                  <span className="text-xs font-bold text-foreground flex items-center gap-1">
                    <Code className="h-3.5 w-3.5 text-violet-400" />
                    Structured Properties
                  </span>
                  <JsonViewer data={result.structured_output} title="Structured Data" defaultExpanded={true} />
                </div>
              )}
            </div>
          )}

          {activeTab === "timeline" && <TraceTimeline result={result} />}

          {activeTab === "raw" && <JsonViewer data={result} title="Complete ToolResult Object" defaultExpanded={true} />}
        </div>
      </div>
    </div>
  )
}
