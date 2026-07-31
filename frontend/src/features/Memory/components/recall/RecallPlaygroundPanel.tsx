// frontend/src/features/Memory/components/recall/RecallPlaygroundPanel.tsx

import { useState } from "react"
import { Search, Zap, Award, AlertCircle } from "lucide-react"
import { useMemoryStudioStore } from "../../store/useMemoryStudioStore"
import { runRecallSearchApi } from "../../services/memoryApi"
import type { RankedMemoryHit } from "../../types/memory.types"

export function RecallPlaygroundPanel() {
  const selectedSessionId = useMemoryStudioStore((s) => s.selectedSessionId)
  const recallQuery = useMemoryStudioStore((s) => s.recallQuery)
  const setRecallQuery = useMemoryStudioStore((s) => s.setRecallQuery)
  const recallTopK = useMemoryStudioStore((s) => s.recallTopK)
  const setRecallTopK = useMemoryStudioStore((s) => s.setRecallTopK)
  const recallAlpha = useMemoryStudioStore((s) => s.recallAlpha)
  const setRecallAlpha = useMemoryStudioStore((s) => s.setRecallAlpha)

  const [results, setResults] = useState<RankedMemoryHit[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [searchError, setSearchError] = useState<string | null>(null)

  const handleRunRecall = async () => {
    if (!recallQuery) return
    setIsSearching(true)
    setSearchError(null)
    try {
      const res = await runRecallSearchApi({
        session_id: selectedSessionId,
        query: recallQuery,
        top_k: recallTopK,
        alpha: recallAlpha,
      })
      setResults(res.results)
    } catch (err: unknown) {
      setSearchError(err instanceof Error ? err.message : "Recall search failed")
    } finally {
      setIsSearching(false)
    }
  }

  return (
    <div className="space-y-4 bg-secondary/15 border border-border/40 rounded-xl p-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border/40 pb-3">
        <div className="flex items-center gap-2">
          <Zap className="h-4 w-4 text-amber-400" />
          <h3 className="text-xs font-bold text-foreground">Interactive Hybrid RRF Recall Bench</h3>
        </div>
        <button
          onClick={handleRunRecall}
          disabled={isSearching}
          className="px-3 py-1.5 text-xs font-bold font-mono rounded-lg bg-amber-500/20 text-amber-300 border border-amber-500/40 hover:bg-amber-500/30 cursor-pointer transition-all disabled:opacity-50"
        >
          {isSearching ? "Recalling..." : "Run Hybrid Recall"}
        </button>
      </div>

      {/* Query Bar */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            value={recallQuery}
            onChange={(e) => setRecallQuery(e.target.value)}
            placeholder="Enter recall query (e.g. vector search latency)..."
            className="w-full pl-9 pr-3 py-2 bg-secondary/30 border border-border/40 rounded-lg text-xs font-mono text-foreground focus:outline-none focus:border-amber-500"
          />
        </div>
      </div>

      {/* Parameters Panel */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-secondary/20 border border-border/30 rounded-xl font-mono text-xs">
        <div className="space-y-1">
          <div className="flex justify-between">
            <span className="text-[10px] text-muted-foreground uppercase font-bold">Top-K Candidate Limit</span>
            <span className="text-amber-400 font-bold">{recallTopK} Candidates</span>
          </div>
          <input
            type="range"
            min={1}
            max={20}
            value={recallTopK}
            onChange={(e) => setRecallTopK(Number(e.target.value))}
            className="w-full accent-amber-400 cursor-pointer"
          />
        </div>

        <div className="space-y-1">
          <div className="flex justify-between">
            <span className="text-[10px] text-muted-foreground uppercase font-bold">Hybrid Alpha Weight (Dense vs Sparse)</span>
            <span className="text-cyan-400 font-bold">Alpha: {recallAlpha.toFixed(2)}</span>
          </div>
          <input
            type="range"
            min={0}
            max={1}
            step={0.05}
            value={recallAlpha}
            onChange={(e) => setRecallAlpha(Number(e.target.value))}
            className="w-full accent-cyan-400 cursor-pointer"
          />
        </div>
      </div>

      {/* Error Banner */}
      {searchError && (
        <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-2 text-xs font-mono text-red-400">
          <AlertCircle className="h-3.5 w-3.5 shrink-0" />
          <span>{searchError}</span>
        </div>
      )}

      {/* Results Matrix */}
      {results.length === 0 ? (
        <div className="p-8 text-center text-xs text-muted-foreground italic bg-secondary/10 border border-dashed border-border/40 rounded-xl font-mono">
          Click "Run Hybrid Recall" to test candidate ranking across Dense and Sparse retrieval.
        </div>
      ) : (
        <div className="space-y-3 font-mono text-xs">
          <span className="font-bold text-foreground uppercase text-[10px]">Ranked Recall Candidates ({results.length})</span>
          <div className="space-y-2">
            {results.map((hit, idx) => (
              <div key={idx} className="p-3 bg-secondary/20 border border-border/40 rounded-xl space-y-2">
                <div className="flex items-center justify-between border-b border-border/30 pb-1.5">
                  <div className="flex items-center gap-2">
                    <Award className="h-3.5 w-3.5 text-amber-400" />
                    <span className="text-amber-400 font-bold">Rank #{idx + 1}</span>
                    <span className="text-[10px] text-muted-foreground uppercase">[{hit.tier}]</span>
                  </div>
                  <span className="text-cyan-400 font-bold">RRF Score: {hit.rrf_score}</span>
                </div>
                <p className="text-foreground text-xs">{hit.content}</p>
                <div className="flex gap-4 text-[10px] text-muted-foreground pt-1">
                  <span>Dense Score: <strong className="text-emerald-400">{hit.dense_score}</strong></span>
                  <span>Sparse Score: <strong className="text-violet-400">{hit.sparse_score}</strong></span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
