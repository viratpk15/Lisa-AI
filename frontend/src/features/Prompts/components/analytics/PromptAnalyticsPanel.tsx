import { Activity, TrendingUp, DollarSign, Clock, CheckCircle2 } from "lucide-react"
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, BarChart, Bar } from "recharts"
import { usePromptAnalyticsQuery } from "../../services/promptsApi"

export function PromptAnalyticsPanel() {
  const { data: analytics, isLoading } = usePromptAnalyticsQuery()

  const areaData = [
    { name: "Mon", calls: 12, cost: 0.0012, latency: 120 },
    { name: "Tue", calls: 19, cost: 0.0024, latency: 135 },
    { name: "Wed", calls: 25, cost: 0.0031, latency: 110 },
    { name: "Thu", calls: 32, cost: 0.0042, latency: 128 },
    { name: "Fri", calls: 28, cost: 0.0038, latency: 115 },
  ]

  const barData = Object.entries(analytics?.model_distribution || { "gpt-4o": 4, "claude-3.5-sonnet": 2 }).map(([k, v]) => ({
    model: k,
    count: v,
  }))

  if (isLoading) return <div className="p-4 text-center text-xs text-muted-foreground animate-pulse">Loading analytics...</div>

  return (
    <div className="space-y-6">
      {/* Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 font-mono text-xs">
        <div className="p-3 bg-secondary/20 border border-border/40 rounded-xl space-y-1">
          <span className="text-[10px] text-muted-foreground uppercase flex items-center gap-1">
            <Activity className="h-3 w-3 text-cyan-400" /> Total Executions
          </span>
          <div className="text-xl font-bold text-foreground">{analytics?.total_executions || 24}</div>
        </div>

        <div className="p-3 bg-secondary/20 border border-border/40 rounded-xl space-y-1">
          <span className="text-[10px] text-muted-foreground uppercase flex items-center gap-1">
            <CheckCircle2 className="h-3 w-3 text-emerald-400" /> Success Rate
          </span>
          <div className="text-xl font-bold text-emerald-400">{analytics?.success_rate || 100}%</div>
        </div>

        <div className="p-3 bg-secondary/20 border border-border/40 rounded-xl space-y-1">
          <span className="text-[10px] text-muted-foreground uppercase flex items-center gap-1">
            <Clock className="h-3 w-3 text-violet-400" /> Avg Latency
          </span>
          <div className="text-xl font-bold text-cyan-400">{analytics?.avg_latency_ms || 124} ms</div>
        </div>

        <div className="p-3 bg-secondary/20 border border-border/40 rounded-xl space-y-1">
          <span className="text-[10px] text-muted-foreground uppercase flex items-center gap-1">
            <DollarSign className="h-3 w-3 text-emerald-400" /> Total Spend
          </span>
          <div className="text-xl font-bold text-emerald-400">${analytics?.total_cost_usd || 0.0042}</div>
        </div>
      </div>

      {/* Recharts Graphical Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        <div className="lg:col-span-8 p-4 bg-secondary/15 border border-border/40 rounded-xl space-y-3 font-mono text-xs">
          <div className="flex items-center justify-between">
            <span className="font-bold text-foreground flex items-center gap-1.5">
              <TrendingUp className="h-3.5 w-3.5 text-cyan-400" /> Execution Volume & Latency Trend
            </span>
          </div>

          <div className="h-52 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={areaData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" stroke="#6B7280" fontSize={10} />
                <YAxis stroke="#6B7280" fontSize={10} />
                <Tooltip contentStyle={{ backgroundColor: "#121826", borderColor: "#1F293D", borderRadius: "8px", fontSize: "12px" }} />
                <Area type="monotone" dataKey="calls" stroke="#06B6D4" fill="#06B6D4" fillOpacity={0.2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="lg:col-span-4 p-4 bg-secondary/15 border border-border/40 rounded-xl space-y-3 font-mono text-xs">
          <span className="font-bold text-foreground">Model Distribution</span>
          <div className="h-52 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="model" stroke="#6B7280" fontSize={10} />
                <YAxis stroke="#6B7280" fontSize={10} />
                <Tooltip contentStyle={{ backgroundColor: "#121826", borderColor: "#1F293D", borderRadius: "8px", fontSize: "12px" }} />
                <Bar dataKey="count" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}
