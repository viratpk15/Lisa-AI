import React from "react"
import { motion } from "framer-motion"
import { Compass, Sparkles, Database, Layers, CheckCircle2, TrendingUp } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { dashboardCardVariants } from "@/lib/motion"

export const Insights: React.FC = () => {
  const models = [
    { name: "Gemini 2.5 Pro", usage: 72 },
    { name: "Gemini 2.5 Flash", usage: 20 },
    { name: "Claude 3.5 Sonnet", usage: 8 }
  ]

  const frequentProjects = [
    { name: "Jarvis AIOS Kernel", count: 48, pct: 100 },
    { name: "Cognitive Frontend UI", count: 24, pct: 50 },
    { name: "NeuroNet Indexer", count: 12, pct: 25 }
  ]

  // Mock path points for memory usage SVG curve representing vector index growth
  const sparklineData = "M 0 45 Q 25 35 50 40 T 100 25 T 150 15 T 200 8"

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-sm font-mono font-semibold tracking-wider text-muted-foreground uppercase">
          Knowledge Insights
        </h2>
        <p className="text-xs text-muted-foreground mt-0.5">Statistical projections from memory registers and model audits.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-4">
        {/* Most Used Models */}
        <motion.div variants={dashboardCardVariants} initial="initial" animate="animate" whileHover="hover" whileTap="tap">
          <Card className="border-border/60 bg-card/25 backdrop-blur-md hover:border-primary/30 transition-all duration-300 h-full">
            <CardContent className="p-4.5 space-y-4.5">
              <div className="flex items-center gap-2 border-b border-border/40 pb-2">
                <Sparkles className="h-4 w-4 text-primary" />
                <span className="font-bold text-xs text-foreground">Model Load Weights</span>
              </div>
              <div className="space-y-3">
                {models.map((m) => (
                  <div key={m.name} className="space-y-1">
                    <div className="flex justify-between text-[10px] font-mono">
                      <span className="text-muted-foreground">{m.name}</span>
                      <span className="text-foreground font-semibold">{m.usage}%</span>
                    </div>
                    <div className="h-1.5 w-full bg-secondary/50 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary rounded-full transition-all duration-500"
                        style={{ width: `${m.usage}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Vector Memory Usage sparkline */}
        <motion.div variants={dashboardCardVariants} initial="initial" animate="animate" whileHover="hover" whileTap="tap">
          <Card className="border-border/60 bg-card/25 backdrop-blur-md hover:border-primary/30 transition-all duration-300 h-full">
            <CardContent className="p-4.5 space-y-4.5 flex flex-col justify-between h-full">
              <div>
                <div className="flex items-center gap-2 border-b border-border/40 pb-2">
                  <Database className="h-4 w-4 text-primary" />
                  <span className="font-bold text-xs text-foreground">Memory Vector Capacity</span>
                </div>
                <div className="flex items-end justify-between gap-4 pt-3">
                  <div className="space-y-1">
                    <span className="font-mono text-xl font-bold tracking-tight text-foreground block">
                      1,824
                    </span>
                    <span className="text-[10px] font-mono text-muted-foreground">
                      Active nodes in semantic cache
                    </span>
                  </div>

                  {/* Sparkline Vector Index plot */}
                  <div className="w-30 h-10 shrink-0">
                    <svg viewBox="0 0 200 50" className="w-full h-full overflow-visible">
                      <path
                        d={sparklineData}
                        fill="none"
                        stroke="hsl(var(--primary))"
                        strokeWidth="2.5"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                      <circle cx="200" cy="8" r="3.5" fill="hsl(var(--primary))" className="animate-pulse" />
                    </svg>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between text-[9px] font-mono text-muted-foreground border-t border-border/40 pt-2.5 mt-2">
                <span>Total buffer allocated: 8.0 GB</span>
                <span className="text-emerald-400 flex items-center gap-0.5 font-semibold">
                  <TrendingUp className="h-3 w-3" />
                  Stable Growth
                </span>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Frequently Accessed Projects */}
        <motion.div variants={dashboardCardVariants} initial="initial" animate="animate" whileHover="hover" whileTap="tap">
          <Card className="border-border/60 bg-card/25 backdrop-blur-md hover:border-primary/30 transition-all duration-300 h-full">
            <CardContent className="p-4.5 space-y-4.5">
              <div className="flex items-center gap-2 border-b border-border/40 pb-2">
                <Compass className="h-4 w-4 text-primary" />
                <span className="font-bold text-xs text-foreground">Frequent Projects</span>
              </div>
              <div className="space-y-3.5">
                {frequentProjects.map((p) => (
                  <div key={p.name} className="flex items-center justify-between gap-4">
                    <div className="min-w-0">
                      <span className="font-bold text-xs text-foreground block truncate">
                        {p.name}
                      </span>
                    </div>
                    <span className="text-[10px] font-mono font-semibold text-muted-foreground bg-secondary/80 border border-border/50 px-2 py-0.5 rounded shrink-0">
                      {p.count} hits
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Learning Progress tracker */}
        <motion.div variants={dashboardCardVariants} initial="initial" animate="animate" whileHover="hover" whileTap="tap">
          <Card className="border-border/60 bg-card/25 backdrop-blur-md hover:border-primary/30 transition-all duration-300 h-full">
            <CardContent className="p-4.5 space-y-4.5 flex flex-col justify-between h-full">
              <div>
                <div className="flex items-center gap-2 border-b border-border/40 pb-2">
                  <Layers className="h-4 w-4 text-primary" />
                  <span className="font-bold text-xs text-foreground">AOS Learning Progress</span>
                </div>
                <div className="pt-3.5 space-y-2">
                  <div className="flex items-center gap-2 text-xs">
                    <CheckCircle2 className="h-4 w-4 text-primary" />
                    <div className="min-w-0">
                      <span className="font-bold text-xs text-foreground block leading-none">
                        Kernel optimizations mapped
                      </span>
                      <span className="text-[9px] font-mono text-muted-foreground mt-0.5 block">
                        9/10 subsystems complete
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between text-[9px] font-mono text-muted-foreground border-t border-border/40 pt-2.5 mt-2">
                <span>Evaluated scopes: 12 files</span>
                <span className="text-primary font-semibold">90% Complete</span>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}
