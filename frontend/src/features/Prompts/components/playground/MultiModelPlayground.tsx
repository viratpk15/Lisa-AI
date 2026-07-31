import { useState } from "react"
import { Play, Zap, Sliders, Clock, DollarSign, Hash, CheckCircle2 } from "lucide-react"
import { usePromptStudioStore } from "../../store/usePromptStudioStore"
import { runPlaygroundApi } from "../../services/promptsApi"
import type { PromptExecution } from "../../types/prompts.types"

export function MultiModelPlayground() {
  const selectedPromptId = usePromptStudioStore((s) => s.selectedPromptId)
  const systemPromptDraft = usePromptStudioStore((s) => s.systemPromptDraft)
  const userPromptDraft = usePromptStudioStore((s) => s.userPromptDraft)
  const parsedVariables = usePromptStudioStore((s) => s.parsedVariables)
  const selectedModels = usePromptStudioStore((s) => s.selectedModels)
  const setSelectedModels = usePromptStudioStore((s) => s.setSelectedModels)
  const temperature = usePromptStudioStore((s) => s.temperature)
  const setTemperature = usePromptStudioStore((s) => s.setTemperature)
  const isExecuting = usePromptStudioStore((s) => s.isExecuting)
  const setIsExecuting = usePromptStudioStore((s) => s.setIsExecuting)

  const [results, setResults] = useState<PromptExecution[]>([])

  const availableModels = [
    { id: "gpt-4o", name: "GPT-4o (OpenAI)" },
    { id: "claude-3.5-sonnet", name: "Claude 3.5 Sonnet (Anthropic)" },
    { id: "gemini-1.5-pro", name: "Gemini 1.5 Pro (Google)" },
  ]

  const handleRunPlayground = async () => {
    setIsExecuting(true)
    const newResults: PromptExecution[] = []

    for (const model of selectedModels) {
      try {
        const exec = await runPlaygroundApi({
          prompt_id: selectedPromptId,
          system_prompt: systemPromptDraft,
          user_prompt: userPromptDraft,
          variables: parsedVariables,
          model,
          temperature,
        })
        newResults.push(exec)
      } catch (err: any) {
        newResults.push({
          id: `err_${Date.now()}`,
          prompt_id: selectedPromptId || "adhoc",
          model_used: model,
          input_variables: parsedVariables,
          raw_output: `Execution Failed: ${err.message}`,
          latency_ms: 0,
          prompt_tokens: 0,
          completion_tokens: 0,
          total_cost: 0,
          status: "ERROR",
          executed_at: new Date().toISOString(),
        })
      }
    }

    setResults(newResults)
    setIsExecuting(false)
  }

  return (
    <div className="space-y-4 bg-secondary/15 border border-border/40 rounded-xl p-4">
      {/* Playground Controls Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border/40 pb-3">
        <div className="flex items-center gap-2">
          <Play className="h-4 w-4 text-cyan-400" />
          <h3 className="text-xs font-bold text-foreground">Multi-Model Playground Experimentation</h3>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleRunPlayground}
            disabled={isExecuting || selectedModels.length === 0}
            className="inline-flex items-center gap-1.5 px-4 py-1.5 text-xs font-bold bg-cyan-500 hover:bg-cyan-400 text-black rounded-lg cursor-pointer transition-all shadow-md disabled:opacity-50"
          >
            <Zap className="h-3.5 w-3.5 fill-current" />
            {isExecuting ? "Executing Models..." : "Run Playground (⌘Enter)"}
          </button>
        </div>
      </div>

      {/* Parameter Controls Bar */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 p-3 bg-secondary/20 border border-border/40 rounded-lg text-xs font-mono">
        <div className="space-y-1">
          <label className="text-[10px] text-muted-foreground uppercase flex items-center gap-1">
            <Sliders className="h-3 w-3 text-cyan-400" />
            Model Selection
          </label>
          <div className="flex flex-wrap gap-1">
            {availableModels.map((m) => {
              const isSelected = selectedModels.includes(m.id)
              return (
                <button
                  key={m.id}
                  onClick={() => {
                    if (isSelected) {
                      setSelectedModels(selectedModels.filter((id) => id !== m.id))
                    } else {
                      setSelectedModels([...selectedModels, m.id])
                    }
                  }}
                  className={`px-2 py-0.5 text-[10px] rounded border cursor-pointer transition-all ${
                    isSelected
                      ? "bg-cyan-500/20 text-cyan-300 border-cyan-500/40 font-bold"
                      : "bg-secondary/40 text-muted-foreground border-border/40"
                  }`}
                >
                  {m.name}
                </button>
              )
            })}
          </div>
        </div>

        <div className="space-y-1">
          <div className="flex items-center justify-between text-[10px] text-muted-foreground uppercase">
            <span>Temperature: {temperature}</span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={temperature}
            onChange={(e) => setTemperature(Number(e.target.value))}
            className="w-full h-1.5 bg-secondary/60 rounded-lg appearance-none cursor-pointer accent-cyan-500"
          />
        </div>

        <div className="space-y-1 text-right">
          <span className="text-[10px] text-muted-foreground uppercase">Selected Models</span>
          <div className="font-bold text-cyan-400">{selectedModels.length} Active</div>
        </div>
      </div>

      {/* Execution Results Grid */}
      {results.length === 0 ? (
        <div className="p-8 text-center text-xs text-muted-foreground italic bg-secondary/10 border border-dashed border-border/40 rounded-xl">
          Click "Run Playground" above to execute model completions in parallel.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {results.map((res, idx) => (
            <div key={`${res.model_used}_${idx}`} className="p-3 bg-[#0D1117] border border-border/40 rounded-xl space-y-2 font-mono text-xs">
              <div className="flex items-center justify-between border-b border-border/40 pb-2">
                <span className="font-bold text-cyan-400 capitalize">{res.model_used}</span>
                <span className="text-[10px] text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 className="h-3 w-3" />
                  {res.status}
                </span>
              </div>

              <div className="flex items-center justify-between text-[10px] text-muted-foreground border-b border-border/30 pb-1">
                <span className="flex items-center gap-1">
                  <Clock className="h-3 w-3 text-violet-400" />
                  {res.latency_ms.toFixed(1)}ms
                </span>
                <span className="flex items-center gap-1">
                  <Hash className="h-3 w-3 text-cyan-400" />
                  {res.prompt_tokens + res.completion_tokens} tok
                </span>
                <span className="flex items-center gap-1">
                  <DollarSign className="h-3 w-3 text-emerald-400" />
                  ${res.total_cost.toFixed(4)}
                </span>
              </div>

              <div className="p-2 bg-secondary/20 rounded border border-border/30 text-[#C9D1D9] text-[11px] whitespace-pre-wrap leading-relaxed max-h-55 overflow-y-auto scrollbar-thin">
                {res.raw_output}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
