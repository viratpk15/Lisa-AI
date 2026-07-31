// frontend/src/features/Memory/components/semantic/SemanticMemoryPanel.tsx
//
// Memory Studio — Semantic Memory Tab
// Provides entity list, lifecycle badges, search, pin, delete, and inline explainability inspector.

import { useState } from "react"
import {
  useMemoryEntitiesQuery,
  usePinMemoryEntity,
  useDeleteMemoryEntity,
  useTriggerMemoryExtraction,
  useExplainMemoryRecall,
} from "../../services/memoryApi"
import type { MemoryEntity, ExplainabilityTrace } from "../../types/memory.types"

const LIFECYCLE_COLORS: Record<string, string> = {
  candidate: "bg-amber-500/15 text-amber-300 border-amber-500/30",
  validated: "bg-blue-500/15 text-blue-300 border-blue-500/30",
  active: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
  compressed: "bg-purple-500/15 text-purple-300 border-purple-500/30",
  archived: "bg-slate-500/15 text-slate-400 border-slate-500/30",
}

const CATEGORY_ICONS: Record<string, string> = {
  Preference: "⚙️",
  Goal: "🎯",
  Fact: "📌",
  Project: "🚀",
  Architecture: "🏗️",
  Concept: "💡",
  Hobby: "🎨",
}

function ImportanceMeter({ score }: { score: number }) {
  const pct = Math.round(score * 100)
  const color = score >= 0.8 ? "#10b981" : score >= 0.6 ? "#f59e0b" : "#ef4444"
  return (
    <div className="flex items-center gap-1.5">
      <div className="w-16 h-1.5 bg-white/10 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
      <span className="text-[10px] text-slate-400">{pct}%</span>
    </div>
  )
}

function EntityCard({
  entity,
  onPin,
  onDelete,
  onExplain,
}: {
  entity: MemoryEntity
  onPin: (e: MemoryEntity) => void
  onDelete: (e: MemoryEntity) => void
  onExplain: (e: MemoryEntity) => void
}) {
  let attrs: Record<string, any> = {}
  try {
    attrs = JSON.parse(entity.attributes_json ?? "{}")
  } catch {}

  const icon = CATEGORY_ICONS[entity.entity_category] ?? "🧠"
  const badgeCls = LIFECYCLE_COLORS[entity.status] ?? LIFECYCLE_COLORS.active

  return (
    <div
      className={`group relative border rounded-xl p-3.5 flex flex-col gap-2 transition-all duration-200
        ${entity.pinned ? "border-cyan-500/40 bg-cyan-500/5" : "border-border/30 bg-white/[0.02]"}
        hover:border-border/60 hover:bg-white/[0.04]`}
    >
      {/* Pin star indicator */}
      {entity.pinned && (
        <div className="absolute top-2 right-2 text-cyan-400 text-xs">📌</div>
      )}

      <div className="flex items-start gap-2.5">
        <span className="text-xl mt-0.5">{icon}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-semibold text-foreground truncate">{entity.entity_name}</span>
            <span className={`text-[9px] font-mono border px-1.5 py-0.5 rounded ${badgeCls}`}>
              {entity.status.toUpperCase()}
            </span>
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">{entity.entity_category}</div>
          {attrs.details && (
            <p className="text-xs text-slate-400 mt-1 leading-relaxed line-clamp-2">{attrs.details}</p>
          )}
        </div>
      </div>

      <div className="flex items-center justify-between mt-1">
        <div className="flex flex-col gap-0.5">
          <span className="text-[9px] text-slate-500 uppercase tracking-wider">Importance</span>
          <ImportanceMeter score={entity.importance_score} />
        </div>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            id={`pin-memory-${entity.id}`}
            onClick={() => onPin(entity)}
            title={entity.pinned ? "Unpin" : "Pin"}
            className="w-7 h-7 flex items-center justify-center rounded-lg text-sm
              hover:bg-cyan-500/20 hover:text-cyan-300 text-slate-400 transition-colors"
          >
            {entity.pinned ? "🔓" : "📌"}
          </button>
          <button
            id={`explain-memory-${entity.id}`}
            onClick={() => onExplain(entity)}
            title="Inspect explainability"
            className="w-7 h-7 flex items-center justify-center rounded-lg text-sm
              hover:bg-purple-500/20 hover:text-purple-300 text-slate-400 transition-colors"
          >
            🔍
          </button>
          <button
            id={`delete-memory-${entity.id}`}
            onClick={() => onDelete(entity)}
            title="Delete"
            className="w-7 h-7 flex items-center justify-center rounded-lg text-sm
              hover:bg-red-500/20 hover:text-red-400 text-slate-500 transition-colors"
          >
            🗑
          </button>
        </div>
      </div>
    </div>
  )
}

