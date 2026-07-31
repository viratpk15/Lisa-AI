// frontend/src/features/Workflows/components/library/WorkflowLibraryPanel.tsx
import { useState } from "react"
import { GitBranch, CheckCircle, Search, Layers, Zap } from "lucide-react"

export function WorkflowLibraryPanel() {
  const [search, setSearch] = useState("")

  const templates = [
    {
      id: "wf_react_loop",
      name: "Standard ReAct Reasoning Graph",
      description: "2-node loop with tool execution and reflection fallback nodes.",
      category: "Reasoning Loop",
      nodes_count: 3,
      status: "ready",
    },
    {
      id: "wf_human_in_loop",
      name: "Human-in-the-Loop Guardrail Workflow",
      description: "Includes conditional approval step before invoking high-risk tools.",
      category: "Safety & Governance",
      nodes_count: 5,
      status: "ready",
    },
    {
      id: "wf_multi_agent_supervisor",
      name: "Multi-Agent Supervisor Routing Topology",
      description: "Routes goals dynamically to Researcher, Coder, and Synthesizer nodes.",
      category: "Multi-Agent Swarm",
      nodes_count: 4,
      status: "ready",
    },
  ]

  const filtered = templates.filter(
    (t) => t.name.toLowerCase().includes(search.toLowerCase()) || t.description.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="space-y-4 font-mono text-xs">
      <div className="flex items-center justify-between gap-3 bg-secondary/15 border border-border/40 p-4 rounded-xl">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search workflow graph templates..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 bg-secondary/30 border border-border/40 rounded-lg text-foreground text-xs font-mono"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {filtered.map((tmpl) => (
          <div key={tmpl.id} className="p-4 bg-secondary/20 border border-border/30 rounded-xl space-y-3 hover:border-cyan-500/40 transition-all">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-2">
                <GitBranch className="h-4 w-4 text-cyan-400" />
                <span className="text-foreground font-bold text-xs">{tmpl.name}</span>
              </div>
              <span className="text-[10px] bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 px-2 py-0.5 rounded-full flex items-center gap-1">
                <CheckCircle className="h-2.5 w-2.5 text-emerald-400" />
                {tmpl.status}
              </span>
            </div>

            <p className="text-muted-foreground text-[11px] leading-relaxed">{tmpl.description}</p>

            <div className="pt-2 border-t border-border/30 flex items-center justify-between text-[10px] text-muted-foreground">
              <span className="flex items-center gap-1">
                <Layers className="h-3 w-3 text-cyan-400" /> {tmpl.nodes_count} Nodes
              </span>
              <span className="text-cyan-300 font-bold">{tmpl.category}</span>
            </div>

            <button className="w-full py-1.5 font-bold rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 hover:bg-cyan-500/30 transition-all cursor-pointer flex items-center justify-center gap-1">
              <Zap className="h-3 w-3" /> Load Template into Canvas
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
