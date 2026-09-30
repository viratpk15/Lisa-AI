import { useNavigate } from "react-router"
import { Activity, ArrowLeft, ShieldCheck } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function ObservabilityPage() {
  const navigate = useNavigate()

  return (
    <div className="max-w-4xl mx-auto space-y-6 py-2">
      <Button
        variant="ghost"
        size="sm"
        onClick={() => navigate("/settings/developer")}
        className="text-xs text-muted-foreground hover:text-foreground -ml-2 cursor-pointer gap-1.5"
      >
        <ArrowLeft className="h-3.5 w-3.5" />
        <span>Back to Developer Portal</span>
      </Button>

      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Observability & Tracing</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Inspect execution traces, tool call latencies, and agent graph states.
        </p>
      </div>

      <div className="p-4 rounded-xl border border-border/50 bg-secondary/20 flex items-start gap-3">
        <ShieldCheck className="h-5 w-5 text-primary shrink-0 mt-0.5" />
        <div className="space-y-1">
          <p className="text-xs font-semibold text-foreground">Execution Audit Traces</p>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Every step taken by an agent team, supervisor node, or tool execution is logged with sub-millisecond precision for auditing and debugging.
          </p>
        </div>
      </div>

      <Card className="border-border/70 bg-card/50 shadow-xs">
        <CardHeader>
          <CardTitle className="text-base font-semibold">Recent Execution Traces</CardTitle>
          <CardDescription>Live session traces and pipeline runs recorded by the runtime.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="py-12 text-center space-y-3">
            <div className="p-3 rounded-full bg-secondary/50 border border-border/40 w-fit mx-auto text-muted-foreground">
              <Activity className="h-6 w-6" />
            </div>
            <div className="space-y-1">
              <p className="text-sm font-semibold text-foreground">No runs recorded yet</p>
              <p className="text-xs text-muted-foreground max-w-sm mx-auto">
                No active background agent traces or workflow runs have been captured in this environment.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
