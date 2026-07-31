import { useState } from "react"
import { Sparkles, Cpu, CheckCircle, Plus } from "lucide-react"
import { useModelRegistryQuery, setDefaultModelApi, registerModelApi } from "../../services/modelsApi"
import { useQueryClient } from "@tanstack/react-query"
import { queryKeys } from "@/services/queries/queryKeys"

export function ModelRegistryGrid() {
  const queryClient = useQueryClient()
  const { data: models = [], isLoading, isError, error } = useModelRegistryQuery()

  const [showAddModal, setShowAddModal] = useState(false)
  const [providerName, setProviderName] = useState("google")
  const [modelId, setModelId] = useState("")
  const [displayName, setDisplayName] = useState("")
  const [contextWindow, setContextWindow] = useState(128000)
  const [inputCost, setInputCost] = useState(0.0015)
  const [outputCost, setOutputCost] = useState(0.0020)
  const [formError, setFormError] = useState<string | null>(null)

  const handleSetDefault = async (mId: string) => {
    try {
      await setDefaultModelApi(mId)
      queryClient.invalidateQueries({ queryKey: queryKeys.models.all() })
    } catch {
      // Handled silently
    }
  }

  const handleRegisterModel = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!modelId || !displayName) return
    setFormError(null)
    try {
      await registerModelApi({
        provider_name: providerName,
        model_id: modelId,
        display_name: displayName,
        context_window: contextWindow,
        input_cost_per_1k: inputCost,
        output_cost_per_1k: outputCost,
      })
      queryClient.invalidateQueries({ queryKey: queryKeys.models.all() })
      setModelId("")
      setDisplayName("")
      setShowAddModal(false)
    } catch (err: unknown) {
      setFormError(err instanceof Error ? err.message : "Failed to register model")
    }
  }

  return (
    <div className="space-y-4">
      {/* Action Header */}
      <div className="flex items-center justify-between border-b border-border/40 pb-3">
        <div className="flex items-center gap-2">
          <Cpu className="h-4 w-4 text-cyan-400" />
          <h3 className="text-xs font-bold text-foreground font-mono">Registered LLM Architecture Endpoints</h3>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold font-mono rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 hover:bg-cyan-500/30 cursor-pointer transition-all"
        >
          <Plus className="h-3.5 w-3.5" />
          Register Model
        </button>
      </div>

      {isLoading ? (
        <div className="p-8 text-center text-xs font-mono text-muted-foreground">Loading model catalog...</div>
      ) : isError ? (
        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-xs text-red-400 font-mono">
          Error: {error instanceof Error ? error.message : "Failed to load models"}
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-3">
          {models.map((model) => (
            <div
              key={model.id}
              className={`p-4 rounded-xl border transition-all duration-200 flex flex-col justify-between space-y-3 font-mono ${
                model.is_default
                  ? "bg-cyan-500/10 border-cyan-500/60 shadow-md"
                  : "bg-secondary/20 border-border/40 hover:border-cyan-500/30"
              }`}
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="p-2 bg-secondary/40 rounded-lg text-cyan-400">
                    <Sparkles className="h-4 w-4" />
                  </div>
                  {model.is_default ? (
                    <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 flex items-center gap-1">
                      <CheckCircle className="h-3 w-3" /> Default
                    </span>
                  ) : (
                    <button
                      onClick={() => handleSetDefault(model.model_id)}
                      className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-secondary/40 text-muted-foreground hover:text-cyan-300 hover:bg-cyan-500/20 border border-border/30 cursor-pointer transition-all"
                    >
                      Make Default
                    </button>
                  )}
                </div>
                <div>
                  <h4 className="text-sm font-bold text-foreground">{model.display_name}</h4>
                  <span className="text-[10px] text-muted-foreground block">{model.model_id}</span>
                </div>
              </div>

              <div className="space-y-1 text-[11px] pt-2 border-t border-border/30 text-muted-foreground">
                <div className="flex justify-between"><span>Provider:</span> <span className="text-cyan-300 font-bold uppercase">{model.provider_name}</span></div>
                <div className="flex justify-between"><span>Context Limit:</span> <span className="text-foreground">{(model.context_window / 1000).toFixed(0)}k tokens</span></div>
                <div className="flex justify-between"><span>Input Cost:</span> <span className="text-emerald-400">${model.input_cost_per_1k}/1k</span></div>
                <div className="flex justify-between"><span>Output Cost:</span> <span className="text-emerald-400">${model.output_cost_per_1k}/1k</span></div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Model Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0D1117] border border-border/50 rounded-xl p-5 max-w-md w-full space-y-4 font-mono text-xs">
            <h3 className="text-xs font-bold text-foreground uppercase">Register LLM Endpoint</h3>
            {formError && <div className="p-2 bg-red-500/10 border border-red-500/30 rounded text-red-400">{formError}</div>}
            <form onSubmit={handleRegisterModel} className="space-y-3">
              <div>
                <label className="text-[10px] text-muted-foreground block mb-1">Provider Catalog Name</label>
                <input
                  type="text"
                  value={providerName}
                  onChange={(e) => setProviderName(e.target.value)}
                  className="w-full p-2 bg-secondary/30 border border-border/40 rounded text-foreground"
                />
              </div>
              <div>
                <label className="text-[10px] text-muted-foreground block mb-1">Model Identifier</label>
                <input
                  type="text"
                  value={modelId}
                  onChange={(e) => setModelId(e.target.value)}
                  placeholder="e.g. claude-3-5-haiku"
                  className="w-full p-2 bg-secondary/30 border border-border/40 rounded text-foreground"
                />
              </div>
              <div>
                <label className="text-[10px] text-muted-foreground block mb-1">Display Label</label>
                <input
                  type="text"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  placeholder="e.g. Claude 3.5 Haiku"
                  className="w-full p-2 bg-secondary/30 border border-border/40 rounded text-foreground"
                />
              </div>

              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="text-[10px] text-muted-foreground block mb-1">Context Window</label>
                  <input
                    type="number"
                    value={contextWindow}
                    onChange={(e) => setContextWindow(Number(e.target.value))}
                    className="w-full p-2 bg-secondary/30 border border-border/40 rounded text-foreground"
                  />
                </div>
                <div>
                  <label className="text-[10px] text-muted-foreground block mb-1">Input $/1k</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={inputCost}
                    onChange={(e) => setInputCost(Number(e.target.value))}
                    className="w-full p-2 bg-secondary/30 border border-border/40 rounded text-foreground"
                  />
                </div>
                <div>
                  <label className="text-[10px] text-muted-foreground block mb-1">Output $/1k</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={outputCost}
                    onChange={(e) => setOutputCost(Number(e.target.value))}
                    className="w-full p-2 bg-secondary/30 border border-border/40 rounded text-foreground"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button type="button" onClick={() => setShowAddModal(false)} className="px-3 py-1.5 rounded bg-secondary/40 text-muted-foreground">Cancel</button>
                <button type="submit" className="px-3 py-1.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold">Register Model</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
