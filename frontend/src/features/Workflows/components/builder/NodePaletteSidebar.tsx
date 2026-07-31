// frontend/src/features/Workflows/components/builder/NodePaletteSidebar.tsx

import { Cpu, Wrench, Database, Brain, Code, GitBranch, ShieldCheck, Globe, Plus } from "lucide-react"
import { useWorkflowStudioStore } from "../../store/useWorkflowStudioStore"
import type { WorkflowNodeType } from "../../types/workflows.types"

export function NodePaletteSidebar() {
  const addNode = useWorkflowStudioStore((s) => s.addNode)
  const nodes = useWorkflowStudioStore((s) => s.nodes)

  const availableNodeTypes: { type: WorkflowNodeType; label: string; icon: any; color: string }[] = [
    { type: "agent", label: "Agent Node", icon: Cpu, color: "text-cyan-400 border-cyan-500/40" },
    { type: "tool", label: "Tool Node", icon: Wrench, color: "text-emerald-400 border-emerald-500/40" },
    { type: "rag", label: "RAG Node", icon: Database, color: "text-violet-400 border-violet-500/40" },
    { type: "memory", label: "Memory Node", icon: Brain, color: "text-amber-400 border-amber-500/40" },
    { type: "model", label: "Model Node", icon: Code, color: "text-rose-400 border-rose-500/40" },
    { type: "condition", label: "Condition Node", icon: GitBranch, color: "text-rose-400 border-rose-500/40" },
    { type: "approval", label: "Human Approval", icon: ShieldCheck, color: "text-yellow-400 border-yellow-500/40" },
    { type: "http", label: "HTTP Ingress", icon: Globe, color: "text-cyan-400 border-cyan-500/40" },
  ]

  const handleAddNode = (type: WorkflowNodeType, label: string) => {
    const newId = `node_${nodes.length + 1}`
    const xPos = 150 + (nodes.length % 3) * 220
    const yPos = 150 + Math.floor(nodes.length / 3) * 120

    addNode({
      id: newId,
      type: "custom",
      position: { x: xPos, y: yPos },
      data: {
        label,
        node_type: type,
        config: {},
      },
    })
  }

  return (
    <div className="space-y-3 bg-secondary/15 border border-border/40 rounded-xl p-4 font-mono text-xs">
      <h3 className="text-xs font-bold text-foreground uppercase border-b border-border/40 pb-2">Node Palette</h3>
      <div className="space-y-2">
        {availableNodeTypes.map((n) => {
          const Icon = n.icon
          return (
            <button
              key={n.type}
              onClick={() => handleAddNode(n.type, n.label)}
              className={`w-full p-2.5 rounded-lg border bg-secondary/20 hover:bg-secondary/40 flex items-center justify-between cursor-pointer transition-all ${n.color}`}
            >
              <div className="flex items-center gap-2">
                <Icon className="h-4 w-4" />
                <span className="font-bold text-foreground text-xs">{n.label}</span>
              </div>
              <Plus className="h-3.5 w-3.5 text-muted-foreground" />
            </button>
          )
        })}
      </div>
    </div>
  )
}
