// frontend/src/features/Workflows/components/builder/NodePropertyInspector.tsx

import { useState } from "react"
import { Sliders, Code } from "lucide-react"
import { useWorkflowStudioStore } from "../../store/useWorkflowStudioStore"

export function NodePropertyInspector() {
  const selectedNodeId = useWorkflowStudioStore((s) => s.selectedNodeId)
  const nodes = useWorkflowStudioStore((s) => s.nodes)
  const updateNodeConfig = useWorkflowStudioStore((s) => s.updateNodeConfig)

  const selectedNode = nodes.find((n) => n.id === selectedNodeId)
  const [paramKey, setParamKey] = useState("")
  const [paramVal, setParamVal] = useState("")

  if (!selectedNode) {
    return (
      <div className="p-6 text-center text-muted-foreground italic border border-dashed border-border/40 rounded-xl font-mono text-xs">
        Select a node on the canvas to inspect and edit properties.
      </div>
    )
  }

  const handleSaveParam = (e: React.FormEvent) => {
    e.preventDefault()
    if (!paramKey) return
    updateNodeConfig(selectedNode.id, { [paramKey]: paramVal })
    setParamKey("")
    setParamVal("")
  }

  return (
    <div className="space-y-4 bg-secondary/15 border border-border/40 rounded-xl p-4 font-mono text-xs">
      <div className="flex items-center gap-2 border-b border-border/40 pb-3">
        <Sliders className="h-4 w-4 text-cyan-400" />
        <h3 className="text-xs font-bold text-foreground">Node Property Inspector</h3>
      </div>

      <div className="space-y-2 bg-secondary/20 p-3 rounded-lg border border-border/30">
        <div><span className="text-muted-foreground text-[10px]">Node ID:</span> <span className="text-cyan-400 font-bold">{selectedNode.id}</span></div>
        <div><span className="text-muted-foreground text-[10px]">Label:</span> <span className="text-foreground">{selectedNode.data.label}</span></div>
        <div><span className="text-muted-foreground text-[10px]">Type:</span> <span className="text-emerald-400 uppercase font-bold">{selectedNode.data.node_type}</span></div>
      </div>

      {/* Config KV Form */}
      <div className="space-y-2">
        <span className="text-[10px] text-muted-foreground uppercase font-bold">Node Configuration Parameters</span>
        <form onSubmit={handleSaveParam} className="space-y-2">
          <input
            type="text"
            placeholder="Parameter Key (e.g. agent_id)"
            value={paramKey}
            onChange={(e) => setParamKey(e.target.value)}
            className="w-full p-2 bg-secondary/30 border border-border/40 rounded text-foreground text-xs"
          />
          <input
            type="text"
            placeholder="Parameter Value (e.g. code_assistant)"
            value={paramVal}
            onChange={(e) => setParamVal(e.target.value)}
            className="w-full p-2 bg-secondary/30 border border-border/40 rounded text-foreground text-xs"
          />
          <button
            type="submit"
            className="w-full py-1.5 font-bold rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 hover:bg-cyan-500/30 transition-all cursor-pointer"
          >
            Update Node Configuration
          </button>
        </form>
      </div>

      {/* Raw Config Output */}
      <div className="space-y-1">
        <span className="text-[10px] text-muted-foreground uppercase font-bold flex items-center gap-1">
          <Code className="h-3 w-3" /> Current Node Config JSON
        </span>
        <pre className="p-3 bg-[#0D1117] border border-border/40 rounded-lg text-cyan-300 text-[11px] overflow-x-auto">
          {JSON.stringify(selectedNode.data.config, null, 2)}
        </pre>
      </div>
    </div>
  )
}
