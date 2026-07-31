// frontend/src/features/Memory/components/timeline/MemoryTimelinePanel.tsx

import { useState } from "react"
import { Clock, Filter, Trash2, Code, Server, Database, Brain, Cpu, AlertCircle } from "lucide-react"
import { useMemoryStudioStore } from "../../store/useMemoryStudioStore"
import { useMemoryTimelineQuery, deleteMemoryItemApi, flushWorkingMemoryApi } from "../../services/memoryApi"
import { useQueryClient } from "@tanstack/react-query"
import { queryKeys } from "@/services/queries/queryKeys"
import type { MemoryTierFilterType } from "../../types/memory.types"

export function MemoryTimelinePanel() {
  const queryClient = useQueryClient()
  const selectedSessionId = useMemoryStudioStore((s) => s.selectedSessionId)
  const tierFilter = useMemoryStudioStore((s) => s.tierFilter)
  const setTierFilter = useMemoryStudioStore((s) => s.setTierFilter)
  const selectedMemoryId = useMemoryStudioStore((s) => s.selectedMemoryId)
  const setSelectedMemoryId = useMemoryStudioStore((s) => s.setSelectedMemoryId)

  const { data: timeline = [], isLoading, isError, error } = useMemoryTimelineQuery(selectedSessionId, tierFilter)
  const [actionError, setActionError] = useState<string | null>(null)

  const selectedItem = timeline.find((item) => item.id === selectedMemoryId) || timeline[0] || null

  const handleDeleteItem = async (memoryId: string) => {
    setActionError(null)
    try {
      await deleteMemoryItemApi(memoryId)
      queryClient.invalidateQueries({ queryKey: queryKeys.memory.all() })
      if (selectedMemoryId === memoryId) {
        setSelectedMemoryId(null)
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to delete memory item"
      setActionError(msg)
    }
  }

  const handleFlushWorking = async () => {
    setActionError(null)
    try {
      await flushWorkingMemoryApi(selectedSessionId)
      queryClient.invalidateQueries({ queryKey: queryKeys.memory.all() })
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to flush working memory"
      setActionError(msg)
    }
  }

  const filters: { id: MemoryTierFilterType; label: string }[] = [
    { id: "all", label: "All Tiers" },
    { id: "working", label: "1. Working" },
    { id: "conversation", label: "2. Conversation" },
    { id: "episodic", label: "3. Episodic" },
    { id: "semantic", label: "4. Semantic" },
    { id: "long_term", label: "5. Long-term" },
  ]

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 h-full">
      {/* Timeline Stream (7 cols) */}
      <div className="lg:col-span-7 flex flex-col space-y-4 bg-secondary/15 border border-border/40 rounded-xl p-4">
        <div className="flex items-center justify-between border-b border-border/40 pb-3">
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-cyan-400" />
            <h3 className="text-xs font-bold text-foreground">Chronological Memory Event Stream</h3>
          </div>
          <button
            onClick={handleFlushWorking}
            className="px-2.5 py-1 text-[11px] font-mono font-medium rounded-lg bg-red-500/10 text-red-400 border border-red-500/30 hover:bg-red-500/20 cursor-pointer transition-all"
          >
            Flush Working Memory
          </button>
        </div>

        {/* Tier Filter Bar */}
        <div className="flex flex-wrap items-center gap-1.5 bg-secondary/20 p-1.5 rounded-lg border border-border/30">
          <Filter className="h-3.5 w-3.5 text-muted-foreground ml-1 mr-1" />
          {filters.map((f) => (
            <button
              key={f.id}
              onClick={() => setTierFilter(f.id)}
              className={`px-2.5 py-1 text-[11px] font-mono rounded-md cursor-pointer transition-all ${
                tierFilter === f.id
                  ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 font-bold"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/40"
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>

        {/* Action Error Banner */}
        {actionError && (
          <div className="p-2.5 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-2 text-xs text-red-400 font-mono">
            <AlertCircle className="h-3.5 w-3.5 shrink-0" />
            <span>{actionError}</span>
          </div>
        )}

        {/* Event List */}
        <div className="flex-1 overflow-y-auto space-y-2 pr-1">
          {isLoading ? (
            <div className="p-8 text-center text-xs text-muted-foreground font-mono">Loading memory stream...</div>
          ) : isError ? (
            <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-xs text-red-400 font-mono">
              Error fetching memory timeline: {error instanceof Error ? error.message : "Unknown error"}
            </div>
          ) : timeline.length === 0 ? (
            <div className="p-8 text-center text-xs text-muted-foreground italic border border-dashed border-border/40 rounded-xl">
              No memory items found for selected filter.
            </div>
          ) : (
            timeline.map((item) => {
              const isSelected = selectedItem?.id === item.id
              return (
                <div
                  key={item.id}
                  onClick={() => setSelectedMemoryId(item.id)}
                  className={`p-3 rounded-xl border transition-all cursor-pointer flex items-start justify-between gap-3 ${
                    isSelected
                      ? "bg-cyan-500/15 border-cyan-500/60 shadow-sm"
                      : "bg-secondary/20 border-border/40 hover:bg-secondary/40"
                  }`}
                >
                  <div className="flex items-start gap-2.5 overflow-hidden">
                    {item.tier === "working" && <Cpu className="h-4 w-4 text-cyan-400 mt-0.5 shrink-0" />}
                    {item.tier === "conversation" && <Server className="h-4 w-4 text-violet-400 mt-0.5 shrink-0" />}
                    {item.tier === "episodic" && <Database className="h-4 w-4 text-emerald-400 mt-0.5 shrink-0" />}
                    {item.tier === "semantic" && <Brain className="h-4 w-4 text-amber-400 mt-0.5 shrink-0" />}
                    {item.tier === "long_term" && <Code className="h-4 w-4 text-rose-400 mt-0.5 shrink-0" />}

                    <div className="space-y-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-cyan-400">
                          [{item.tier}]
                        </span>
                        <span className="text-[10px] font-mono text-muted-foreground">
                          {new Date(item.created_at).toLocaleTimeString()}
                        </span>
                      </div>
                      <p className="text-xs text-foreground font-mono truncate">{item.content}</p>
                    </div>
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDeleteItem(item.id)
                    }}
                    className="p-1 hover:bg-red-500/20 rounded text-muted-foreground hover:text-red-400 cursor-pointer transition-colors"
                    title="Delete Memory Item"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              )
            })
          )}
        </div>
      </div>

      {/* Memory Inspector Card (5 cols) */}
      <div className="lg:col-span-5 flex flex-col space-y-4 bg-secondary/15 border border-border/40 rounded-xl p-4">
        <div className="flex items-center gap-2 border-b border-border/40 pb-3">
          <Code className="h-4 w-4 text-violet-400" />
          <h3 className="text-xs font-bold text-foreground">Memory Item Inspector</h3>
        </div>

        {selectedItem ? (
          <div className="space-y-4 flex-1 overflow-y-auto">
            {/* Metadata Summary */}
            <div className="grid grid-cols-2 gap-2 text-xs font-mono bg-secondary/20 p-3 rounded-lg border border-border/30">
              <div>
                <span className="text-[10px] text-muted-foreground block">ID</span>
                <span className="text-cyan-400 font-bold">{selectedItem.id}</span>
              </div>
              <div>
                <span className="text-[10px] text-muted-foreground block">Tier</span>
                <span className="text-emerald-400 font-bold uppercase">{selectedItem.tier}</span>
              </div>
              <div>
                <span className="text-[10px] text-muted-foreground block">Tokens</span>
                <span className="text-foreground">{selectedItem.tokens} tokens</span>
              </div>
              <div>
                <span className="text-[10px] text-muted-foreground block">TTL</span>
                <span className="text-foreground">{selectedItem.ttl_seconds ? `${selectedItem.ttl_seconds}s` : "Permanent"}</span>
              </div>
            </div>

            {/* Content Preview */}
            <div className="space-y-1.5 font-mono text-xs">
              <span className="text-[10px] text-muted-foreground uppercase font-bold">Content Text</span>
              <div className="p-3 bg-[#0D1117] border border-border/40 rounded-lg text-foreground leading-relaxed whitespace-pre-wrap">
                {selectedItem.content}
              </div>
            </div>

            {/* Raw JSON Payload */}
            <div className="space-y-1.5 font-mono text-xs">
              <span className="text-[10px] text-muted-foreground uppercase font-bold">Raw Payload JSON</span>
              <pre className="p-3 bg-[#0D1117] border border-border/40 rounded-lg text-cyan-300 text-[11px] overflow-x-auto">
                {JSON.stringify(selectedItem.metadata_json, null, 2)}
              </pre>
            </div>
          </div>
        ) : (
          <div className="p-8 text-center text-xs text-muted-foreground italic border border-dashed border-border/40 rounded-xl">
            Select a memory item from the timeline stream to inspect its metadata and payload.
          </div>
        )}
      </div>
    </div>
  )
}
