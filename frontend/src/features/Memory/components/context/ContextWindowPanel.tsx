// frontend/src/features/Memory/components/context/ContextWindowPanel.tsx

import { useState } from "react"
import { PieChart, Minimize2, Code, CheckCircle } from "lucide-react"
import { useContextWindowQuery, compressMemoryApi } from "../../services/memoryApi"
import { useMemoryStudioStore } from "../../store/useMemoryStudioStore"
import { useQueryClient } from "@tanstack/react-query"
import { queryKeys } from "@/services/queries/queryKeys"

export function ContextWindowPanel() {
  const queryClient = useQueryClient()
  const selectedSessionId = useMemoryStudioStore((s) => s.selectedSessionId)
  const { data: contextData } = useContextWindowQuery(selectedSessionId)

  const [compressStatus, setCompressStatus] = useState<string | null>(null)
  const [isCompressing, setIsCompressing] = useState(false)

  const breakdown = contextData?.breakdown || {
    system_prompt: 1024,
    conversation_history: 2048,
    recalled_long_term: 1024,
    working_buffer: 512,
    headroom: 3584,
  }

  const maxTokens = contextData?.max_tokens || 8192
  const usedTokens = contextData?.used_tokens || 4608
  const usedPct = Math.round((usedTokens / maxTokens) * 100)

  const handleCompress = async () => {
    setIsCompressing(true)
    setCompressStatus(null)
    try {
      const res = await compressMemoryApi({ session_id: selectedSessionId, strategy: "summarize" })
      queryClient.invalidateQueries({ queryKey: queryKeys.memory.all() })
      setCompressStatus(`Compressed! Saved ${res.tokens_saved} tokens.`)
    } catch (err: unknown) {
      setCompressStatus(err instanceof Error ? err.message : "Compression failed")
    } finally {
      setIsCompressing(false)
    }
  }

  return (
    <div className="space-y-4 bg-secondary/15 border border-border/40 rounded-xl p-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border/40 pb-3">
        <div className="flex items-center gap-2">
          <PieChart className="h-4 w-4 text-cyan-400" />
          <h3 className="text-xs font-bold text-foreground">Token Window Budget & Assembled Prompt Preview</h3>
        </div>
        <button
          onClick={handleCompress}
          disabled={isCompressing}
          className="flex items-center gap-1.5 px-3 py-1 text-xs font-bold font-mono rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 hover:bg-cyan-500/30 cursor-pointer transition-all disabled:opacity-50"
        >
          <Minimize2 className="h-3.5 w-3.5" />
          {isCompressing ? "Compressing..." : "Trigger Memory Compression"}
        </button>
      </div>

      {/* Compression Status Notification */}
      {compressStatus && (
        <div className="p-2.5 bg-cyan-500/10 border border-cyan-500/30 rounded-lg flex items-center gap-2 text-xs font-mono text-cyan-300">
          <CheckCircle className="h-3.5 w-3.5 shrink-0" />
          <span>{compressStatus}</span>
        </div>
      )}

      {/* Token Saturation Progress Meter */}
      <div className="space-y-2 font-mono text-xs bg-secondary/20 p-4 rounded-xl border border-border/30">
        <div className="flex justify-between items-center">
          <span className="text-[10px] text-muted-foreground uppercase font-bold">Context Window Saturation</span>
          <span className="text-cyan-400 font-bold">{usedTokens} / {maxTokens} tokens ({usedPct}%)</span>
        </div>
        <div className="w-full h-3 bg-secondary/40 rounded-full overflow-hidden flex border border-border/30">
          <div style={{ width: `${(breakdown.system_prompt / maxTokens) * 100}%` }} className="bg-cyan-500" title="System Prompt" />
          <div style={{ width: `${(breakdown.conversation_history / maxTokens) * 100}%` }} className="bg-violet-500" title="Conversation History" />
          <div style={{ width: `${(breakdown.recalled_long_term / maxTokens) * 100}%` }} className="bg-rose-500" title="Recalled LTM" />
          <div style={{ width: `${(breakdown.working_buffer / maxTokens) * 100}%` }} className="bg-amber-500" title="Working Buffer" />
        </div>

        {/* Legend */}
        <div className="flex flex-wrap items-center gap-4 text-[10px] pt-1 text-muted-foreground">
          <div className="flex items-center gap-1.5"><div className="h-2 w-2 rounded-full bg-cyan-500" /><span>System ({breakdown.system_prompt}t)</span></div>
          <div className="flex items-center gap-1.5"><div className="h-2 w-2 rounded-full bg-violet-500" /><span>Conversation ({breakdown.conversation_history}t)</span></div>
          <div className="flex items-center gap-1.5"><div className="h-2 w-2 rounded-full bg-rose-500" /><span>Long-Term ({breakdown.recalled_long_term}t)</span></div>
          <div className="flex items-center gap-1.5"><div className="h-2 w-2 rounded-full bg-amber-500" /><span>Working ({breakdown.working_buffer}t)</span></div>
        </div>
      </div>

      {/* Prompt Assembly Viewer */}
      <div className="space-y-1.5 font-mono text-xs">
        <div className="flex items-center gap-2">
          <Code className="h-3.5 w-3.5 text-violet-400" />
          <span className="text-[10px] text-muted-foreground uppercase font-bold">Assembled LLM Prompt Payload</span>
        </div>
        <pre className="p-4 bg-[#0D1117] border border-border/40 rounded-xl text-cyan-300 text-[11px] leading-relaxed overflow-x-auto whitespace-pre-wrap">
          {contextData?.assembled_prompt || "<system>You are Jarvis AIOS core agent runtime.</system>\n<memory_context>[Semantic] User active session default</memory_context>"}
        </pre>
      </div>
    </div>
  )
}
