// frontend/src/features/Agents/components/TeamBuilder.tsx
import { Users, Bot, ArrowRight, ShieldCheck } from "lucide-react"

export default function TeamBuilder() {
  const teamNodes = [
    { id: "orchestrator", name: "Supervisor Orchestrator", role: "Goal Decomposition", color: "border-cyan-500 text-cyan-300" },
    { id: "researcher", name: "RAG Retrieval Specialist", role: "Knowledge Fetching", color: "border-emerald-500 text-emerald-300" },
    { id: "coder", name: "Python Execution Engineer", role: "Code Generation & Execution", color: "border-amber-500 text-amber-300" },
  ]

  return (
    <div className="space-y-4 font-mono text-xs">
      <div className="flex items-center justify-between border-b border-border/40 pb-3">
        <div className="flex items-center gap-2">
          <Users className="h-4 w-4 text-cyan-400" />
          <h3 className="text-xs font-bold text-foreground">Multi-Agent Swarm & Team Collaboration Topology</h3>
        </div>
        <span className="text-[10px] text-cyan-400 font-bold bg-cyan-500/10 border border-cyan-500/30 px-2 py-0.5 rounded">
          LangGraph Team Active
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {teamNodes.map((node, i) => (
          <div key={node.id} className={`p-4 bg-secondary/20 border rounded-xl space-y-2 ${node.color}`}>
            <div className="flex items-center justify-between">
              <span className="font-bold text-xs flex items-center gap-1.5">
                <Bot className="h-4 w-4" /> {node.name}
              </span>
              {i < teamNodes.length - 1 && <ArrowRight className="h-4 w-4 text-muted-foreground" />}
            </div>
            <div className="text-[10px] text-muted-foreground">Role: <span className="text-foreground">{node.role}</span></div>
          </div>
        ))}
      </div>

      <div className="p-3 bg-secondary/15 border border-border/40 rounded-xl flex items-center gap-2 text-muted-foreground text-[11px]">
        <ShieldCheck className="h-4 w-4 text-cyan-400 shrink-0" />
        <span>Multi-agent team routing uses LangGraph Supervisor nodes to route sub-goals dynamically between agents.</span>
      </div>
    </div>
  )
}