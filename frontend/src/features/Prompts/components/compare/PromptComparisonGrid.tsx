import { useState } from "react"
import { Columns, Play, Clock, DollarSign, Award } from "lucide-react"
import { usePromptStudioStore } from "../../store/usePromptStudioStore"
import { comparePromptsApi } from "../../services/promptsApi"
import type { PromptExecution } from "../../types/prompts.types"

export function PromptComparisonGrid() {
  const systemPromptDraft = usePromptStudioStore((s) => s.systemPromptDraft)
  const userPromptDraft = usePromptStudioStore((s) => s.userPromptDraft)
  const parsedVariables = usePromptStudioStore((s) => s.parsedVariables)

  const [comparisons, setComparisons] = useState<PromptExecution[]>([])
  const [isComparing, setIsComparing] = useState(false)
  const [winnerModel, setWinnerModel] = useState<string | null>(null)

  const handleRunComparison = async () => {
    setIsComparing(true)
    try {
      const res = await comparePromptsApi({
        system_prompt: systemPromptDraft,
        user_prompt: userPromptDraft,
        variables: parsedVariables,
        models: ["gpt-4o", "claude-3.5-sonnet", "gemini-1.5-pro"],
      })
      setComparisons(res.comparisons)
    } catch (err: any) {
      console.error(err)
    } finally {
      setIsComparing(false)
    }
  }

  return (
    <div className="space-y-4 bg-secondary/15 border border-border/40 rounded-xl p-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border/40 pb-3">
        <div className="flex items-center gap-2">
          <Columns className="h-4 w-4 text-cyan-400" />
          <h3 className="text-xs font-bold text-foreground">Multi-Model Parallel A/B/C Benchmark Comparison</h3>
        </div>

        <button
          onClick={handleRunComparison}
          disabled={isComparing}
          className="inline-flex items-center gap-1.5 px-4 py-1.5 text-xs font-bold bg-cyan-500 hover:bg-cyan-400 text-black rounded-lg cursor-pointer transition-all shadow-md disabled:opacity-50"
        >
          <Play className="h-3.5 w-3.5 fill-current" />
          {isComparing ? "Benchmarking Models..." : "Run Parallel Benchmark"}
        </button>
      </div>

      {comparisons.length === 0 ? (
        <div className="p-8 text-center text-xs text-muted-foreground italic bg-secondary/10 border border-dashed border-border/40 rounded-xl">
          Click "Run Parallel Benchmark" to execute Prompt A/B/C across GPT-4o, Claude 3.5, and Gemini 1.5.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {comparisons.map((c) => {
            const isWinner = winnerModel === c.model_used
            return (
              <div
                key={c.model_used}
                className={`p-4 rounded-xl border transition-all space-y-3 font-mono text-xs ${
                  isWinner
                    ? "bg-emerald-500/10 border-emerald-500/50 ring-1 ring-emerald-500/30"
                    : "bg-[#0D1117] border-border/40"
                }`}
              >
                <div className="flex items-center justify-between border-b border-border/40 pb-2">
                  <span className="font-bold text-cyan-400 capitalize">{c.model_used}</span>
                  {isWinner && (
                    <span className="px-2 py-0.5 text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 rounded flex items-center gap-1">
                      <Award className="h-3 w-3" /> Winner Choice
                    </span>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-2 text-[10px] bg-secondary/20 p-2 rounded border border-border/30">
                  <span className="flex items-center gap-1 text-muted-foreground">
                    <Clock className="h-3 w-3 text-cyan-400" />
                    Latency: <strong className="text-foreground">{c.latency_ms.toFixed(1)}ms</strong>
                  </span>
                  <span className="flex items-center gap-1 text-muted-foreground">
                    <DollarSign className="h-3 w-3 text-emerald-400" />
                    Cost: <strong className="text-foreground">${c.total_cost.toFixed(4)}</strong>
                  </span>
                </div>

                <div className="p-2.5 bg-secondary/10 rounded border border-border/30 text-[#C9D1D9] text-[11px] whitespace-pre-wrap leading-relaxed max-h-50 overflow-y-auto scrollbar-thin">
                  {c.raw_output}
                </div>

                <button
                  onClick={() => setWinnerModel(c.model_used)}
                  className={`w-full py-1.5 text-xs font-bold rounded-lg cursor-pointer transition-all ${
                    isWinner
                      ? "bg-emerald-500 text-black shadow-md"
                      : "bg-secondary/40 hover:bg-secondary/70 text-muted-foreground hover:text-foreground border border-border/40"
                  }`}
                >
                  {isWinner ? "Selected as Active Winner" : "Mark as Winner"}
                </button>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
