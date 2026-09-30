// frontend/src/features/Models/ModelsPage.tsx

import { useState } from "react"
import { WorkspaceShell } from "../Tools/components/shell/WorkspaceShell"
import { useModelStudioStore } from "./store/useModelStudioStore"
import { ModelRegistryGrid } from "./components/registry/ModelRegistryGrid"
import { BenchmarkRunnerPanel } from "./components/benchmark/BenchmarkRunnerPanel"
import { CostCalculatorPanel } from "./components/cost/CostCalculatorPanel"
import { RoutingPolicyEditor } from "./components/routing/RoutingPolicyEditor"
import { ModelAnalyticsDashboard } from "./components/analytics/ModelAnalyticsDashboard"
import type { ModelTabType } from "./types/models.types"
import { Cpu, Server, Zap, DollarSign, GitBranch, Activity, Key, Plus, Trash2, CheckCircle, ShieldCheck } from "lucide-react"
import { useProvidersQuery, registerProviderApi, deleteProviderApi } from "./services/modelsApi"
import { useQueryClient } from "@tanstack/react-query"
import { queryKeys } from "@/services/queries/queryKeys"
import { isAllowedProvider } from "./utils/allowedProviders"

function FilteredProviderConfigPanel() {
  const queryClient = useQueryClient()
  const { data: allProviders = [], isLoading } = useProvidersQuery()

  // Filter provider list to show only authorized providers
  const providers = allProviders.filter(isAllowedProvider)

  const [showModal, setShowModal] = useState(false)
  const [providerName, setProviderName] = useState("groq")
  const [displayName, setDisplayName] = useState("Groq LPU")
  const [baseUrl, setBaseUrl] = useState("https://api.groq.com/openai/v1")
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

  const handleSelectPreset = (preset: "groq" | "nvidia" | "mistral") => {
    if (preset === "groq") {
      setProviderName("groq")
      setDisplayName("Groq Cloud")
      setBaseUrl("https://api.groq.com/openai/v1")
    } else if (preset === "nvidia") {
      setProviderName("nvidia")
      setDisplayName("NVIDIA NIM")
      setBaseUrl("https://integrate.api.nvidia.com/v1")
    } else if (preset === "mistral") {
      setProviderName("mistral")
      setDisplayName("Mistral AI")
      setBaseUrl("https://api.mistral.ai/v1")
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
          <h3 className="text-xs font-bold text-foreground">Active LLM Provider Registry</h3>
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
        <span>Authorized production inference providers: Groq, NVIDIA NIM, and Mistral. Credentials are encrypted at rest.</span>
      </div>

      {isLoading ? (
        <div className="p-8 text-center text-muted-foreground">Loading provider registry...</div>
      ) : providers.length === 0 ? (
        <div className="p-8 text-center text-muted-foreground space-y-2">
          <p>No authorized providers configured yet.</p>
          <p className="text-[11px]">Configure Groq, NVIDIA NIM, or Mistral credentials to enable inference.</p>
        </div>
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
            
            {/* Quick preset selection */}
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => handleSelectPreset("groq")}
                className={`flex-1 py-1.5 px-2 rounded border text-[11px] font-bold cursor-pointer transition-all ${
                  providerName === "groq"
                    ? "bg-cyan-500/20 border-cyan-500/50 text-cyan-300"
                    : "bg-secondary/30 border-border/40 text-muted-foreground hover:text-foreground"
                }`}
              >
                Groq
              </button>
              <button
                type="button"
                onClick={() => handleSelectPreset("nvidia")}
                className={`flex-1 py-1.5 px-2 rounded border text-[11px] font-bold cursor-pointer transition-all ${
                  providerName === "nvidia"
                    ? "bg-cyan-500/20 border-cyan-500/50 text-cyan-300"
                    : "bg-secondary/30 border-border/40 text-muted-foreground hover:text-foreground"
                }`}
              >
                NVIDIA NIM
              </button>
              <button
                type="button"
                onClick={() => handleSelectPreset("mistral")}
                className={`flex-1 py-1.5 px-2 rounded border text-[11px] font-bold cursor-pointer transition-all ${
                  providerName === "mistral"
                    ? "bg-cyan-500/20 border-cyan-500/50 text-cyan-300"
                    : "bg-secondary/30 border-border/40 text-muted-foreground hover:text-foreground"
                }`}
              >
                Mistral
              </button>
            </div>

            <form onSubmit={handleSaveProvider} className="space-y-3">
              <div>
                <label className="text-[10px] text-muted-foreground block mb-1">Provider ID</label>
                <input
                  type="text"
                  value={providerName}
                  onChange={(e) => setProviderName(e.target.value)}
                  placeholder="e.g. groq"
                  className="w-full p-2 bg-secondary/30 border border-border/40 rounded text-foreground"
                />
              </div>
              <div>
                <label className="text-[10px] text-muted-foreground block mb-1">Display Name</label>
                <input
                  type="text"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  placeholder="e.g. Groq Cloud"
                  className="w-full p-2 bg-secondary/30 border border-border/40 rounded text-foreground"
                />
              </div>
              <div>
                <label className="text-[10px] text-muted-foreground block mb-1">API Base URL</label>
                <input
                  type="text"
                  value={baseUrl}
                  onChange={(e) => setBaseUrl(e.target.value)}
                  placeholder="https://api.groq.com/openai/v1"
                  className="w-full p-2 bg-secondary/30 border border-border/40 rounded text-foreground"
                />
              </div>
              <div>
                <label className="text-[10px] text-muted-foreground block mb-1">API Key (Encrypted at rest)</label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="sk-..."
                  className="w-full p-2 bg-secondary/30 border border-border/40 rounded text-foreground"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button type="button" onClick={() => setShowModal(false)} className="px-3 py-1.5 rounded bg-secondary/40 text-muted-foreground cursor-pointer">Cancel</button>
                <button type="submit" className="px-3 py-1.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-bold cursor-pointer">Save Provider</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default function ModelsPage() {
  const activeTab = useModelStudioStore((s) => s.activeTab)
  const setActiveTab = useModelStudioStore((s) => s.setActiveTab)

  const tabs: { id: ModelTabType; label: string; icon: any }[] = [
    { id: "registry", label: "Model Registry", icon: Cpu },
    { id: "providers", label: "Providers (Groq, NVIDIA NIM, Mistral)", icon: Server },
    { id: "benchmark", label: "Latency Benchmark", icon: Zap },
    { id: "cost", label: "Cost Calculator", icon: DollarSign },
    { id: "routing", label: "Routing & Fallbacks", icon: GitBranch },
    { id: "analytics", label: "Analytics", icon: Activity },
  ]

  return (
    <WorkspaceShell
      title="Model Studio"
      subtitle="Provider registry, multi-model fallback chains, latency benchmarking, and token cost analytics."
    >
      <div className="space-y-4">
        {/* Model Studio Navigation Tabs */}
        <div className="flex flex-wrap items-center gap-2 border-b border-border/40 pb-3 font-mono">
          {tabs.map((tab) => {
            const Icon = tab.icon
            const isSelected = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-3 py-1.5 text-xs font-bold rounded-lg cursor-pointer transition-all ${
                  isSelected
                    ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 shadow-sm"
                    : "text-muted-foreground hover:text-foreground hover:bg-secondary/40"
                }`}
              >
                <Icon className={`h-3.5 w-3.5 ${isSelected ? "text-cyan-400" : "text-muted-foreground"}`} />
                <span>{tab.label}</span>
              </button>
            )
          })}
        </div>

        {/* Viewport Panels */}
        {activeTab === "registry" && <ModelRegistryGrid />}
        {activeTab === "providers" && <FilteredProviderConfigPanel />}
        {activeTab === "benchmark" && <BenchmarkRunnerPanel />}
        {activeTab === "cost" && <CostCalculatorPanel />}
        {activeTab === "routing" && <RoutingPolicyEditor />}
        {activeTab === "analytics" && <ModelAnalyticsDashboard />}
      </div>
    </WorkspaceShell>
  )
}

