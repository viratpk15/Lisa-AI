// frontend/src/features/Models/components/routing/RoutingPolicyEditor.tsx

import { Sliders, GitBranch } from "lucide-react"
import { useRoutingPoliciesQuery } from "../../services/modelsApi"

export function RoutingPolicyEditor() {
  const { data: policies = [], isLoading } = useRoutingPoliciesQuery()

  return (
    <div className="space-y-4 bg-secondary/15 border border-border/40 rounded-xl p-4 font-mono text-xs">
      <div className="flex items-center justify-between border-b border-border/40 pb-3">
        <div className="flex items-center gap-2">
          <GitBranch className="h-4 w-4 text-violet-400" />
          <h3 className="text-xs font-bold text-foreground">Multi-Provider Fallback Chains & Routing Policies</h3>
        </div>
        <span className="text-[10px] text-muted-foreground">{policies.length} Active Policies</span>
      </div>

      {isLoading ? (
        <div className="p-8 text-center text-muted-foreground">Loading routing policies...</div>
      ) : (
        <div className="space-y-3">
          {policies.map((p) => (
            <div key={p.id} className="p-4 bg-secondary/20 border border-border/40 rounded-xl space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Sliders className="h-3.5 w-3.5 text-cyan-400" />
                  <span className="font-bold text-foreground text-sm">{p.policy_name}</span>
                </div>
                <span className="px-2 py-0.5 text-[10px] rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-bold uppercase">
                  {p.is_active ? "Active Policy" : "Inactive"}
                </span>
              </div>
              <p className="text-[11px] text-muted-foreground">{p.description}</p>
              <pre className="p-3 bg-[#0D1117] border border-border/40 rounded-lg text-cyan-300 text-[11px] overflow-x-auto">
                {JSON.stringify(p.config_json, null, 2)}
              </pre>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
