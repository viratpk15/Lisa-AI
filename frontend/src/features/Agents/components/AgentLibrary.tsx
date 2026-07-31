// frontend/src/features/Agents/components/AgentLibrary.tsx
import { useState } from "react"
import { Bot, Plus, Search, CheckCircle, Loader2, AlertTriangle, Inbox } from "lucide-react"
import { useAgentsQuery, useCreateAgentMutation } from "../services/agentsApi"

export default function AgentLibrary() {
  const [search, setSearch] = useState("")
  const [newAgentName, setNewAgentName] = useState("")

  const { data: agents, isLoading, isError, error, refetch } = useAgentsQuery()
  const createAgent = useCreateAgentMutation()

  const filtered = (agents ?? []).filter(
    (a) =>
      a.name.toLowerCase().includes(search.toLowerCase()) ||
      (a.description ?? "").toLowerCase().includes(search.toLowerCase())
  )

  const handleCreate = () => {
    const name = newAgentName.trim()
    if (!name) return
    createAgent.mutate(
      { name, description: null },
      { onSuccess: () => setNewAgentName("") }
    )
  }

  return (
    <div className="space-y-4 font-mono text-xs">
      {/* Top Action Bar */}
      <div className="flex items-center justify-between gap-3 bg-secondary/15 border border-border/40 p-4 rounded-xl">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search agents by name or capability..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 bg-secondary/30 border border-border/40 rounded-lg text-foreground text-xs font-mono"
          />
        </div>
        <input
          type="text"
          placeholder="New agent name..."
          value={newAgentName}
          onChange={(e) => setNewAgentName(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleCreate()}
          className="w-48 px-3 py-1.5 bg-secondary/30 border border-border/40 rounded-lg text-foreground text-xs font-mono"
        />
        <button
          onClick={handleCreate}
          disabled={createAgent.isPending || !newAgentName.trim()}
          className="flex items-center gap-1.5 px-3 py-1.5 font-bold rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 hover:bg-cyan-500/30 cursor-pointer transition-all disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {createAgent.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Plus className="h-3.5 w-3.5" />}
          Create New Agent
        </button>
      </div>

      {createAgent.isError && (
        <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-300 text-[11px]">
          <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
          Failed to create agent: {(createAgent.error as Error)?.message ?? "Unknown error"}
        </div>
      )}

      {/* Loading state */}
      {isLoading && (
        <div className="flex items-center justify-center gap-2 p-10 text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          Loading agents...
        </div>
      )}

      {/* Error state */}
      {isError && (
        <div className="flex flex-col items-center justify-center gap-2 p-10 text-center">
          <AlertTriangle className="h-6 w-6 text-red-400" />
          <p className="text-red-300">Failed to load agents: {(error as Error)?.message ?? "Unknown error"}</p>
          <button
            onClick={() => refetch()}
            className="px-3 py-1 mt-1 rounded bg-secondary/30 border border-border/40 hover:bg-secondary/50"
          >
            Retry
          </button>
        </div>
      )}

      {/* Empty state */}
      {!isLoading && !isError && filtered.length === 0 && (
        <div className="flex flex-col items-center justify-center gap-2 p-10 text-center text-muted-foreground">
          <Inbox className="h-6 w-6" />
          <p>{agents?.length ? "No agents match your search." : "No agents yet. Create your first one above."}</p>
        </div>
      )}

      {/* Agent Cards Grid */}
      {!isLoading && !isError && filtered.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {filtered.map((agent) => (
            <div key={agent.id} className="p-4 bg-secondary/20 border border-border/30 rounded-xl space-y-3 hover:border-cyan-500/40 transition-all">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                  <Bot className="h-4 w-4 text-cyan-400" />
                  <span className="text-foreground font-bold text-xs">{agent.name}</span>
                </div>
                <span
                  className={`text-[10px] px-2 py-0.5 rounded-full flex items-center gap-1 border ${
                    agent.is_active
                      ? "bg-emerald-500/10 text-emerald-300 border-emerald-500/30"
                      : "bg-secondary/30 text-muted-foreground border-border/40"
                  }`}
                >
                  <CheckCircle className="h-2.5 w-2.5" />
                  {agent.is_active ? "active" : "inactive"}
                </span>
              </div>

              <p className="text-muted-foreground text-[11px] leading-relaxed">
                {agent.description || "No description provided."}
              </p>

              <div className="pt-2 border-t border-border/30 text-[10px] text-muted-foreground">
                Created {new Date(agent.created_at).toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
