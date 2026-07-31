// frontend/src/features/Agents/components/AnalyticsDashboard.tsx
import { BarChart3, Activity, Cpu, CheckCircle } from "lucide-react"

export default function AnalyticsDashboard() {
  return (
    <div className="space-y-4 font-mono text-xs">
      <div className="flex items-center justify-between border-b border-border/40 pb-3">
        <div className="flex items-center gap-2">
          <BarChart3 className="h-4 w-4 text-cyan-400" />
          <h3 className="text-xs font-bold text-foreground">Agent Performance & Execution Analytics</h3>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="p-4 bg-secondary/20 border border-border/30 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="flex items-center gap-1.5"><Activity className="h-4 w-4 text-cyan-400" /> Total Executions</span>
            <span className="text-cyan-400 font-bold">142 Runs</span>
          </div>
          <div className="w-full h-2 bg-secondary/50 rounded-full overflow-hidden">
            <div className="h-full bg-cyan-400" style={{ width: "85%" }} />
          </div>
        </div>

        <div className="p-4 bg-secondary/20 border border-border/30 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="flex items-center gap-1.5"><Cpu className="h-4 w-4 text-emerald-400" /> Avg Latency</span>
            <span className="text-emerald-400 font-bold">18.4ms</span>
          </div>
          <div className="w-full h-2 bg-secondary/50 rounded-full overflow-hidden">
            <div className="h-full bg-emerald-400" style={{ width: "20%" }} />
          </div>
        </div>

        <div className="p-4 bg-secondary/20 border border-border/30 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="flex items-center gap-1.5"><CheckCircle className="h-4 w-4 text-amber-400" /> Goal Completion Rate</span>
            <span className="text-amber-400 font-bold">98.5%</span>
          </div>
          <div className="w-full h-2 bg-secondary/50 rounded-full overflow-hidden">
            <div className="h-full bg-amber-400" style={{ width: "98.5%" }} />
          </div>
        </div>
      </div>
    </div>
  )
}