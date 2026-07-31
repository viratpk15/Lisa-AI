import { useState } from "react"
import { Scissors, Play, Layers } from "lucide-react"
import { useRAGStudioStore } from "../../store/useRAGStudioStore"
import { previewChunkingApi } from "../../services/ragApi"

export function ChunkInspector() {
  const chunkSize = useRAGStudioStore((s) => s.chunkSize)
  const chunkOverlap = useRAGStudioStore((s) => s.chunkOverlap)
  const chunkStrategy = useRAGStudioStore((s) => s.chunkStrategy)
  const setChunkParams = useRAGStudioStore((s) => s.setChunkParams)

  const [sampleText, setSampleText] = useState(
    "Jarvis AIOS is a high-performance AI Operating System engineered for extensibility and production deployment. It orchestrates LangGraph execution nodes and ToolEngine tool execution routines with ChromaDB HNSW vector index."
  )
  const [chunkPreviews, setChunkPreviews] = useState<any[]>([])
  const [isProcessing, setIsProcessing] = useState(false)

  const handlePreview = async () => {
    setIsProcessing(true)
    try {
      const res = await previewChunkingApi({
        text: sampleText,
        chunk_size: chunkSize,
        overlap: chunkOverlap,
        strategy: chunkStrategy,
      })
      setChunkPreviews(res)
    } catch (err: any) {
      console.error(err)
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="space-y-4 bg-secondary/15 border border-border/40 rounded-xl p-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border/40 pb-3">
        <div className="flex items-center gap-2">
          <Scissors className="h-4 w-4 text-cyan-400" />
          <h3 className="text-xs font-bold text-foreground">Chunking Strategy Inspector & Diff Preview</h3>
        </div>

        <button
          onClick={handlePreview}
          disabled={isProcessing}
          className="inline-flex items-center gap-1.5 px-4 py-1.5 text-xs font-bold bg-cyan-500 hover:bg-cyan-400 text-black rounded-lg cursor-pointer transition-all shadow-md disabled:opacity-50"
        >
          <Play className="h-3.5 w-3.5 fill-current" />
          {isProcessing ? "Chunking..." : "Preview Chunking"}
        </button>
      </div>

      {/* Chunking Parameter Sliders */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 p-3 bg-secondary/20 border border-border/40 rounded-lg text-xs font-mono">
        <div className="space-y-1">
          <label className="text-[10px] text-muted-foreground uppercase">Strategy</label>
          <div className="flex gap-1">
            {(["fixed", "semantic", "recursive"] as const).map((strat) => (
              <button
                key={strat}
                onClick={() => setChunkParams(chunkSize, chunkOverlap, strat)}
                className={`px-2 py-1 text-[10px] rounded border cursor-pointer capitalize ${
                  chunkStrategy === strat
                    ? "bg-cyan-500/20 text-cyan-300 border-cyan-500/40 font-bold"
                    : "bg-secondary/40 text-muted-foreground border-border/40"
                }`}
              >
                {strat}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-1">
          <div className="flex justify-between text-[10px] text-muted-foreground uppercase">
            <span>Chunk Size: {chunkSize} tokens</span>
          </div>
          <input
            type="range"
            min="64"
            max="1024"
            step="32"
            value={chunkSize}
            onChange={(e) => setChunkParams(Number(e.target.value), chunkOverlap, chunkStrategy)}
            className="w-full h-1.5 bg-secondary/60 rounded-lg appearance-none cursor-pointer accent-cyan-500"
          />
        </div>

        <div className="space-y-1">
          <div className="flex justify-between text-[10px] text-muted-foreground uppercase">
            <span>Overlap: {chunkOverlap} tokens</span>
          </div>
          <input
            type="range"
            min="0"
            max="128"
            step="8"
            value={chunkOverlap}
            onChange={(e) => setChunkParams(chunkSize, Number(e.target.value), chunkStrategy)}
            className="w-full h-1.5 bg-secondary/60 rounded-lg appearance-none cursor-pointer accent-cyan-500"
          />
        </div>
      </div>

      {/* Raw Input Textarea */}
      <div className="space-y-1.5">
        <label className="text-xs font-mono font-bold text-foreground">Sample Document Input</label>
        <textarea
          rows={3}
          value={sampleText}
          onChange={(e) => setSampleText(e.target.value)}
          className="w-full p-2.5 text-xs font-mono bg-[#0D1117] border border-border/50 rounded-lg text-[#C9D1D9] focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
        />
      </div>

      {/* Chunk Previews Output */}
      {chunkPreviews.length > 0 && (
        <div className="space-y-2 font-mono text-xs">
          <span className="text-xs font-bold text-foreground flex items-center gap-1.5">
            <Layers className="h-3.5 w-3.5 text-cyan-400" /> Output Chunk Segments ({chunkPreviews.length})
          </span>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {chunkPreviews.map((chk) => (
              <div key={chk.chunk_index} className="p-3 bg-[#0D1117] border border-border/40 rounded-xl space-y-1.5">
                <div className="flex items-center justify-between text-[10px] text-muted-foreground border-b border-border/30 pb-1">
                  <span className="font-bold text-cyan-400">Chunk #{chk.chunk_index + 1}</span>
                  <span>{chk.token_length} words</span>
                </div>
                <p className="text-[11px] text-[#C9D1D9] leading-relaxed">{chk.raw_text}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
