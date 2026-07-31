import React from "react"
import { motion } from "framer-motion"
import { Cpu, Sparkles, Database, Layers, Search, ToyBrick, Check } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { dashboardCardVariants } from "@/lib/motion"

interface TelemetryItem {
  id: string
  name: string
  icon: typeof Cpu
  status: "nominal" | "warning" | "error"
  latency: string
  load: string
  metric: string
  metricLabel: string
  color: string
}

export const SystemHealth: React.FC = () => {
  const subsystems: TelemetryItem[] = [
    {
      id: "sys-backend",
      name: "FastAPI Core Kernel",
      icon: Cpu,
      status: "nominal",
      latency: "2ms",
      load: "4% CPU",
      metric: "99.98%",
      metricLabel: "Uptime",
      color: "text-emerald-500 bg-emerald-500/10 border-emerald-500/20"
    },
    {
      id: "sys-model",
      name: "Model Registry API",
      icon: Sparkles,
      status: "nominal",
      latency: "142ms",
      load: "Standby",
      metric: "98.7%",
      metricLabel: "Inference Success",
      color: "text-violet-500 bg-violet-500/10 border-violet-500/20"
    },
    {
      id: "sys-memory",
      name: "Memory Bus Manager",
      icon: Layers,
      status: "nominal",
      latency: "1ms",
      load: "1.2 GB / 8 GB",
      metric: "15%",
      metricLabel: "Load",
      color: "text-blue-500 bg-blue-500/10 border-blue-500/20"
    },
    {
      id: "sys-vectordb",
      name: "Vector Database Index",
      icon: Database,
      status: "nominal",
      latency: "8ms",
      load: "1,824 vectors cached",
      metric: "Sync",
      metricLabel: "Database Status",
      color: "text-amber-500 bg-amber-500/10 border-amber-500/20"
    },
    {
      id: "sys-search",
      name: "Search Crawler Agent",
      icon: Search,
      status: "nominal",
      latency: "320ms",
      load: "Idle",
      metric: "Ok",
      metricLabel: "Connectivity",
      color: "text-rose-500 bg-rose-500/10 border-rose-500/20"
    },
    {
      id: "sys-tools",
      name: "Client Tool Engine",
      icon: ToyBrick,
      status: "nominal",
      latency: "3ms",
      load: "28 modules registered",
      metric: "Ready",
      metricLabel: "Tool Status",
      color: "text-pink-500 bg-pink-500/10 border-pink-500/20"
    }
  ]

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-sm font-mono font-semibold tracking-wider text-muted-foreground uppercase">
          System Health Telemetry
        </h2>
        <p className="text-xs text-muted-foreground mt-0.5">Real-time status loops for active kernel threads and memory registers.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-4">
        {subsystems.map((sub) => {
          const Icon = sub.icon
          return (
            <motion.div
              key={sub.id}
              variants={dashboardCardVariants}
              initial="initial"
              animate="animate"
              whileHover="hover"
              whileTap="tap"
            >
              <Card className="border-border/60 bg-card/25 backdrop-blur-md hover:border-primary/30 transition-all duration-300 relative group overflow-hidden">
                <CardContent className="p-4 space-y-3">
                  
                  {/* Subsystem identity */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className={`p-1.5 rounded border ${sub.color}`}>
                        <Icon className="h-3.5 w-3.5" />
                      </div>
                      <span className="font-bold text-xs text-foreground group-hover:text-primary transition-colors truncate">
                        {sub.name}
                      </span>
                    </div>

                    <span className="flex h-2 w-2 relative shrink-0">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                  </div>

                  {/* Metrics details */}
                  <div className="grid grid-cols-2 gap-2 pt-1 font-mono text-[10px]">
                    <div className="p-2 bg-secondary/35 border border-border/40 rounded flex flex-col justify-between">
                      <span className="text-muted-foreground leading-none">Latency</span>
                      <span className="text-foreground font-bold mt-1.5">{sub.latency}</span>
                    </div>
                    <div className="p-2 bg-secondary/35 border border-border/40 rounded flex flex-col justify-between">
                      <span className="text-muted-foreground leading-none">{sub.metricLabel}</span>
                      <span className="text-foreground font-bold mt-1.5">{sub.metric}</span>
                    </div>
                  </div>

                  {/* Load bar or text */}
                  <div className="flex items-center justify-between text-[9px] font-mono text-muted-foreground/80 border-t border-border/40 pt-2.5">
                    <span className="truncate">{sub.load}</span>
                    <span className="text-emerald-400 font-semibold flex items-center gap-0.5">
                      <Check className="h-2.5 w-2.5" />
                      Nominal
                    </span>
                  </div>

                </CardContent>
              </Card>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
