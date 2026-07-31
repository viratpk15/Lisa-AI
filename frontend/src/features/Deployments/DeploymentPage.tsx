// frontend/src/features/Deployments/DeploymentPage.tsx

import { WorkspaceShell } from "../Tools/components/shell/WorkspaceShell"
import { useDeploymentStudioStore } from "./store/useDeploymentStudioStore"
import { DeploymentMetricsDashboard } from "./components/dashboard/DeploymentMetricsDashboard"
import { EnvironmentManagerPanel } from "./components/environments/EnvironmentManagerPanel"
import { ReleaseHistoryPanel } from "./components/releases/ReleaseHistoryPanel"
import { SecretVaultManagerModal } from "./components/secrets/SecretVaultManagerModal"
import { BackupRestoreManager } from "./components/backups/BackupRestoreManager"
import type { DeploymentTabType } from "./types/deployments.types"
import { Activity, Server, Rocket, Lock, Database } from "lucide-react"

export default function DeploymentPage() {
  const activeTab = useDeploymentStudioStore((s) => s.activeTab)
  const setActiveTab = useDeploymentStudioStore((s) => s.setActiveTab)

  const tabs: { id: DeploymentTabType; label: string; icon: any }[] = [
    { id: "dashboard", label: "Health & Telemetry", icon: Activity },
    { id: "environments", label: "Environments & Targets", icon: Server },
    { id: "releases", label: "Release Rollout", icon: Rocket },
    { id: "secrets", label: "Secret Vault", icon: Lock },
    { id: "backups", label: "Database Backups", icon: Database },
  ]

  return (
    <WorkspaceShell
      title="Deployment Studio"
      subtitle="Enterprise multi-cloud deployment orchestrator, secret vault, health monitoring, and automated disaster recovery engine."
    >
      <div className="space-y-4 font-mono">
        {/* Navigation Bar */}
        <div className="flex items-center justify-between border-b border-border/40 pb-3">
          <div className="flex items-center gap-2">
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
              )}
            )}
          </div>
        </div>

        {/* Viewport Panels */}
        {activeTab === "dashboard" && <DeploymentMetricsDashboard />}
        {activeTab === "environments" && <EnvironmentManagerPanel />}
        {activeTab === "releases" && <ReleaseHistoryPanel />}
        {activeTab === "secrets" && <SecretVaultManagerModal />}
        {activeTab === "backups" && <BackupRestoreManager />}
      </div>
    </WorkspaceShell>
  )
}
