// frontend/src/features/Models/components/providers/ProviderConfigPanel.tsx

import { useState } from "react"
import { Server, Key, Plus, Trash2, CheckCircle, ShieldCheck } from "lucide-react"
import { useProvidersQuery, registerProviderApi, deleteProviderApi } from "../../services/modelsApi"
import { useQueryClient } from "@tanstack/react-query"
import { queryKeys } from "@/services/queries/queryKeys"

export function ProviderConfigPanel() {
  const queryClient = useQueryClient()
  const { data: providers = [], isLoading } = useProvidersQuery()

  const [showModal, setShowModal] = useState(false)
  const [providerName, setProviderName] = useState("")
  const [displayName, setDisplayName] = useState("")
  const [baseUrl, setBaseUrl] = useState("")
  const [apiKey, setApiKey] = useState("")
  const [formError, setFormError] = useState<string | null>(null)

  const handleDelete = async (id: number) => {
    try {
      await deleteProviderApi(id)
      queryClient.invalidateQueries({ queryKey: queryKeys.models.all() })
    } catch {
      // Handled silently
    }
  }

  const handleSaveProvider = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!providerName || !displayName || !baseUrl) return
    setFormError(null)
    try {
      await registerProviderApi({
        provider_name: providerName,
        display_name: displayName,
        api_base_url: baseUrl,
        api_key: apiKey || undefined,
        is_enabled: true,
      })
      queryClient.invalidateQueries({ queryKey: queryKeys.models.all() })
      setProviderName("")
      setDisplayName("")
      setBaseUrl("")
      setApiKey("")
      setShowModal(false)
    } catch (err: unknown) {
      setFormError(err instanceof Error ? err.message : "Failed to register provider")
    }
  }

  return (
    <div className="space-y-4 bg-secondary/15 border border-border/40 rounded-xl p-4 font-mono text-xs">
      <div className="flex items-center justify-between border-b border-border/40 pb-3">
        <div className="flex items-center gap-2">
          <Server className="h-4 w-4 text-emerald-400" />
          <h3 className="text-xs font-bold text-foreground">15+ Model Provider Registry & Key Vault</h3>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-1.5 px-3 py-1.5 font-bold rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 hover:bg-emerald-500/30 cursor-pointer transition-all"
        >
          <Plus className="h-3.5 w-3.5" />
          Configure Provider
        </button>
      </div>

      <div className="p-3 bg-secondary/20 border border-border/30 rounded-lg flex items-center gap-2 text-muted-foreground text-[11px]">
        <ShieldCheck className="h-4 w-4 text-cyan-400 shrink-0" />
        <span>Provider credentials are encrypted at rest with XOR ciphers and decrypted only in memory during model execution.</span>
      </div>

      {isLoading ? (
        <div className="p-8 text-center text-muted-foreground">Loading provider registry...</div>
      ) : (
        <div className="space-y-2">
          {providers.map((p) => (
            <div key={p.id} className="p-3 bg-secondary/20 border border-border/40 rounded-xl flex items-center justify-between gap-4">
              <div className="space-y-0.5">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-foreground text-sm">{p.display_name}</span>
                  <span className="text-[10px] text-cyan-400 uppercase">[{p.provider_name}]</span>
                  {p.is_healthy ? (
                    <span className="text-[10px] text-emerald-400 flex items-center gap-1"><CheckCircle className="h-3 w-3" /> Healthy</span>
                  ) : (
                    <span className="text-[10px] text-rose-400">Degraded</span>
                  )}
                </div>
                <span className="text-[10px] text-muted-foreground block font-mono">{p.api_base_url}</span>
              </div>

              <div className="flex items-center gap-3">
                <span className={`text-[10px] px-2 py-0.5 rounded border ${p.has_api_key ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" : "bg-amber-500/10 text-amber-400 border-amber-500/30"}`}>
                  <Key className="h-3 w-3 inline mr-1" />
                  {p.has_api_key ? "Key Configured" : "No Key Set"}
                </span>

                <button onClick={() => handleDelete(p.id)} className="p-1 hover:bg-red-500/20 text-muted-foreground hover:text-red-400 rounded cursor-pointer">
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0D1117] border border-border/50 rounded-xl p-5 max-w-md w-full space-y-4">
            <h3 className="text-xs font-bold text-foreground uppercase">Configure LLM Provider</h3>
            {formError && <div className="p-2 bg-red-500/10 border border-red-500/30 rounded text-red-400">{formError}</div>}
            <form onSubmit={handleSaveProvider} className="space-y-3">
              <div>
                <label className="text-[10px] text-muted-foreground block mb-1">Provider ID</label>
                <input type="text" value={providerName} onChange={(e) => setProviderName(e.target.value)} placeholder="e.g. deepseek" className="w-full p-2 bg-secondary/30 border border-border/40 rounded text-foreground" />
              </div>
              <div>
                <label className="text-[10px] text-muted-foreground block mb-1">Display Name</label>
                <input type="text" value={displayName} onChange={(e) => setDisplayName(e.target.value)} placeholder="e.g. DeepSeek AI" className="w-full p-2 bg-secondary/30 border border-border/40 rounded text-foreground" />
              </div>
              <div>
                <label className="text-[10px] text-muted-foreground block mb-1">API Base URL</label>
                <input type="text" value={baseUrl} onChange={(e) => setBaseUrl(e.target.value)} placeholder="https://api.deepseek.com/v1" className="w-full p-2 bg-secondary/30 border border-border/40 rounded text-foreground" />
              </div>
              <div>
                <label className="text-[10px] text-muted-foreground block mb-1">API Key (Encrypted at rest)</label>
                <input type="password" value={apiKey} onChange={(e) => setApiKey(e.target.value)} placeholder="sk-..." className="w-full p-2 bg-secondary/30 border border-border/40 rounded text-foreground" />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button type="button" onClick={() => setShowModal(false)} className="px-3 py-1.5 rounded bg-secondary/40 text-muted-foreground">Cancel</button>
                <button type="submit" className="px-3 py-1.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-bold">Save Provider</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
