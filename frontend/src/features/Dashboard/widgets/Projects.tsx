import React from "react"
import { motion } from "framer-motion"
import { Folder, ArrowRight, AlertCircle, PlayCircle, Loader2 } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { dashboardCardVariants } from "@/lib/motion"

interface ProjectItem {
  id: string
  name: string
  description: string
  category: string
  tasksCompleted: number
  tasksTotal: number
  priority: "high" | "medium" | "low"
  status: "in_progress" | "review" | "paused"
  activity: string
}

export const Projects: React.FC = () => {
  const projects: ProjectItem[] = [
    {
      id: "p1",
      name: "Jarvis AIOS Kernel",
      description: "FastAPI endpoints, tool registry engine, memory sync",
      category: "Backend / OS",
      tasksCompleted: 24,
      tasksTotal: 28,
      priority: "high",
      status: "in_progress",
      activity: "Optimized tool retrieval loops (10m ago)"
    },
    {
      id: "p2",
      name: "Cognitive Frontend UI",
      description: "Dynamic React 19 app shell with Framer-motion widgets",
      category: "Frontend",
      tasksCompleted: 14,
      tasksTotal: 20,
      priority: "high",
      status: "in_progress",
      activity: "Created Welcome Hero layout (1h ago)"
    },
    {
      id: "p3",
      name: "NeuroNet Indexer",
      description: "Local database embeddings mapping & evaluations",
      category: "ML Ops",
      tasksCompleted: 8,
      tasksTotal: 18,
      priority: "medium",
      status: "review",
      activity: "Ran evaluation sweep for 1536d models (Yesterday)"
    },
    {
      id: "p4",
      name: "Autonomous Web Agent",
      description: "LangGraph-driven scraper & summarization engine",
      category: "Intelligence",
      tasksCompleted: 5,
      tasksTotal: 15,
      priority: "low",
      status: "paused",
      activity: "Halted due to browser authorization errors (3d ago)"
    }
  ]

  const getPriorityBadge = (prio: ProjectItem["priority"]) => {
    switch (prio) {
      case "high":
        return (
          <span className="inline-flex items-center gap-1 text-[9px] font-mono text-red-400 bg-red-400/5 px-2 py-0.5 rounded border border-red-400/15">
            <span className="h-1 w-1 rounded-full bg-red-500 animate-pulse" />
            CRITICAL
          </span>
        )
      case "medium":
        return (
          <span className="inline-flex items-center gap-1 text-[9px] font-mono text-amber-400 bg-amber-400/5 px-2 py-0.5 rounded border border-amber-400/15">
            <span className="h-1 w-1 rounded-full bg-amber-500" />
            HIGH
          </span>
        )
      case "low":
        return (
          <span className="inline-flex items-center gap-1 text-[9px] font-mono text-blue-400 bg-blue-400/5 px-2 py-0.5 rounded border border-blue-400/15">
            <span className="h-1 w-1 rounded-full bg-blue-500" />
            STANDARD
          </span>
        )
    }
  }

  const getStatusIcon = (status: ProjectItem["status"]) => {
    switch (status) {
      case "in_progress":
        return <Loader2 className="h-3.5 w-3.5 text-primary animate-spin" />
      case "review":
        return <PlayCircle className="h-3.5 w-3.5 text-amber-400" />
      case "paused":
        return <AlertCircle className="h-3.5 w-3.5 text-zinc-400" />
    }
  }

  const getStatusText = (status: ProjectItem["status"]) => {
    switch (status) {
      case "in_progress":
        return "Executing"
      case "review":
        return "Review"
      case "paused":
        return "Standby"
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-sm font-mono font-semibold tracking-wider text-muted-foreground uppercase">
            Active Projects
          </h2>
          <p className="text-xs text-muted-foreground mt-0.5">Monitor progress metrics and execution threads across all projects.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {projects.map((proj) => {
          const pct = Math.round((proj.tasksCompleted / proj.tasksTotal) * 100)
          return (
            <motion.div
              key={proj.id}
              variants={dashboardCardVariants}
              initial="initial"
              animate="animate"
              whileHover="hover"
              whileTap="tap"
            >
              <Card className="border-border/60 bg-card/25 backdrop-blur-md hover:border-primary/30 transition-all duration-300 relative group overflow-hidden h-full flex flex-col justify-between">
                <CardContent className="p-5 space-y-4">
                  {/* Title & Icon row */}
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-secondary/50 rounded-lg text-primary border border-border/40 shrink-0">
                        <Folder className="h-4 w-4" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-sm text-foreground group-hover:text-primary transition-colors leading-none">
                            {proj.name}
                          </span>
                        </div>
                        <span className="text-[10px] text-muted-foreground mt-1 block">
                          {proj.category}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      {getPriorityBadge(proj.priority)}
                    </div>
                  </div>

                  <p className="text-xs text-muted-foreground leading-relaxed">
                    {proj.description}
                  </p>

                  {/* Task counts & Progress progress bar */}
                  <div className="space-y-2">
                    <div className="flex justify-between items-center text-[10px] font-mono font-semibold">
                      <div className="flex items-center gap-1.5 text-muted-foreground">
                        {getStatusIcon(proj.status)}
                        <span>{getStatusText(proj.status)}</span>
                      </div>
                      <span className="text-foreground">
                        {proj.tasksCompleted}/{proj.tasksTotal} Tasks ({pct}%)
                      </span>
                    </div>
                    <div className="h-1.5 w-full bg-secondary/50 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary rounded-full transition-all duration-500 ease-out"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>

                  {/* Recent activities footer */}
                  <div className="border-t border-border/40 pt-3 flex items-center justify-between text-[10px] font-mono">
                    <span className="text-muted-foreground truncate max-w-50" title={proj.activity}>
                      {proj.activity}
                    </span>
                    <span className="text-primary hover:text-primary-foreground flex items-center gap-0.5 cursor-pointer hover:underline transition-colors shrink-0">
                      Files
                      <ArrowRight className="h-3 w-3" />
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
