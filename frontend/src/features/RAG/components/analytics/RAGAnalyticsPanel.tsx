import { Activity, TrendingUp, DollarSign, Clock, HardDrive } from "lucide-react"
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, BarChart, Bar } from "recharts"
import { useRAGAnalyticsQuery } from "../../services/ragApi"

export function RAGAnalyticsPanel() {
  const { data: analytics, isLoading } = useRAGAnalyticsQuery()

  const areaData = [
    { name: "Mon", queries: 140, latency: 12 },
    { name: "Tue", queries: 230, latency: 15 },
    { name: "Wed", queries: 310, latency: 11 },
    { name: "Thu", queries: 450, latency: 14 },
    { name: "Fri", queries: 380, latency: 13 },
  ]

  const barData = [
    { name: "Dense Vector", ms: 8 },
    { name: "BM25 Sparse", ms: 4 },
    { name: "Reranker", ms: 14 },
    { name: "Context Pack", ms: 2 },
  ]

  if (isLoading) return <div className="p-4 text-center text-xs text-muted-foreground animate-pulse">Loading analytics...</div>

  return (
    <div className="space-y-6">
      {/* Metric Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 font-mono text-xs">
        <div className="p-3 bg-secondary/20 border border-border/40 rounded-xl space-y-1">
          <span className="text-[10px] text-muted-foreground uppercase flex items-center gap-1">
            <Activity className="h-3 w-3 text-cyan-400" /> Total Queries
          </span>
          <div className="text-xl font-bold text-foreground">{analytics?.total_queries || 1512}</div>
        </div>

        <div className="p-3 bg-secondary/20 border border-border/40 rounded-xl space-y-1">
          <span className="text-[10px] text-muted-foreground uppercase flex items-center gap-1">
            <HardDrive className="h-3 w-3 text-violet-400" /> Indexed Vector Dimensions
          </span>
          <div className="text-xl font-bold text-violet-400">{analytics?.total_vectors || "6,328,320"}</div>
        </div>

        <div className="p-3 bg-secondary/20 border border-border/40 rounded-xl space-y-1">
          <span className="text-[10px] text-muted-foreground uppercase flex items-center gap-1">
            <Clock className="h-3 w-3 text-cyan-400" /> Avg Retrieval Latency
          </span>
          <div className="text-xl font-bold text-cyan-400">{analytics?.avg_latency_ms || 14.5} ms</div>
        </div>

        <div className="p-3 bg-secondary/20 border border-border/40 rounded-xl space-y-1">
          <span className="text-[10px] text-muted-foreground uppercase flex items-center gap-1">
            <DollarSign className="h-3 w-3 text-emerald-400" /> Vector Cost (USD)
          </span>
          <div className="text-xl font-bold text-emerald-400">${analytics?.total_cost_usd || 0.0034}</div>
        </div>
      </div>

      {/* Graphical Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        <div className="lg:col-span-8 p-4 bg-secondary/15 border border-border/40 rounded-xl space-y-3 font-mono text-xs">
          <span className="font-bold text-foreground flex items-center gap-1.5">
            <TrendingUp className="h-3.5 w-3.5 text-cyan-400" /> Daily Query Throughput
          </span>
          <div className="h-52 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={areaData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" stroke="#6B7280" fontSize={10} />
                <YAxis stroke="#6B7280" fontSize={10} />
                <Tooltip contentStyle={{ backgroundColor: "#121826", borderColor: "#1F293D", borderRadius: "8px", fontSize: "12px" }} />
                <Area type="monotone" dataKey="queries" stroke="#06B6D4" fill="#06B6D4" fillOpacity={0.2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="lg:col-span-4 p-4 bg-secondary/15 border border-border/40 rounded-xl space-y-3 font-mono text-xs">
          <span className="font-bold text-foreground">Pipeline Stage Latencies (ms)</span>
          <div className="h-52 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" stroke="#6B7280" fontSize={10} />
                <YAxis stroke="#6B7280" fontSize={10} />
                <Tooltip contentStyle={{ backgroundColor: "#121826", borderColor: "#1F293D", borderRadius: "8px", fontSize: "12px" }} />
                <Bar dataKey="ms" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}
