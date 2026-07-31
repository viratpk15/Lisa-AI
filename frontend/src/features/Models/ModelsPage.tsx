// frontend/src/features/Models/ModelsPage.tsx

import { WorkspaceShell } from "../Tools/components/shell/WorkspaceShell"
import { useModelStudioStore } from "./store/useModelStudioStore"
import { ModelRegistryGrid } from "./components/registry/ModelRegistryGrid"
import { ProviderConfigPanel } from "./components/providers/ProviderConfigPanel"
import { BenchmarkRunnerPanel } from "./components/benchmark/BenchmarkRunnerPanel"
import { CostCalculatorPanel } from "./components/cost/CostCalculatorPanel"
import { RoutingPolicyEditor } from "./components/routing/RoutingPolicyEditor"
import { ModelAnalyticsDashboard } from "./components/analytics/ModelAnalyticsDashboard"
import type { ModelTabType } from "./types/models.types"
import { Cpu, Server, Zap, DollarSign, GitBranch, Activity } from "lucide-react"

export default function ModelsPage() {
  const activeTab = useModelStudioStore((s) => s.activeTab)
  const setActiveTab = useModelStudioStore((s) => s.setActiveTab)

  const tabs: { id: ModelTabType; label: string; icon: any }[] = [
    { id: "registry", label: "Model Registry", icon: Cpu },
    { id: "providers", label: "Providers (15+)", icon: Server },
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
        {activeTab === "providers" && <ProviderConfigPanel />}
        {activeTab === "benchmark" && <BenchmarkRunnerPanel />}
        {activeTab === "cost" && <CostCalculatorPanel />}
        {activeTab === "routing" && <RoutingPolicyEditor />}
        {activeTab === "analytics" && <ModelAnalyticsDashboard />}
      </div>
    </WorkspaceShell>
  )
}
