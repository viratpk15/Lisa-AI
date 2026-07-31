// frontend/src/features/Workflows/components/builder/WorkflowCanvas.tsx

import { Cpu, Wrench, Database, Brain, Code, GitBranch, ShieldCheck, Globe } from "lucide-react"
import { useWorkflowStudioStore } from "../../store/useWorkflowStudioStore"
import type { WorkflowNode, WorkflowNodeType } from "../../types/workflows.types"

export function WorkflowCanvas() {
  const nodes = useWorkflowStudioStore((s) => s.nodes)
  const edges = useWorkflowStudioStore((s) => s.edges)
  const selectedNodeId = useWorkflowStudioStore((s) => s.selectedNodeId)
  const setSelectedNodeId = useWorkflowStudioStore((s) => s.setSelectedNodeId)
  const breakpoints = useWorkflowStudioStore((s) => s.breakpoints)
  const toggleBreakpoint = useWorkflowStudioStore((s) => s.toggleBreakpoint)

  const getNodeIcon = (type: WorkflowNodeType) => {
    switch (type) {
      case "agent": return <Cpu className="h-4 w-4 text-cyan-400" />
      case "tool": return <Wrench className="h-4 w-4 text-emerald-400" />
      case "rag": return <Database className="h-4 w-4 text-violet-400" />
      case "memory": return <Brain className="h-4 w-4 text-amber-400" />
      case "model": return <Code className="h-4 w-4 text-rose-400" />
      case "condition": return <GitBranch className="h-4 w-4 text-rose-400" />
      case "approval": return <ShieldCheck className="h-4 w-4 text-yellow-400" />
      default: return <Globe className="h-4 w-4 text-cyan-400" />
    }
  }

  return (
    <div className="relative h-137.5 bg-[#0D1117] border border-border/40 rounded-xl overflow-hidden flex items-center justify-center font-mono">
      {/* Grid Axis Background */}
      <div className="absolute inset-0 bg-[radial-gradient(#1E293B_1px,transparent_1px)] bg-size-[16px_16px] opacity-40 pointer-events-none" />

      {/* Render Edges as Flow Connections */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none">
        {edges.map((e) => {
          const srcNode = nodes.find((n) => n.id === e.source)
          const tgtNode = nodes.find((n) => n.id === e.target)
          if (!srcNode || !tgtNode) return null

          const x1 = srcNode.position.x + 80
          const y1 = srcNode.position.y + 35
          const x2 = tgtNode.position.x + 10
          const y2 = tgtNode.position.y + 35

          return (
            <g key={e.id}>
              <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="#38BDF8" strokeWidth="2" strokeDasharray="4" />
            </g>
          )
        })}
      </svg>

      {/* Render Interactive Nodes */}
      {nodes.map((node: WorkflowNode) => {
        const isSelected = selectedNodeId === node.id
        const hasBreakpoint = breakpoints.has(node.id)

        return (
          <div
            key={node.id}
            onClick={() => setSelectedNodeId(node.id)}
            style={{ transform: `translate(${node.position.x}px, ${node.position.y}px)` }}
            className={`absolute p-3 rounded-xl border w-48 shadow-lg cursor-pointer transition-all ${
              isSelected
                ? "bg-cyan-500/20 border-cyan-500 font-bold scale-105 z-10"
                : "bg-secondary/20 border-border/40 hover:border-cyan-500/40"
            }`}
          >
            <div className="flex items-center justify-between border-b border-border/30 pb-2 mb-2">
              <div className="flex items-center gap-2">
                {getNodeIcon(node.data.node_type)}
                <span className="text-xs text-foreground font-bold">{node.data.label}</span>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  toggleBreakpoint(node.id)
                }}
                className={`h-2.5 w-2.5 rounded-full cursor-pointer transition-colors ${
                  hasBreakpoint ? "bg-rose-500 shadow-rose-500/50 shadow-md" : "bg-secondary/40 hover:bg-rose-400"
                }`}
                title="Toggle Breakpoint"
              />
            </div>

            <div className="text-[10px] text-muted-foreground space-y-0.5">
              <div>Type: <span className="text-cyan-300 uppercase">{node.data.node_type}</span></div>
              <div className="truncate">ID: {node.id}</div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
