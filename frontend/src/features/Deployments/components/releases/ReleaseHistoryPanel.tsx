// frontend/src/features/Deployments/components/releases/ReleaseHistoryPanel.tsx

import { useState } from "react"
import { Rocket, CheckCircle, RotateCcw } from "lucide-react"
import { useDeploymentStudioStore } from "../../store/useDeploymentStudioStore"
import { triggerRolloutApi, triggerRollbackApi } from "../../services/deploymentsApi"

export function ReleaseHistoryPanel() {
  const selectedEnvId = useDeploymentStudioStore((s) => s.selectedEnvId)
  const addLog = useDeploymentStudioStore((s) => s.addLog)

  const [versionTag, setVersionTag] = useState("v1.8.0")
  const [strategy, setStrategy] = useState("blue_green")
  const [statusMsg, setStatusMsg] = useState<string | null>(null)
  const [isDeploying, setIsDeploying] = useState(false)

  const handleRollout = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsDeploying(true)
    setStatusMsg(null)
    try {
      const res = await triggerRolloutApi({ env_id: selectedEnvId, version_tag: versionTag, strategy })
      setStatusMsg(`Rollout triggered! Release ID: ${res.release_id} (${res.strategy})`)
      addLog({ timestamp: new Date().toLocaleTimeString(), level: "INFO", message: `Deployed ${versionTag} to ${selectedEnvId}` })
    } catch {
      setStatusMsg("Rollout failed")
    } finally {
      setIsDeploying(false)
    }
  }

  const handleRollback = async (relId: string) => {
    try {
      const res = await triggerRollbackApi({ env_id: selectedEnvId, target_release_id: relId })
      setStatusMsg(res.message)
    } catch {
      setStatusMsg("Rollback error")
    }
  }

  return (
    <div className="space-y-4 font-mono text-xs">
      {/* Trigger Rollout Form */}
      <div className="bg-secondary/15 border border-border/40 p-4 rounded-xl space-y-3">
        <div className="flex items-center gap-2 border-b border-border/40 pb-2">
          <Rocket className="h-4 w-4 text-cyan-400" />
          <h3 className="text-xs font-bold text-foreground">Trigger Deployment Release Rollout</h3>
        </div>

        <form onSubmit={handleRollout} className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <input
            type="text"
            placeholder="Version Tag (e.g. v1.8.0)"
            value={versionTag}
            onChange={(e) => setVersionTag(e.target.value)}
            className="p-2 bg-secondary/30 border border-border/40 rounded text-foreground text-xs"
          />
          <select
            value={strategy}
            onChange={(e) => setStrategy(e.target.value)}
            className="p-2 bg-secondary/30 border border-border/40 rounded text-foreground text-xs"
          >
            <option value="blue_green">Blue/Green Strategy</option>
            <option value="canary">Canary Strategy</option>
            <option value="direct">Direct Rolling Update</option>
          </select>
          <button
            type="submit"
            disabled={isDeploying}
            className="py-2 px-4 font-bold rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 hover:bg-cyan-500/30 cursor-pointer transition-all disabled:opacity-50"
          >
            {isDeploying ? "Deploying..." : "Execute Rollout"}
          </button>
        </form>

        {statusMsg && (
          <div className="p-3 bg-cyan-500/10 border border-cyan-500/30 rounded-lg text-cyan-300 flex items-center gap-2">
            <CheckCircle className="h-4 w-4 text-cyan-400 shrink-0" />
            <span>{statusMsg}</span>
          </div>
        )}
      </div>

      {/* Release History */}
      <div className="bg-secondary/15 border border-border/40 rounded-xl p-4 space-y-3">
        <h4 className="text-xs font-bold text-foreground border-b border-border/40 pb-2">Release Deployment History</h4>
        <div className="space-y-2">
          {[
            { release_id: "rel_v1_8_0", version_tag: "v1.8.0", strategy: "blue_green", status: "healthy", deployed_at: "2026-07-27 17:30" },
            { release_id: "rel_v1_7_0", version_tag: "v1.7.0", strategy: "blue_green", status: "rolled_back", deployed_at: "2026-07-26 14:20" },
          ].map((rel) => (
            <div key={rel.release_id} className="p-3 bg-secondary/20 border border-border/30 rounded-lg flex items-center justify-between">
              <div>
                <span className="text-foreground font-bold">{rel.version_tag}</span>{" "}
                <span className="text-muted-foreground text-[10px]">({rel.strategy})</span>
                <div className="text-[10px] text-muted-foreground">ID: {rel.release_id} | {rel.deployed_at}</div>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-emerald-400 text-[10px] bg-emerald-500/10 border border-emerald-500/30 px-2 py-0.5 rounded">
                  {rel.status}
                </span>
                <button
                  onClick={() => handleRollback(rel.release_id)}
                  className="p-1 rounded bg-rose-500/20 text-rose-300 border border-rose-500/40 hover:bg-rose-500/30 cursor-pointer"
                  title="Rollback to this version"
                >
                  <RotateCcw className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