function ExplainabilityInspector({ traces }: { traces: ExplainabilityTrace[] }) {
  if (!traces.length)
    return (
      <div className="text-center py-8 text-slate-500 text-sm">
        No memories matched above the recall threshold.
      </div>
    )

  return (
    <div className="space-y-3">
      {traces.map((t, i) => (
        <div
          key={t.memory_id}
          className="border border-border/30 rounded-xl p-3.5 bg-white/[0.02]"
        >
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono text-slate-500">#{i + 1}</span>
              <span className="text-xs font-semibold text-foreground truncate max-w-[200px]">{t.content}</span>
            </div>
            <div className="text-right">
              <div className="text-base font-bold text-cyan-400">{Math.round(t.final_score * 100)}%</div>
              <div className="text-[9px] text-slate-500">score</div>
            </div>
          </div>

          {/* Score metrics bar */}
          <div className="grid grid-cols-4 gap-2 mb-2.5">
            {[
              { label: "Similarity", val: t.metrics.similarity },
              { label: "Importance", val: t.metrics.importance },
              { label: "Confidence", val: t.metrics.confidence },
              { label: "Recency", val: t.metrics.recency_decay },
            ].map((m) => (
              <div key={m.label} className="flex flex-col gap-0.5">
                <span className="text-[9px] text-slate-500">{m.label}</span>
                <div className="h-1 bg-white/10 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-purple-500"
                    style={{ width: `${Math.round(m.val * 100)}%` }}
                  />
                </div>
                <span className="text-[9px] text-slate-400">{Math.round(m.val * 100)}%</span>
              </div>
            ))}
          </div>

          {/* Explanations */}
          <div className="flex flex-wrap gap-1.5">
            {t.explanations.map((exp, j) => (
              <span
                key={j}
                className={`text-[10px] px-1.5 py-0.5 rounded border font-mono
                  ${exp.startsWith("✓") ? "border-emerald-500/30 text-emerald-400 bg-emerald-500/10" : "border-amber-500/30 text-amber-400 bg-amber-500/10"}`}
              >
                {exp}
              </span>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

export function SemanticMemoryPanel() {
  const [searchQ, setSearchQ] = useState("")
  const [statusFilter, setStatusFilter] = useState<string>("")
  const [explainQuery, setExplainQuery] = useState("")
  const [explainThreshold, setExplainThreshold] = useState(0.40)
  const [traces, setTraces] = useState<ExplainabilityTrace[]>([])
  const [showInspector, setShowInspector] = useState(false)
  const [extractSessionId, setExtractSessionId] = useState("")

  const entitiesQuery = useMemoryEntitiesQuery(
    searchQ || statusFilter
      ? { q: searchQ || undefined, status: statusFilter || undefined }
      : undefined
  )
  const pinMutation = usePinMemoryEntity()
  const deleteMutation = useDeleteMemoryEntity()
  const extractMutation = useTriggerMemoryExtraction()
  const explainMutation = useExplainMemoryRecall()

  const handlePin = (entity: MemoryEntity) => {
    pinMutation.mutate({ entityId: entity.id, pinned: !entity.pinned })
  }

  const handleDelete = (entity: MemoryEntity) => {
    if (confirm(`Delete memory "${entity.entity_name}"?`)) {
      deleteMutation.mutate(entity.id)
    }
  }

  const handleExplainEntity = (entity: MemoryEntity) => {
    setExplainQuery(entity.entity_name)
    setShowInspector(true)
    explainMutation.mutate(
      { query: entity.entity_name, similarity_threshold: 0.1, top_k: 5 },
      { onSuccess: (data) => setTraces(data) }
    )
  }

  const handleExplainSearch = () => {
    if (!explainQuery.trim()) return
    setShowInspector(true)
    explainMutation.mutate(
      { query: explainQuery, similarity_threshold: explainThreshold, top_k: 5 },
      { onSuccess: (data) => setTraces(data) }
    )
  }

  const entities: MemoryEntity[] = entitiesQuery.data ?? []
  const pinned = entities.filter((e) => e.pinned)
  const unpinned = entities.filter((e) => !e.pinned)

  return (
    <div className="flex flex-col h-full gap-4 p-1">
      {/* Top toolbar */}
      <div className="flex flex-wrap items-center gap-2">
        <input
          id="memory-search-input"
          value={searchQ}
          onChange={(e) => setSearchQ(e.target.value)}
          placeholder="Search memories…"
          className="flex-1 min-w-[180px] h-8 px-3 text-xs rounded-lg bg-white/5 border border-border/40 text-foreground placeholder:text-slate-500 focus:outline-none focus:border-cyan-500/50 transition-colors"
        />
        <select
          id="memory-status-filter"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="h-8 px-2 text-xs rounded-lg bg-white/5 border border-border/40 text-foreground focus:outline-none focus:border-cyan-500/50"
        >
          <option value="">All Status</option>
          <option value="candidate">Candidate</option>
          <option value="validated">Validated</option>
          <option value="active">Active</option>
          <option value="compressed">Compressed</option>
          <option value="archived">Archived</option>
        </select>

        <div className="flex items-center gap-1.5 border-l border-border/30 pl-2">
          <input
            id="memory-extract-session-input"
            value={extractSessionId}
            onChange={(e) => setExtractSessionId(e.target.value)}
            placeholder="session_id"
            className="w-32 h-8 px-2 text-xs rounded-lg bg-white/5 border border-border/40 text-foreground placeholder:text-slate-500 focus:outline-none focus:border-cyan-500/50"
          />
          <button
            id="memory-extract-btn"
            disabled={!extractSessionId || extractMutation.isPending}
            onClick={() => extractMutation.mutate(extractSessionId)}
            className="h-8 px-3 text-xs rounded-lg font-medium bg-cyan-500/15 border border-cyan-500/30 text-cyan-300
              hover:bg-cyan-500/25 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            {extractMutation.isPending ? "Extracting…" : "⚡ Extract"}
          </button>
        </div>
      </div>

      {/* Main area: entity list + inspector */}
      <div className="flex flex-1 gap-4 overflow-hidden">
        {/* Entity list column */}
        <div className="flex-1 overflow-y-auto space-y-2 pr-1">
          {entitiesQuery.isLoading && (
            <div className="flex items-center justify-center py-10">
              <div className="w-5 h-5 border-2 border-cyan-400/30 border-t-cyan-400 rounded-full animate-spin" />
            </div>
          )}

          {!entitiesQuery.isLoading && entities.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 gap-3 text-center">
              <span className="text-3xl">🧠</span>
              <p className="text-sm text-slate-500">No memories found.</p>
              <p className="text-xs text-slate-600">
                Start a conversation and use ⚡ Extract to persist important facts.
              </p>
            </div>
          )}

          {pinned.length > 0 && (
            <>
              <div className="text-[10px] font-mono text-slate-500 uppercase tracking-widest px-1">📌 Pinned</div>
              {pinned.map((e) => (
                <EntityCard key={e.id} entity={e} onPin={handlePin} onDelete={handleDelete} onExplain={handleExplainEntity} />
              ))}
              {unpinned.length > 0 && (
                <div className="text-[10px] font-mono text-slate-500 uppercase tracking-widest px-1 mt-2">All Memories</div>
              )}
            </>
          )}
          {unpinned.map((e) => (
            <EntityCard key={e.id} entity={e} onPin={handlePin} onDelete={handleDelete} onExplain={handleExplainEntity} />
          ))}
        </div>

        {/* Explainability inspector sidebar */}
        <div
          className={`w-80 flex-shrink-0 border border-border/30 rounded-xl bg-white/[0.015] flex flex-col overflow-hidden transition-all duration-300
            ${showInspector ? "opacity-100" : "opacity-60"}`}
        >
          <div className="px-3 py-2.5 border-b border-border/20 flex items-center justify-between">
            <span className="text-xs font-semibold text-foreground">🔍 Recall Inspector</span>
            <button
              id="inspector-close-btn"
              onClick={() => setShowInspector(false)}
              className="text-slate-500 hover:text-foreground transition-colors text-sm"
            >
              ✕
            </button>
          </div>

          <div className="p-3 border-b border-border/20 space-y-2">
            <input
              id="explain-query-input"
              value={explainQuery}
              onChange={(e) => setExplainQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleExplainSearch()}
              placeholder="Recall query…"
              className="w-full h-8 px-3 text-xs rounded-lg bg-white/5 border border-border/40 text-foreground placeholder:text-slate-500 focus:outline-none focus:border-purple-500/50"
            />
            <div className="flex items-center gap-2">
              <label className="text-[10px] text-slate-500 whitespace-nowrap">Threshold</label>
              <input
                id="explain-threshold-slider"
                type="range"
                min={0}
                max={1}
                step={0.05}
                value={explainThreshold}
                onChange={(e) => setExplainThreshold(Number(e.target.value))}
                className="flex-1 accent-purple-500"
              />
              <span className="text-[10px] text-slate-400 w-6">{explainThreshold.toFixed(2)}</span>
            </div>
            <button
              id="explain-search-btn"
              onClick={handleExplainSearch}
              disabled={!explainQuery.trim() || explainMutation.isPending}
              className="w-full h-8 text-xs font-medium rounded-lg bg-purple-500/15 border border-purple-500/30 text-purple-300
                hover:bg-purple-500/25 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              {explainMutation.isPending ? "Recalling…" : "Run Recall"}
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-3">
            {explainMutation.isPending ? (
              <div className="flex items-center justify-center py-8">
                <div className="w-5 h-5 border-2 border-purple-400/30 border-t-purple-400 rounded-full animate-spin" />
              </div>
            ) : (
              <ExplainabilityInspector traces={traces} />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
