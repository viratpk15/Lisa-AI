// frontend/src/features/Models/components/benchmark/BenchmarkRunnerPanel.tsx

import { useState } from "react"
import { Zap, Award, Activity } from "lucide-react"
import { useModelStudioStore } from "../../store/useModelStudioStore"
import { useModelRegistryQuery, runBenchmarkApi } from "../../services/modelsApi"
import type { BenchmarkRun } from "../../types/models.types"

export function BenchmarkRunnerPanel() {
  const selectedModelId = useModelStudioStore((s) => s.selectedModelId)
  const setSelectedModelId = useModelStudioStore((s) => s.setSelectedModelId)
  const promptTokens = useModelStudioStore((s) => s.benchmarkPromptTokens)
  const setPromptTokens = useModelStudioStore((s) => s.setBenchmarkPromptTokens)
  const completionTokens = useModelStudioStore((s) => s.benchmarkCompletionTokens)
  const setCompletionTokens = useModelStudioStore((s) => s.setBenchmarkCompletionTokens)

  const { data: models = [] } = useModelRegistryQuery()
  const [isRunning, setIsRunning] = useState(false)
  const [benchmarkResult, setBenchmarkResult] = useState<BenchmarkRun | null>(null)

  const handleRunBenchmark = async () => {
    setIsRunning(true)
    try {
      const res = await runBenchmarkApi({
        model_id: selectedModelId,
        prompt_tokens: promptTokens,
        completion_tokens: completionTokens,
      })
      setBenchmarkResult(res)
    } catch {
      // Handled silently
    } finally {
      setIsRunning(false)
    }
  }

  return (
    <div className="space-y-4 bg-secondary/15 border border-border/40 rounded-xl p-4 font-mono text-xs">
      <div className="flex items-center justify-between border-b border-border/40 pb-3">
        <div className="flex items-center gap-2">
          <Zap className="h-4 w-4 text-amber-400" />
          <h3 className="text-xs font-bold text-foreground">Interactive Latency & TTFT Benchmark Runner</h3>
        </div>
        <button
          onClick={handleRunBenchmark}
          disabled={isRunning}
          className="px-3 py-1.5 font-bold rounded-lg bg-amber-500/20 text-amber-300 border border-amber-500/40 hover:bg-amber-500/30 cursor-pointer transition-all disabled:opacity-50"
        >
          {isRunning ? "Testing Latency..." : "Run Latency Benchmark"}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="text-[10px] text-muted-foreground block mb-1">Target Model</label>
          <select
            value={selectedModelId}
            onChange={(e) => setSelectedModelId(e.target.value)}
            className="w-full p-2 bg-secondary/30 border border-border/40 rounded text-foreground text-xs"
          >
            {models.map((m) => (
              <option key={m.id} value={m.model_id}>{m.display_name} ({m.model_id})</option>
            ))}
          </select>
        </div>

        <div>
          <label className="text-[10px] text-muted-foreground block mb-1">Prompt Tokens</label>
          <input
            type="number"
            value={promptTokens}
            onChange={(e) => setPromptTokens(Number(e.target.value))}
            className="w-full p-2 bg-secondary/30 border border-border/40 rounded text-foreground text-xs"
          />
        </div>

        <div>
          <label className="text-[10px] text-muted-foreground block mb-1">Completion Tokens</label>
          <input
            type="number"
            value={completionTokens}
            onChange={(e) => setCompletionTokens(Number(e.target.value))}
            className="w-full p-2 bg-secondary/30 border border-border/40 rounded text-foreground text-xs"
          />
        </div>
      </div>

      {benchmarkResult ? (
        <div className="p-4 bg-[#0D1117] border border-border/40 rounded-xl space-y-3">
          <div className="flex items-center gap-2 border-b border-border/30 pb-2">
            <Award className="h-4 w-4 text-amber-400" />
            <span className="font-bold text-foreground">Benchmark Results: {benchmarkResult.model_id}</span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="p-3 bg-secondary/20 border border-border/30 rounded-lg">
              <span className="text-[10px] text-muted-foreground block">Total Latency</span>
              <span className="text-lg font-bold text-cyan-400">{benchmarkResult.total_latency_ms}ms</span>
            </div>
            <div className="p-3 bg-secondary/20 border border-border/30 rounded-lg">
              <span className="text-[10px] text-muted-foreground block">TTFT (First Token)</span>
              <span className="text-lg font-bold text-emerald-400">{benchmarkResult.ttft_ms}ms</span>
            </div>
            <div className="p-3 bg-secondary/20 border border-border/30 rounded-lg">
              <span className="text-[10px] text-muted-foreground block">Generation Tokens</span>
              <span className="text-lg font-bold text-amber-400">{benchmarkResult.completion_tokens}t</span>
            </div>
            <div className="p-3 bg-secondary/20 border border-border/30 rounded-lg">
              <span className="text-[10px] text-muted-foreground block">Throughput Speed</span>
              <span className="text-lg font-bold text-rose-400">
                {((benchmarkResult.completion_tokens / (benchmarkResult.total_latency_ms / 1000))).toFixed(1)} t/s
              </span>
            </div>
          </div>
        </div>
      ) : (
        <div className="p-8 text-center text-muted-foreground italic border border-dashed border-border/40 rounded-xl">
          <Activity className="h-5 w-5 mx-auto mb-1 text-muted-foreground" />
          Click "Run Latency Benchmark" to test model response time, TTFT, and generation throughput.
        </div>
      )}
    </div>
  )
}
