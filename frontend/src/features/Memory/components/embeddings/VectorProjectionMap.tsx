// frontend/src/features/Memory/components/embeddings/VectorProjectionMap.tsx

import { useState } from "react"
import { Compass } from "lucide-react"
import { useVectorProjectionsQuery } from "../../services/memoryApi"
import { useMemoryStudioStore } from "../../store/useMemoryStudioStore"

export function VectorProjectionMap() {
  const selectedSessionId = useMemoryStudioStore((s) => s.selectedSessionId)
  const { data } = useVectorProjectionsQuery(selectedSessionId)
  const [selectedPointId, setSelectedPointId] = useState<string | null>(null)

  const points = data?.points || [
    { id: "vec_1", session_id: selectedSessionId, text_preview: "Jarvis Memory Studio 5-tier architecture", x: 25, y: 35, tier: "long_term" },
    { id: "vec_2", session_id: selectedSessionId, text_preview: "LangGraph execution state persistence", x: -40, y: 55, tier: "conversation" },
    { id: "vec_3", session_id: selectedSessionId, text_preview: "Reciprocal Rank Fusion hybrid search", x: 10, y: -45, tier: "long_term" },
    { id: "vec_4", session_id: selectedSessionId, text_preview: "Semantic graph entity extraction", x: -20, y: -30, tier: "semantic" },
  ]

  const activePoint = points.find((p) => p.id === selectedPointId) || points[0]

  return (
    <div className="space-y-4 bg-secondary/15 border border-border/40 rounded-xl p-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border/40 pb-3">
        <div className="flex items-center gap-2">
          <Compass className="h-4 w-4 text-rose-400" />
          <h3 className="text-xs font-bold text-foreground">2D UMAP Vector Projection Map</h3>
        </div>
        <span className="text-[10px] font-mono text-muted-foreground">{points.length} Vector Clusters</span>
      </div>

      {/* Vector Projection Canvas Area */}
      <div className="relative h-72 bg-[#0D1117] border border-border/40 rounded-xl overflow-hidden flex items-center justify-center">
        {/* Grid Axis Overlay */}
        <div className="absolute inset-0 bg-[radial-gradient(#1E293B_1px,transparent_1px)] bg-size-[16px_16px] opacity-40 pointer-events-none" />

        {/* Render Vector Nodes */}
        {points.map((p) => {
          const isSelected = activePoint?.id === p.id
          // Map x, y (-100 to 100) into container percentage
          const leftPercent = 50 + (p.x / 2)
          const topPercent = 50 - (p.y / 2)

          return (
            <button
              key={p.id}
              onClick={() => setSelectedPointId(p.id)}
              style={{ left: `${leftPercent}%`, top: `${topPercent}%` }}
              className={`absolute -translate-x-1/2 -translate-y-1/2 p-2 rounded-full border transition-all cursor-pointer ${
                isSelected
                  ? "bg-rose-500/30 border-rose-500 scale-125 z-10 shadow-lg"
                  : "bg-cyan-500/20 border-cyan-500/40 hover:scale-110"
              }`}
              title={p.text_preview}
            >
              <div className="h-2 w-2 rounded-full bg-rose-400" />
            </button>
          )
        })}
      </div>

      {/* Selected Vector Point Detail Drawer */}
      {activePoint && (
        <div className="p-4 bg-secondary/20 border border-border/40 rounded-xl space-y-2 font-mono text-xs">
          <div className="flex items-center justify-between border-b border-border/30 pb-2">
            <span className="text-[10px] text-muted-foreground uppercase font-bold">Selected Vector Cluster Payload</span>
            <span className="text-cyan-400 font-bold text-[11px]">{activePoint.id}</span>
          </div>
          <p className="text-foreground italic bg-[#0D1117] p-2.5 rounded border border-border/30">
            "{activePoint.text_preview}"
          </p>
          <div className="grid grid-cols-3 gap-2 text-[11px] pt-1">
            <div><span className="text-muted-foreground">X Coordinate:</span> <span className="text-rose-400 font-bold">{activePoint.x}</span></div>
            <div><span className="text-muted-foreground">Y Coordinate:</span> <span className="text-rose-400 font-bold">{activePoint.y}</span></div>
            <div><span className="text-muted-foreground">Tier:</span> <span className="text-emerald-400 font-bold uppercase">{activePoint.tier}</span></div>
          </div>
        </div>
      )}
    </div>
  )
}
