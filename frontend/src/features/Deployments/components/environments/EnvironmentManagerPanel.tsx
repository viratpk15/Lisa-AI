// frontend/src/features/Deployments/components/environments/EnvironmentManagerPanel.tsx

import { Server, Globe, Cpu, CheckCircle } from "lucide-react"
import { useDeploymentStudioStore } from "../../store/useDeploymentStudioStore"
import { useEnvironmentsQuery, useTargetsQuery } from "../../services/deploymentsApi"

export function EnvironmentManagerPanel() {
  const selectedEnvId = useDeploymentStudioStore((s) => s.selectedEnvId)
  const setSelectedEnvId = useDeploymentStudioStore((s) => s.setSelectedEnvId)
  const { data: envs } = useEnvironmentsQuery()
  const { data: targets } = useTargetsQuery()

  const providerIcons: Record<string, any> = {
    docker: Server,
    k8s: Cpu,
    railway: Globe,
    aws: Server,
  }

  return (
    <div className="space-y-4 font-mono text-xs">
      <div className="flex items-center justify-between border-b border-border/40 pb-3">
        <h3 className="text-xs font-bold text-foreground uppercase">Deployment Environment Registry</h3>
        <span className="text-[10px] text-cyan-400 font-bold">{envs?.length || 3} Environments Active</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {(envs || [
          { id: 1, env_id: "prod", name: "Production Environment", tier: "production", is_active: true },
          { id: 2, env_id: "staging", name: "Staging Pre-Release", tier: "staging", is_active: true },
          { id: 3, env_id: "dev", name: "Local Development", tier: "dev", is_active: true },
        ]).map((env) => {
          const isSelected = selectedEnvId === env.env_id
          return (
            <div
              key={env.env_id}
              onClick={() => setSelectedEnvId(env.env_id)}
              className={`p-4 rounded-xl border cursor-pointer transition-all ${
                isSelected
                  ? "bg-cyan-500/20 border-cyan-500 font-bold shadow-lg"
                  : "bg-secondary/20 border-border/30 hover:border-cyan-500/40"
              }`}
            >
              <div className="flex items-center justify-between border-b border-border/30 pb-2 mb-2">
                <span className="text-foreground font-bold">{env.name}</span>
                {isSelected && <CheckCircle className="h-4 w-4 text-cyan-400" />}
              </div>
              <div className="text-[10px] text-muted-foreground space-y-1">
                <div>Tier: <span className="text-cyan-300 uppercase">{env.tier}</span></div>
                <div>ID: <span className="text-foreground">{env.env_id}</span></div>
              </div>
            </div>
          )
        })}
      </div>

      <div className="space-y-3 bg-secondary/15 border border-border/40 rounded-xl p-4">
        <h4 className="text-xs font-bold text-foreground border-b border-border/40 pb-2">Target Provider Configured Clusters</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {(targets || [
            { id: 1, provider_type: "docker", status: "active", config: { replicas: 3 } },
            { id: 2, provider_type: "k8s", status: "active", config: { namespace: "prod" } },
          ]).map((target, i) => {
            const Icon = providerIcons[target.provider_type] || Server
            return (
              <div key={i} className="p-3 bg-secondary/20 border border-border/30 rounded-lg flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Icon className="h-4 w-4 text-cyan-400" />
                  <span className="text-foreground font-bold uppercase">{target.provider_type} Target</span>
                </div>
                <span className="text-emerald-400 text-[10px] bg-emerald-500/10 border border-emerald-500/30 px-2 py-0.5 rounded">
                  {target.status}
                </span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
