// frontend/src/features/Deployments/components/backups/BackupRestoreManager.tsx

import { useState } from "react"
import { Database, Download, RefreshCw, CheckCircle } from "lucide-react"
import { useDeploymentStudioStore } from "../../store/useDeploymentStudioStore"
import { createBackupApi, restoreBackupApi } from "../../services/deploymentsApi"

export function BackupRestoreManager() {
  const selectedEnvId = useDeploymentStudioStore((s) => s.selectedEnvId)
  const [statusMsg, setStatusMsg] = useState<string | null>(null)
  const [isBackingUp, setIsBackingUp] = useState(false)

  const handleCreateBackup = async () => {
    setIsBackingUp(true)
    setStatusMsg(null)
    try {
      const res = await createBackupApi(selectedEnvId)
      setStatusMsg(`Backup Snapshot Created! ${res.snapshot_name} (${(res.size_bytes / 1024 / 1024).toFixed(1)} MB)`)
    } catch {
      setStatusMsg("Backup failed")
    } finally {
      setIsBackingUp(false)
    }
  }

  const handleRestore = async (name: string) => {
    try {
      const res = await restoreBackupApi(name)
      setStatusMsg(res.message)
    } catch {
      setStatusMsg("Restore error")
    }
  }

  return (
    <div className="space-y-4 font-mono text-xs">
      <div className="flex items-center justify-between bg-secondary/15 border border-border/40 p-4 rounded-xl">
        <div className="flex items-center gap-2">
          <Database className="h-4 w-4 text-cyan-400" />
          <h3 className="text-xs font-bold text-foreground">Database Snapshot & Disaster Recovery Restore</h3>
        </div>

        <button
          onClick={handleCreateBackup}
          disabled={isBackingUp}
          className="flex items-center gap-1.5 px-3 py-1.5 font-bold rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 hover:bg-cyan-500/30 cursor-pointer transition-all disabled:opacity-50"
        >
          <Download className="h-3.5 w-3.5" />
          {isBackingUp ? "Creating..." : "Create Snapshot"}
        </button>
      </div>

      {statusMsg && (
        <div className="p-3 bg-cyan-500/10 border border-cyan-500/30 rounded-xl text-cyan-300 flex items-center gap-2">
          <CheckCircle className="h-4 w-4 text-cyan-400 shrink-0" />
          <span>{statusMsg}</span>
        </div>
      )}

      <div className="bg-secondary/15 border border-border/40 rounded-xl p-4 space-y-3">
        <h4 className="text-xs font-bold text-foreground border-b border-border/40 pb-2">Available Snapshot Backups</h4>
        <div className="space-y-2">
          {[
            { name: "backup_prod_20260727_173000", size: "15.4 MB", date: "2026-07-27 17:30" },
            { name: "backup_prod_20260726_120000", size: "14.8 MB", date: "2026-07-26 12:00" },
          ].map((b) => (
            <div key={b.name} className="p-3 bg-secondary/20 border border-border/30 rounded-lg flex items-center justify-between">
              <div>
                <span className="text-foreground font-bold">{b.name}</span>
                <div className="text-[10px] text-muted-foreground">Size: {b.size} | Created: {b.date}</div>
              </div>

              <button
                onClick={() => handleRestore(b.name)}
                className="flex items-center gap-1 px-2.5 py-1 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold hover:bg-amber-500/30 cursor-pointer"
              >
                <RefreshCw className="h-3 w-3" />
                Restore DB
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
