import { useState } from "react"
import { GitCommit, RotateCcw, Clock } from "lucide-react"
import { usePromptStudioStore } from "../../store/usePromptStudioStore"
import { usePromptVersionsQuery, restoreVersionApi } from "../../services/promptsApi"
import type { PromptVersion } from "../../types/prompts.types"

export function VersionDiffViewer() {
  const selectedPromptId = usePromptStudioStore((s) => s.selectedPromptId)
  const setDraftContent = usePromptStudioStore((s) => s.setDraftContent)

  const { data: versions = [], refetch } = usePromptVersionsQuery(selectedPromptId)
  const [selectedVerId, setSelectedVerId] = useState<string | null>(null)
  const [statusMsg, setStatusMsg] = useState<string | null>(null)

  const currentHead = versions[0]
  const targetVer: PromptVersion | undefined = versions.find((v) => v.id === selectedVerId) || versions[1] || currentHead

  const handleRestore = async (versionId: string) => {
    if (!selectedPromptId) return
    try {
      const restored = await restoreVersionApi(selectedPromptId, versionId)
      setDraftContent(restored.system_prompt, restored.user_prompt)
      setStatusMsg(`Restored ${restored.version_tag} as active draft.`)
      refetch()
      setTimeout(() => setStatusMsg(null), 2500)
    } catch (err: any) {
      setStatusMsg(`Restore failed: ${err.message}`)
    }
  }

  return (
    <div className="space-y-4 bg-secondary/15 border border-border/40 rounded-xl p-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border/40 pb-3">
        <div className="flex items-center gap-2">
          <GitCommit className="h-4 w-4 text-cyan-400" />
          <h3 className="text-xs font-bold text-foreground">Git-Style Version Timeline & Diff Viewer ({versions.length})</h3>
        </div>
        {statusMsg && <span className="text-xs font-mono text-emerald-400 font-semibold">{statusMsg}</span>}
      </div>

      {versions.length === 0 ? (
        <div className="p-6 text-center text-xs text-muted-foreground italic bg-secondary/10 rounded-lg">
          No version history available for this prompt.
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          {/* Commit List Timeline (Left Column) */}
          <div className="lg:col-span-4 space-y-2 max-h-100 overflow-y-auto scrollbar-thin">
            {versions.map((ver, idx) => {
              const isHead = idx === 0
              const isSelected = targetVer?.id === ver.id
              return (
                <div
                  key={ver.id}
                  onClick={() => setSelectedVerId(ver.id)}
                  className={`p-3 rounded-lg border transition-all cursor-pointer space-y-1 ${
                    isSelected
                      ? "bg-cyan-500/10 border-cyan-500/50 shadow-sm"
                      : "bg-secondary/20 border-border/40 hover:bg-secondary/40"
                  }`}
                >
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="font-bold text-cyan-400 flex items-center gap-1">
                      <GitCommit className="h-3 w-3" />
                      {ver.version_tag}
                    </span>
                    {isHead && (
                      <span className="px-1.5 py-0.2 text-[9px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded">
                        Active Head
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] text-foreground font-medium line-clamp-1">{ver.commit_message}</p>
                  <div className="flex items-center gap-2 text-[10px] font-mono text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Clock className="h-2.5 w-2.5" />
                      {new Date(ver.created_at).toLocaleTimeString()}
                    </span>
                    <span>• {ver.author}</span>
                  </div>
                </div>
              )
            })}
          </div>

          {/* Side-by-Side Diff Comparison View (Right Column) */}
          <div className="lg:col-span-8 space-y-3 font-mono text-xs">
            <div className="flex items-center justify-between bg-secondary/30 p-2 rounded border border-border/40 text-[11px]">
              <span className="text-muted-foreground">
                Comparing <strong className="text-foreground">{currentHead?.version_tag} (Head)</strong> vs{" "}
                <strong className="text-cyan-400">{targetVer?.version_tag}</strong>
              </span>

              {targetVer && targetVer.id !== currentHead?.id && (
                <button
                  onClick={() => handleRestore(targetVer.id)}
                  className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-bold bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 rounded cursor-pointer transition-all"
                >
                  <RotateCcw className="h-3 w-3" />
                  Restore {targetVer.version_tag}
                </button>
              )}
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div className="space-y-1">
                <span className="text-[10px] text-muted-foreground uppercase">Active Head ({currentHead?.version_tag})</span>
                <div className="p-3 bg-[#0D1117] border border-border/40 rounded-lg text-[#C9D1D9] text-[11px] whitespace-pre-wrap leading-relaxed max-h-75 overflow-y-auto scrollbar-thin">
                  {currentHead?.user_prompt}
                </div>
              </div>

              <div className="space-y-1">
                <span className="text-[10px] text-cyan-400 uppercase">Target Commit ({targetVer?.version_tag})</span>
                <div className="p-3 bg-[#0D1117] border border-cyan-500/30 rounded-lg text-[#C9D1D9] text-[11px] whitespace-pre-wrap leading-relaxed max-h-75 overflow-y-auto scrollbar-thin">
                  {targetVer?.user_prompt}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
