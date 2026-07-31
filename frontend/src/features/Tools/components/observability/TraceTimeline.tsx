import { CheckCircle2, ShieldCheck, Clock, Layers, Activity } from "lucide-react"
import type { ToolResult } from "../../types/tools.types"

interface TraceTimelineProps {
  result: ToolResult
}

export function TraceTimeline({ result }: TraceTimelineProps) {
  const stages = [
    {
      id: "val",
      name: "1. Payload Validation Stage",
      description: "Sanitized tool name & argument payload boundaries.",
      duration: "< 0.01 ms",
      status: "PASS",
      icon: <ShieldCheck className="h-3.5 w-3.5 text-cyan-400" />,
    },
    {
      id: "reg",
      name: "2. Registry Lookup",
      description: `O(1) index lookup for tool '${result.tool_name}'.`,
      duration: "< 0.01 ms",
      status: "PASS",
      icon: <Layers className="h-3.5 w-3.5 text-blue-400" />,
    },
    {
      id: "perm",
      name: "3. RBAC & Permission Stage",
      description: `Verified caller context level '${result.metadata?.permission_level || "USER"}'.`,
      duration: "< 0.01 ms",
      status: "PASS",
      icon: <ShieldCheck className="h-3.5 w-3.5 text-violet-400" />,
    },
    {
      id: "exec",
      name: "4. Execution Pipeline Gate",
      description: `Subprocess / runner execution gate (${result.duration_ms.toFixed(1)} ms).`,
      duration: `${result.duration_ms.toFixed(1)} ms`,
      status: result.status,
      icon: <Clock className="h-3.5 w-3.5 text-emerald-400" />,
    },
    {
      id: "obs",
      name: "5. Observability & Telemetry",
      description: `Recorded execution event trace ID '${result.execution_id}'.`,
      duration: "< 0.01 ms",
      status: "PASS",
      icon: <Activity className="h-3.5 w-3.5 text-amber-400" />,
    },
  ]

  return (
    <div className="space-y-3 bg-[#0D1117] border border-border/40 rounded-xl p-4 font-mono text-xs">
      <div className="flex items-center justify-between border-b border-border/40 pb-2">
        <span className="font-bold text-foreground flex items-center gap-1.5">
          <Activity className="h-3.5 w-3.5 text-cyan-400" />
          Execution Stage Trace Timeline
        </span>
        <span className="text-[10px] text-muted-foreground">Trace ID: {result.execution_id}</span>
      </div>

      <div className="relative pl-4 space-y-3 before:absolute before:left-1.75 before:top-2 before:bottom-2 before:w-0.5 before:bg-border/50">
        {stages.map((stage) => (
          <div key={stage.id} className="relative flex items-start gap-2.5 group">
            <div className="absolute -left-4 top-0.5 p-1 bg-[#121826] border border-border/60 rounded-full">
              <CheckCircle2 className="h-3 w-3 text-emerald-400" />
            </div>

            <div className="flex-1 bg-secondary/20 hover:bg-secondary/40 border border-border/40 p-2.5 rounded-lg transition-all">
              <div className="flex items-center justify-between">
                <span className="font-bold text-foreground flex items-center gap-1.5">
                  {stage.icon}
                  {stage.name}
                </span>
                <span className="text-[10px] text-cyan-400 font-semibold">{stage.duration}</span>
              </div>
              <p className="text-[11px] text-muted-foreground mt-0.5 leading-relaxed">{stage.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
