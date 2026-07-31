import { useState, useEffect } from "react"
import { Code, GitCommit, Sparkles, DollarSign, Clock, Hash } from "lucide-react"
import { usePromptStudioStore } from "../../store/usePromptStudioStore"
import { usePromptDetailsQuery, commitVersionApi, parseVariablesApi } from "../../services/promptsApi"

export function MonacoPromptEditor() {
  const selectedPromptId = usePromptStudioStore((s) => s.selectedPromptId)
  const systemPromptDraft = usePromptStudioStore((s) => s.systemPromptDraft)
  const userPromptDraft = usePromptStudioStore((s) => s.userPromptDraft)
  const setDraftContent = usePromptStudioStore((s) => s.setDraftContent)
  const updateVariableValue = usePromptStudioStore((s) => s.updateVariableValue)
  const setAiAssistModalOpen = usePromptStudioStore((s) => s.setAiAssistModalOpen)
  const setActiveTab = usePromptStudioStore((s) => s.setActiveTab)

  const { data: details, refetch } = usePromptDetailsQuery(selectedPromptId)

  const [commitMsg, setCommitMsg] = useState("")
  const [isCommitting, setIsCommitting] = useState(false)
  const [saveStatus, setSaveStatus] = useState<string | null>(null)

  useEffect(() => {
    if (details?.current_version) {
      setDraftContent(details.current_version.system_prompt, details.current_version.user_prompt)
    }
  }, [details, setDraftContent])

  // Extract variables on prompt edit
  useEffect(() => {
    const text = systemPromptDraft + " " + userPromptDraft
    parseVariablesApi(text).then((res) => {
      res.variables.forEach((v) => {
        updateVariableValue(v, "")
      })
    })
  }, [systemPromptDraft, userPromptDraft, updateVariableValue])

  const totalTokens = (systemPromptDraft.split(/\s+/).length + userPromptDraft.split(/\s+/).length) * 1.3
  const estimatedCost = (totalTokens * 0.00001).toFixed(4)
  const estimatedLatency = (120 + totalTokens * 0.5).toFixed(0)

  const handleCommit = async () => {
    if (!selectedPromptId) return
    setIsCommitting(true)
    try {
      await commitVersionApi(selectedPromptId, {
        system_prompt: systemPromptDraft,
        user_prompt: userPromptDraft,
        commit_message: commitMsg || "Update prompt template",
        model: "gpt-4o",
        temperature: 0.7,
        top_p: 0.95,
        max_tokens: 2048,
      })
      setSaveStatus("Committed successfully!")
      refetch()
      setTimeout(() => setSaveStatus(null), 2500)
    } catch (err: any) {
      setSaveStatus(`Commit failed: ${err.message}`)
    } finally {
      setIsCommitting(false)
    }
  }

  return (
    <div className="space-y-4 bg-secondary/15 border border-border/40 rounded-xl p-4">
      {/* Editor Header Toolbar */}
      <div className="flex items-center justify-between border-b border-border/40 pb-3">
        <div className="flex items-center gap-2">
          <Code className="h-4 w-4 text-cyan-400" />
          <h3 className="text-xs font-bold text-foreground">
            Monaco Prompt Editor: {details?.prompt.title || "New Draft"}
          </h3>
          {saveStatus && <span className="text-[11px] text-emerald-400 font-mono font-semibold">{saveStatus}</span>}
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setAiAssistModalOpen(true)}
            className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-semibold bg-violet-500/20 hover:bg-violet-500/30 text-violet-300 border border-violet-500/40 rounded-lg cursor-pointer transition-all"
          >
            <Sparkles className="h-3.5 w-3.5" />
            AI Optimize
          </button>

          <button
            onClick={handleCommit}
            disabled={isCommitting || !selectedPromptId}
            className="inline-flex items-center gap-1 px-3 py-1 text-xs font-bold bg-cyan-500 hover:bg-cyan-400 text-black rounded-lg cursor-pointer transition-all shadow-md disabled:opacity-50"
          >
            <GitCommit className="h-3.5 w-3.5" />
            {isCommitting ? "Committing..." : "Save Version"}
          </button>
        </div>
      </div>

      {/* Editor Metadata Metrics Strip */}
      <div className="flex flex-wrap items-center gap-4 text-xs font-mono text-muted-foreground p-2 bg-[#0D1117] border border-border/40 rounded-lg">
        <span className="flex items-center gap-1 text-foreground">
          <Hash className="h-3 w-3 text-cyan-400" />
          Tokens: <strong className="text-cyan-400">{Math.round(totalTokens)}</strong>
        </span>
        <span className="flex items-center gap-1 text-foreground">
          <DollarSign className="h-3 w-3 text-emerald-400" />
          Est. Cost: <strong className="text-emerald-400">${estimatedCost}</strong>
        </span>
        <span className="flex items-center gap-1 text-foreground">
          <Clock className="h-3 w-3 text-violet-400" />
          Est. Latency: <strong className="text-violet-400">{estimatedLatency}ms</strong>
        </span>
      </div>

      {/* System Prompt Input */}
      <div className="space-y-1.5">
        <label className="text-xs font-mono font-bold text-foreground flex items-center justify-between">
          <span>System Prompt Guidelines</span>
          <span className="text-[10px] text-muted-foreground font-normal">Behavioral Rules</span>
        </label>
        <textarea
          rows={3}
          value={systemPromptDraft}
          onChange={(e) => setDraftContent(e.target.value, userPromptDraft)}
          placeholder="System role guidelines (e.g. You are an expert DB administrator...)"
          className="w-full p-3 text-xs font-mono bg-[#0D1117] border border-border/50 rounded-lg text-[#C9D1D9] focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 transition-all leading-relaxed"
        />
      </div>

      {/* User Prompt Input with Monaco Highlighting aesthetics */}
      <div className="space-y-1.5">
        <label className="text-xs font-mono font-bold text-foreground flex items-center justify-between">
          <span>User Prompt Template</span>
          <span className="text-[10px] text-cyan-400 font-mono">{"Variables syntax: {{variable_name}}"}</span>
        </label>
        <textarea
          rows={6}
          value={userPromptDraft}
          onChange={(e) => setDraftContent(systemPromptDraft, e.target.value)}
          placeholder="User prompt template (e.g. Write a query for {{metrics}} from {{table_name}}...)"
          className="w-full p-3 text-xs font-mono bg-[#0D1117] border border-border/50 rounded-lg text-[#C9D1D9] focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 transition-all leading-relaxed"
        />
      </div>

      {/* Commit Note Input */}
      <div className="flex items-center gap-2 pt-2 border-t border-border/40">
        <input
          type="text"
          value={commitMsg}
          onChange={(e) => setCommitMsg(e.target.value)}
          placeholder="Commit message (e.g. Added {{table_name}} parameter)"
          className="flex-1 px-3 py-1.5 text-xs bg-secondary/30 border border-border/50 rounded-lg text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
        />
        <button
          onClick={() => setActiveTab("playground")}
          className="px-3 py-1.5 text-xs font-bold bg-violet-500/20 hover:bg-violet-500/30 text-violet-300 border border-violet-500/40 rounded-lg cursor-pointer transition-all whitespace-nowrap"
        >
          Test in Playground →
        </button>
      </div>
    </div>
  )
}
