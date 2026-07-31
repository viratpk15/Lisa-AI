import { useState } from "react"
import { Sliders, Zap, Award, AlertCircle } from "lucide-react"
import { useRAGStudioStore } from "../../store/useRAGStudioStore"
import { runHybridSearchApi } from "../../services/ragApi"

export function HybridSearchPanel() {
  const queryText = useRAGStudioStore((s) => s.queryText)
  const setQueryText = useRAGStudioStore((s) => s.setQueryText)
  const topK = useRAGStudioStore((s) => s.topK)
  const setTopK = useRAGStudioStore((s) => s.setTopK)
  const hybridAlpha = useRAGStudioStore((s) => s.hybridAlpha)
  const setHybridAlpha = useRAGStudioStore((s) => s.setHybridAlpha)
  const useReranker = useRAGStudioStore((s) => s.useReranker)
  const setUseReranker = useRAGStudioStore((s) => s.setUseReranker)
  const searchResults = useRAGStudioStore((s) => s.searchResults)
  const setSearchResults = useRAGStudioStore((s) => s.setSearchResults)
  const isSearching = useRAGStudioStore((s) => s.isSearching)
  const setIsSearching = useRAGStudioStore((s) => s.setIsSearching)

  const [searchError, setSearchError] = useState<string | null>(null)

  const handleRunSearch = async () => {
    if (!queryText) return
    setIsSearching(true)
    setSearchError(null)
    try {
      const res = await runHybridSearchApi({
        query: queryText,
        top_k: topK,
        alpha: hybridAlpha,
        use_reranker: useReranker,
      })
      setSearchResults(res.results)
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "An unexpected error occurred"
      setSearchError(message)
    } finally {
      setIsSearching(false)
    }
  }


  return (
    <div className="space-y-4 bg-secondary/15 border border-border/40 rounded-xl p-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border/40 pb-3">
        <div className="flex items-center gap-2">
          <Sliders className="h-4 w-4 text-cyan-400" />
          <h3 className="text-xs font-bold text-foreground">Hybrid Dense+Sparse Vector Search & Reranker Panel</h3>
        </div>

        <button
          onClick={handleRunSearch}
          disabled={isSearching || !queryText}
          className="inline-flex items-center gap-1.5 px-4 py-1.5 text-xs font-bold bg-cyan-500 hover:bg-cyan-400 text-black rounded-lg cursor-pointer transition-all shadow-md disabled:opacity-50"
        >
          <Zap className="h-3.5 w-3.5 fill-current" />
          {isSearching ? "Searching..." : "Run Hybrid Search (⌘Enter)"}
        </button>
      </div>

      {/* Query Bar */}
      <input
        type="text"
        value={queryText}
        onChange={(e) => setQueryText(e.target.value)}
        placeholder="Enter natural language query or keyword..."
        className="w-full px-3 py-2 text-xs font-mono bg-[#0D1117] border border-border/50 rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
      />

      {/* Alpha Slider Controls */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-3 bg-secondary/20 border border-border/40 rounded-lg text-xs font-mono">
        <div className="space-y-1">
          <div className="flex justify-between text-[10px] text-muted-foreground uppercase">
            <span>Alpha: {hybridAlpha.toFixed(2)}</span>
            <span className="text-cyan-400 font-bold">
              {hybridAlpha === 0 ? "100% BM25" : hybridAlpha === 1 ? "100% Dense" : `${Math.round(hybridAlpha * 100)}% Dense / ${Math.round((1 - hybridAlpha) * 100)}% Sparse`}
            </span>
          </div>
          <input
            type="range"
            min="0.0"
            max="1.0"
            step="0.05"
            value={hybridAlpha}
            onChange={(e) => setHybridAlpha(Number(e.target.value))}
            className="w-full h-1.5 bg-secondary/60 rounded-lg appearance-none cursor-pointer accent-cyan-500"
          />
        </div>

        <div className="space-y-1">
          <div className="flex justify-between text-[10px] text-muted-foreground uppercase">
            <span>Top-K Candidates: {topK}</span>
          </div>
          <input
            type="range"
            min="1"
            max="20"
            step="1"
            value={topK}
            onChange={(e) => setTopK(Number(e.target.value))}
            className="w-full h-1.5 bg-secondary/60 rounded-lg appearance-none cursor-pointer accent-cyan-500"
          />
        </div>

        <div className="space-y-1 flex items-center justify-between pt-3">
          <span className="text-[10px] text-muted-foreground uppercase">Cross-Encoder Reranker</span>
          <button
            onClick={() => setUseReranker(!useReranker)}
            className={`px-3 py-1 text-xs font-bold rounded-lg cursor-pointer transition-all ${
              useReranker
                ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                : "bg-secondary/40 text-muted-foreground border border-border/40"
            }`}
          >
            {useReranker ? "Enabled" : "Disabled"}
          </button>
        </div>
      </div>

      {/* Error Banner */}
      {searchError && (
        <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/40 rounded-lg text-xs font-mono text-red-400">
          <AlertCircle className="h-3.5 w-3.5 shrink-0" />
          <span>{searchError}</span>
        </div>
      )}

      {/* Results Matrix */}
      {searchResults.length === 0 ? (
        <div className="p-8 text-center text-xs text-muted-foreground italic bg-secondary/10 border border-dashed border-border/40 rounded-xl">
          Click "Run Hybrid Search" to retrieve ranked candidate chunks.
        </div>
      ) : (
        <div className="space-y-3 font-mono text-xs">
          <span className="font-bold text-foreground">Retrieved Hybrid Candidate Chunks ({searchResults.length})</span>

          <div className="space-y-2">
            {searchResults.map((res, idx) => (
              <div
                key={res.chunk_id}
                className="p-3 bg-[#0D1117] border border-border/40 hover:border-cyan-500/40 rounded-xl space-y-2 transition-all"
              >
                <div className="flex items-center justify-between border-b border-border/40 pb-1.5 text-[11px]">
                  <span className="font-bold text-cyan-400 flex items-center gap-1.5">
                    <Award className="h-3.5 w-3.5 text-amber-400" />
                    Rank #{idx + 1} ({res.chunk_id})
                  </span>
                  <div className="flex items-center gap-2 text-[10px]">
                    <span className="text-muted-foreground">Dense: <strong className="text-cyan-400">{res.dense_score}</strong></span>
                    <span className="text-muted-foreground">BM25: <strong className="text-violet-400">{res.sparse_score}</strong></span>
                    <span className="text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/30">
                      Rerank Score: {res.rerank_score}
                    </span>
                  </div>
                </div>

                <p className="text-[11px] text-[#C9D1D9] leading-relaxed">{res.raw_text}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
