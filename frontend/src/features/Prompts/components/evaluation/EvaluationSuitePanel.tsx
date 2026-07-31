import { useState } from "react"
import { Award, CheckCircle2, ShieldCheck } from "lucide-react"
import { evaluateExecutionApi } from "../../services/promptsApi"

export function EvaluationSuitePanel() {
  const [correctness, setCorrectness] = useState(10.0)
  const [hallucination, setHallucination] = useState(0.0)
  const [tone, setTone] = useState(9.5)
  const [clarity, setClarity] = useState(9.5)
  const [relevance, setRelevance] = useState(10.0)
  const [evalResult, setEvalResult] = useState<any>(null)
  const [isEvaluating, setIsEvaluating] = useState(false)

  const handleRunEvaluation = async () => {
    setIsEvaluating(true)
    try {
      const res = await evaluateExecutionApi({
        execution_id: `exec_adhoc_${Date.now()}`,
        correctness,
        hallucination,
        tone,
        clarity,
        relevance,
      })
      setEvalResult(res)
    } catch (err: any) {
      console.error(err)
    } finally {
      setIsEvaluating(false)
    }
  }

  return (
    <div className="space-y-4 bg-secondary/15 border border-border/40 rounded-xl p-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border/40 pb-3">
        <div className="flex items-center gap-2">
          <Award className="h-4 w-4 text-cyan-400" />
          <h3 className="text-xs font-bold text-foreground">AI & Human Quality Evaluation Suite</h3>
        </div>

        <button
          onClick={handleRunEvaluation}
          disabled={isEvaluating}
          className="inline-flex items-center gap-1.5 px-4 py-1.5 text-xs font-bold bg-cyan-500 hover:bg-cyan-400 text-black rounded-lg cursor-pointer transition-all shadow-md disabled:opacity-50"
        >
          <ShieldCheck className="h-3.5 w-3.5" />
          {isEvaluating ? "Scoring..." : "Run AI Auto-Evaluate"}
        </button>
      </div>

      {/* Evaluation Criteria Controls Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-3 bg-secondary/20 p-3 rounded-lg border border-border/40 font-mono text-xs">
          <div className="space-y-1">
            <div className="flex justify-between text-[11px]">
              <span className="text-foreground font-bold">Correctness & Precision Score</span>
              <span className="text-cyan-400 font-bold">{correctness} / 10</span>
            </div>
            <input
              type="range"
              min="0"
              max="10"
              step="0.5"
              value={correctness}
              onChange={(e) => setCorrectness(Number(e.target.value))}
              className="w-full h-1.5 bg-secondary/60 rounded-lg appearance-none cursor-pointer accent-cyan-500"
            />
          </div>

          <div className="space-y-1">
            <div className="flex justify-between text-[11px]">
              <span className="text-foreground font-bold">Tone Appropriateness & Persona Alignment</span>
              <span className="text-cyan-400 font-bold">{tone} / 10</span>
            </div>
            <input
              type="range"
              min="0"
              max="10"
              step="0.5"
              value={tone}
              onChange={(e) => setTone(Number(e.target.value))}
              className="w-full h-1.5 bg-secondary/60 rounded-lg appearance-none cursor-pointer accent-cyan-500"
            />
          </div>

          <div className="space-y-1">
            <div className="flex justify-between text-[11px]">
              <span className="text-foreground font-bold">Hallucination Risk (Lower is Better)</span>
              <span className="text-rose-400 font-bold">{hallucination} / 10</span>
            </div>
            <input
              type="range"
              min="0"
              max="10"
              step="0.5"
              value={hallucination}
              onChange={(e) => setHallucination(Number(e.target.value))}
              className="w-full h-1.5 bg-secondary/60 rounded-lg appearance-none cursor-pointer accent-rose-500"
            />
          </div>

          <div className="space-y-1">
            <div className="flex justify-between text-[11px]">
              <span className="text-foreground font-bold">Clarity & Structural Formatting</span>
              <span className="text-violet-400 font-bold">{clarity} / 10</span>
            </div>
            <input
              type="range"
              min="0"
              max="10"
              step="0.5"
              value={clarity}
              onChange={(e) => setClarity(Number(e.target.value))}
              className="w-full h-1.5 bg-secondary/60 rounded-lg appearance-none cursor-pointer accent-violet-500"
            />
          </div>

          <div className="space-y-1">
            <div className="flex justify-between text-[11px]">
              <span className="text-foreground font-bold">Contextual Relevance & Groundedness</span>
              <span className="text-emerald-400 font-bold">{relevance} / 10</span>
            </div>
            <input
              type="range"
              min="0"
              max="10"
              step="0.5"
              value={relevance}
              onChange={(e) => setRelevance(Number(e.target.value))}
              className="w-full h-1.5 bg-secondary/60 rounded-lg appearance-none cursor-pointer accent-emerald-500"
            />
          </div>
        </div>

        {/* Evaluation Output Result */}
        <div className="space-y-2 font-mono text-xs">
          <span className="text-xs font-bold text-foreground">Scoring Assessment Matrix</span>

          {evalResult ? (
            <div className="p-4 bg-[#0D1117] border border-border/40 rounded-xl space-y-3">
              <div className="flex items-center justify-between border-b border-border/40 pb-2">
                <span className="font-bold text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 className="h-4 w-4" />
                  Evaluation Score Passed
                </span>
                <span className="text-[10px] text-muted-foreground">{evalResult.evaluator_type}</span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-[11px]">
                <div className="p-2 bg-secondary/20 rounded border border-border/30">
                  <span className="text-[10px] text-muted-foreground uppercase">Correctness</span>
                  <div className="font-bold text-cyan-400">{evalResult.correctness_score} / 10</div>
                </div>

                <div className="p-2 bg-secondary/20 rounded border border-border/30">
                  <span className="text-[10px] text-muted-foreground uppercase">Hallucination</span>
                  <div className="font-bold text-emerald-400">{evalResult.hallucination_score} (0%)</div>
                </div>
              </div>

              <p className="text-[11px] text-[#C9D1D9] leading-relaxed italic bg-secondary/10 p-2 rounded">
                "{evalResult.detailed_feedback?.summary}"
              </p>
            </div>
          ) : (
            <div className="p-6 text-center text-xs text-muted-foreground italic bg-secondary/10 border border-dashed border-border/40 rounded-xl">
              Configure quality parameters on the left and click "Run AI Auto-Evaluate".
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
