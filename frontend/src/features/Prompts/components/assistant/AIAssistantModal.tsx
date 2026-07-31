import { useState } from "react"
import { Sparkles, X, Check, Wand2 } from "lucide-react"
import { usePromptStudioStore } from "../../store/usePromptStudioStore"
import { aiAssistApi } from "../../services/promptsApi"

export function AIAssistantModal() {
  const aiAssistModalOpen = usePromptStudioStore((s) => s.aiAssistModalOpen)
  const setAiAssistModalOpen = usePromptStudioStore((s) => s.setAiAssistModalOpen)
  const userPromptDraft = usePromptStudioStore((s) => s.userPromptDraft)
  const systemPromptDraft = usePromptStudioStore((s) => s.systemPromptDraft)
  const setDraftContent = usePromptStudioStore((s) => s.setDraftContent)

  const [action, setAction] = useState<"IMPROVE" | "OPTIMIZE" | "FORMAT">("IMPROVE")
  const [suggestedText, setSuggestedText] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)

  if (!aiAssistModalOpen) return null

  const handleRunAiAssist = async () => {
    setIsProcessing(true)
    try {
      const res = await aiAssistApi(userPromptDraft, action)
      setSuggestedText(res.suggested_text)
    } catch (err: any) {
      console.error(err)
    } finally {
      setIsProcessing(false)
    }
  }

  const handleApply = () => {
    if (suggestedText) {
      setDraftContent(systemPromptDraft, suggestedText)
      setAiAssistModalOpen(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in zoom-in-95 duration-150">
      <div className="bg-[#121826] border border-violet-500/40 rounded-xl w-full max-w-xl shadow-2xl overflow-hidden space-y-4 p-4 font-mono text-xs">
        <div className="flex items-center justify-between border-b border-border/40 pb-3">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-violet-400" />
            <h3 className="text-sm font-bold text-foreground">AI Prompt Optimization Assistant</h3>
          </div>
          <button onClick={() => setAiAssistModalOpen(false)} className="p-1 text-muted-foreground hover:text-foreground cursor-pointer">
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="flex items-center gap-2">
          {(["IMPROVE", "OPTIMIZE", "FORMAT"] as const).map((act) => (
            <button
              key={act}
              onClick={() => setAction(act)}
              className={`px-3 py-1 text-xs font-semibold rounded-lg cursor-pointer transition-all ${
                action === act
                  ? "bg-violet-500/20 text-violet-300 border border-violet-500/40"
                  : "bg-secondary/30 text-muted-foreground border border-border/40"
              }`}
            >
              {act}
            </button>
          ))}

          <button
            onClick={handleRunAiAssist}
            disabled={isProcessing}
            className="ml-auto inline-flex items-center gap-1 px-3 py-1 text-xs font-bold bg-violet-500 hover:bg-violet-400 text-black rounded-lg cursor-pointer transition-all shadow-md disabled:opacity-50"
          >
            <Wand2 className="h-3.5 w-3.5" />
            {isProcessing ? "Processing..." : "Generate Proposal"}
          </button>
        </div>

        <div className="space-y-2">
          <span className="text-[10px] text-muted-foreground uppercase">Original Draft</span>
          <div className="p-2.5 bg-[#0D1117] border border-border/40 rounded-lg text-muted-foreground text-[11px] whitespace-pre-wrap max-h-30 overflow-y-auto scrollbar-thin">
            {userPromptDraft}
          </div>
        </div>

        {suggestedText && (
          <div className="space-y-2">
            <span className="text-[10px] text-violet-400 uppercase font-bold">AI Proposed Optimization (Requires Human Approval)</span>
            <div className="p-3 bg-[#0D1117] border border-violet-500/40 rounded-lg text-foreground text-[11px] whitespace-pre-wrap leading-relaxed max-h-45 overflow-y-auto scrollbar-thin">
              {suggestedText}
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-border/40">
              <button
                onClick={() => setAiAssistModalOpen(false)}
                className="px-3 py-1.5 text-xs text-muted-foreground hover:text-foreground bg-secondary/30 rounded-lg cursor-pointer"
              >
                Reject Proposal
              </button>
              <button
                onClick={handleApply}
                className="inline-flex items-center gap-1 px-4 py-1.5 text-xs font-bold bg-emerald-500 hover:bg-emerald-400 text-black rounded-lg cursor-pointer shadow-md"
              >
                <Check className="h-3.5 w-3.5" />
                Approve & Apply to Draft
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
