// frontend/src/features/Models/components/cost/CostCalculatorPanel.tsx

import { useState } from "react"
import { DollarSign, Calculator } from "lucide-react"
import { useModelStudioStore } from "../../store/useModelStudioStore"
import { useModelRegistryQuery, estimateCostApi } from "../../services/modelsApi"
import type { CostEstimate } from "../../types/models.types"

export function CostCalculatorPanel() {
  const selectedModelId = useModelStudioStore((s) => s.selectedModelId)
  const setSelectedModelId = useModelStudioStore((s) => s.setSelectedModelId)
  const promptTokens = useModelStudioStore((s) => s.costPromptTokens)
  const setPromptTokens = useModelStudioStore((s) => s.setCostPromptTokens)
  const completionTokens = useModelStudioStore((s) => s.costCompletionTokens)
  const setCompletionTokens = useModelStudioStore((s) => s.setCostCompletionTokens)
  const monthlyRequests = useModelStudioStore((s) => s.costMonthlyRequests)
  const setMonthlyRequests = useModelStudioStore((s) => s.setCostMonthlyRequests)

  const { data: models = [] } = useModelRegistryQuery()
  const [costResult, setCostResult] = useState<CostEstimate | null>(null)

  const handleCalculate = async () => {
    try {
      const res = await estimateCostApi({
        model_id: selectedModelId,
        prompt_tokens: promptTokens,
        completion_tokens: completionTokens,
        monthly_requests: monthlyRequests,
      })
      setCostResult(res)
    } catch {
      // Handled silently
    }
  }

  return (
    <div className="space-y-4 bg-secondary/15 border border-border/40 rounded-xl p-4 font-mono text-xs">
      <div className="flex items-center justify-between border-b border-border/40 pb-3">
        <div className="flex items-center gap-2">
          <DollarSign className="h-4 w-4 text-emerald-400" />
          <h3 className="text-xs font-bold text-foreground">Multi-Model Token Cost Calculator</h3>
        </div>
        <button
          onClick={handleCalculate}
          className="px-3 py-1.5 font-bold rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 hover:bg-emerald-500/30 cursor-pointer transition-all"
        >
          Calculate Expenditure
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label className="text-[10px] text-muted-foreground block mb-1">Target LLM</label>
          <select
            value={selectedModelId}
            onChange={(e) => setSelectedModelId(e.target.value)}
            className="w-full p-2 bg-secondary/30 border border-border/40 rounded text-foreground text-xs"
          >
            {models.map((m) => (
              <option key={m.id} value={m.model_id}>{m.display_name}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="text-[10px] text-muted-foreground block mb-1">Input Tokens / Req</label>
          <input
            type="number"
            value={promptTokens}
            onChange={(e) => setPromptTokens(Number(e.target.value))}
            className="w-full p-2 bg-secondary/30 border border-border/40 rounded text-foreground text-xs"
          />
        </div>

        <div>
          <label className="text-[10px] text-muted-foreground block mb-1">Output Tokens / Req</label>
          <input
            type="number"
            value={completionTokens}
            onChange={(e) => setCompletionTokens(Number(e.target.value))}
            className="w-full p-2 bg-secondary/30 border border-border/40 rounded text-foreground text-xs"
          />
        </div>

        <div>
          <label className="text-[10px] text-muted-foreground block mb-1">Est. Monthly Requests</label>
          <input
            type="number"
            value={monthlyRequests}
            onChange={(e) => setMonthlyRequests(Number(e.target.value))}
            className="w-full p-2 bg-secondary/30 border border-border/40 rounded text-foreground text-xs"
          />
        </div>
      </div>

      {costResult ? (
        <div className="p-4 bg-[#0D1117] border border-border/40 rounded-xl space-y-3">
          <div className="flex items-center justify-between border-b border-border/30 pb-2">
            <span className="font-bold text-foreground uppercase text-[10px]">Cost Projection Details</span>
            <span className="text-cyan-400 font-bold">{costResult.model_id}</span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="p-3 bg-secondary/20 border border-border/30 rounded-lg">
              <span className="text-[10px] text-muted-foreground block">Prompt Cost / Req</span>
              <span className="text-lg font-bold text-cyan-400">${costResult.prompt_cost}</span>
            </div>
            <div className="p-3 bg-secondary/20 border border-border/30 rounded-lg">
              <span className="text-[10px] text-muted-foreground block">Completion Cost / Req</span>
              <span className="text-lg font-bold text-emerald-400">${costResult.completion_cost}</span>
            </div>
            <div className="p-3 bg-secondary/20 border border-border/30 rounded-lg">
              <span className="text-[10px] text-muted-foreground block">Cost Per Request</span>
              <span className="text-lg font-bold text-amber-400">${costResult.total_cost_per_request}</span>
            </div>
            <div className="p-3 bg-secondary/20 border border-border/30 rounded-lg">
              <span className="text-[10px] text-muted-foreground block">Est. Monthly Total</span>
              <span className="text-lg font-bold text-rose-400">${costResult.estimated_monthly_cost}</span>
            </div>
          </div>
        </div>
      ) : (
        <div className="p-8 text-center text-muted-foreground italic border border-dashed border-border/40 rounded-xl">
          <Calculator className="h-5 w-5 mx-auto mb-1 text-muted-foreground" />
          Click "Calculate Expenditure" to view token cost estimates.
        </div>
      )}
    </div>
  )
}
