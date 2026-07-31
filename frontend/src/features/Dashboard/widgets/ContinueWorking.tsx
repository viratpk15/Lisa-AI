import React, { useState } from "react"
import { motion } from "framer-motion"
import { Pin, Clock, Play, BarChart2 } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { dashboardCardVariants } from "@/lib/motion"

interface WorkspaceItem {
  id: string
  name: string
  scope: string
  lastOpened: string
  progress: number
  status: "active" | "standby" | "completed" | "halted"
  pinned: boolean
}

export const ContinueWorking: React.FC = () => {
  const [workspaces, setWorkspaces] = useState<WorkspaceItem[]>([
    {
      id: "ws-jarvis",
      name: "Jarvis AIOS",
      scope: "Core kernel structure & tool registration flow",
      lastOpened: "12 minutes ago",
      progress: 78,
      status: "active",
      pinned: true
    },
    {
      id: "ws-frontend",
      name: "Frontend UI",
      scope: "Framer-motion layouts & theme variables integration",
      lastOpened: "1 hour ago",
      progress: 60,
      status: "active",
      pinned: true
    },
    {
      id: "ws-neuron",
      name: "NeuroNet AI",
      scope: "Embeddings mapping & retrieval evaluation metrics",
      lastOpened: "Yesterday",
      progress: 45,
      status: "standby",
      pinned: false
    },
    {
      id: "ws-research",
      name: "LLM Research",
      scope: "Evaluation log analysis & prompt optimizations",
      lastOpened: "3 days ago",
      progress: 100,
      status: "completed",
      pinned: false
    }
  ])

  const togglePin = (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    setWorkspaces((prev) =>
      prev.map((ws) => (ws.id === id ? { ...ws, pinned: !ws.pinned } : ws))
    )
  }

  const getStatusBadge = (status: WorkspaceItem["status"]) => {
    switch (status) {
      case "active":
        return (
          <Badge className="text-[9px] font-mono bg-emerald-500/10 text-emerald-400 border-emerald-500/20 font-semibold px-2 py-0.5">
            ACTIVE
          </Badge>
        )
      case "standby":
        return (
          <Badge className="text-[9px] font-mono bg-zinc-500/10 text-zinc-400 border-zinc-500/20 font-semibold px-2 py-0.5">
            STANDBY
          </Badge>
        )
      case "completed":
        return (
          <Badge className="text-[9px] font-mono bg-blue-500/10 text-blue-400 border-blue-500/20 font-semibold px-2 py-0.5">
            COMPLETED
          </Badge>
        )
      case "halted":
        return (
          <Badge className="text-[9px] font-mono bg-red-500/10 text-red-400 border-red-500/20 font-semibold px-2 py-0.5">
            HALTED
          </Badge>
        )
    }
  }

  // Sort pinned first, then by lastOpened (order preserved from initial array)
  const sortedWorkspaces = [...workspaces].sort((a, b) => {
    if (a.pinned && !b.pinned) return -1
    if (!a.pinned && b.pinned) return 1
    return 0
  })

  return (
    <div id="continue-working-section" className="space-y-4 scroll-mt-20">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-sm font-mono font-semibold tracking-wider text-muted-foreground uppercase">
            Continue Working
          </h2>
          <p className="text-xs text-muted-foreground mt-0.5">Pick up where you left off. Memory layers remain cached.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {sortedWorkspaces.map((ws) => (
          <motion.div
            key={ws.id}
            variants={dashboardCardVariants}
            initial="initial"
            animate="animate"
            whileHover="hover"
            whileTap="tap"
          >
            <Card className="border-border/60 bg-card/25 backdrop-blur-md hover:border-primary/30 transition-all duration-300 relative group overflow-hidden h-full flex flex-col justify-between">
              <CardContent className="p-5 space-y-4 flex-1">
                {/* Header Row */}
                <div className="flex items-start justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm text-foreground group-hover:text-primary transition-colors">
                        {ws.name}
                      </span>
                      {ws.pinned && (
                        <Pin className="h-3 w-3 text-primary fill-primary/30 rotate-45" />
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground line-clamp-1">
                      {ws.scope}
                    </p>
                  </div>

                  <button
                    onClick={(e) => togglePin(ws.id, e)}
                    className="p-1 rounded hover:bg-secondary text-muted-foreground/60 hover:text-foreground cursor-pointer focus:outline-none transition-colors shrink-0"
                    title={ws.pinned ? "Unpin workspace" : "Pin workspace"}
                  >
                    <Pin className={`h-3.5 w-3.5 ${ws.pinned ? "fill-primary/20 text-primary rotate-45" : "text-muted-foreground/40 group-hover:text-muted-foreground/80"}`} />
                  </button>
                </div>

                {/* Progress bar */}
                <div className="space-y-1.5">
                  <div className="flex justify-between text-[10px] font-mono font-semibold">
                    <span className="text-muted-foreground flex items-center gap-1">
                      <BarChart2 className="h-3.5 w-3.5 text-primary" />
                      Compilation progress
                    </span>
                    <span className="text-foreground">{ws.progress}%</span>
                  </div>
                  <div className="h-1.5 w-full bg-secondary/50 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary rounded-full transition-all duration-500 ease-out"
                      style={{ width: `${ws.progress}%` }}
                    />
                  </div>
                </div>

                {/* Telemetry Row */}
                <div className="flex items-center justify-between border-t border-border/40 pt-3 text-[10px] font-mono">
                  <div className="flex items-center gap-1 text-muted-foreground">
                    <Clock className="h-3 w-3 text-primary/80" />
                    <span>{ws.lastOpened}</span>
                  </div>
                  {getStatusBadge(ws.status)}
                </div>
              </CardContent>

              {/* Action overlay on card hover */}
              <div className="absolute inset-0 bg-primary/2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
              
              <div className="absolute right-4 bottom-4 opacity-0 group-hover:opacity-100 transition-opacity">
                <Button size="icon-sm" className="h-7 w-7 rounded-full shadow-lg cursor-pointer">
                  <Play className="h-3 w-3 fill-current ml-0.5" />
                </Button>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
