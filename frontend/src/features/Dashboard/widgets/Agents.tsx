import React from "react"
import { useNavigate } from "react-router"
import { motion } from "framer-motion"
import { Bot, Calendar, ClipboardList, CheckCircle2, Loader2 } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { dashboardCardVariants } from "@/lib/motion"

interface AgentItem {
  id: string
  name: string
  role: string
  status: "idle" | "working" | "waiting" | "completed"
  taskCount: number
  lastExecution: string
  avatarColor: string
  avatarText: string
  activeNode?: string
}

export const Agents: React.FC = () => {
  const navigate = useNavigate()

  const agents: AgentItem[] = [
    {
      id: "ag-planner",
      name: "Planner Agent",
      role: "Orchestrates graph nodes & decomposes tasks",
      status: "idle",
      taskCount: 0,
      lastExecution: "15 minutes ago",
      avatarColor: "bg-primary text-primary-foreground border-primary/20",
      avatarText: "PL"
    },
    {
      id: "ag-research",
      name: "Research Agent",
      role: "Surfs Google Search & extracts HTML summaries",
      status: "working",
      taskCount: 3,
      lastExecution: "Running now",
      avatarColor: "bg-blue-500/10 text-blue-400 border-blue-500/20",
      avatarText: "RE",
      activeNode: "crawl_web_pages"
    },
    {
      id: "ag-backend",
      name: "Backend Agent",
      role: "Generates FastAPI routers & resolves db queries",
      status: "waiting",
      taskCount: 1,
      lastExecution: "5 minutes ago",
      avatarColor: "bg-amber-500/10 text-amber-400 border-amber-500/20",
      avatarText: "BE",
      activeNode: "verify_migration_schema"
    },
    {
      id: "ag-frontend",
      name: "Frontend Agent",
      role: "Validates React 19 specs & Tailwind layouts",
      status: "completed",
      taskCount: 0,
      lastExecution: "32 minutes ago",
      avatarColor: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
      avatarText: "FE"
    },
    {
      id: "ag-testing",
      name: "Testing Agent",
      role: "Generates pytest suites & vitest modules",
      status: "idle",
      taskCount: 0,
      lastExecution: "1 hour ago",
      avatarColor: "bg-red-500/10 text-red-400 border-red-500/20",
      avatarText: "TE"
    },
    {
      id: "ag-doc",
      name: "Documentation Agent",
      role: "Syncs markdown schemas & updates walkthroughs",
      status: "completed",
      taskCount: 0,
      lastExecution: "Yesterday",
      avatarColor: "bg-violet-500/10 text-violet-400 border-violet-500/20",
      avatarText: "DO"
    }
  ]

  const getStatusBadge = (agent: AgentItem) => {
    switch (agent.status) {
      case "idle":
        return (
          <Badge variant="secondary" className="text-[9px] font-mono border-border/50 bg-secondary/80 text-muted-foreground font-semibold px-2 py-0.5">
            STANDBY
          </Badge>
        )
      case "working":
        return (
          <Badge className="text-[9px] font-mono bg-emerald-500/10 text-emerald-400 border-emerald-500/20 font-semibold px-2 py-0.5 gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
            EXECUTING
          </Badge>
        )
      case "waiting":
        return (
          <Badge className="text-[9px] font-mono bg-amber-500/10 text-amber-400 border-amber-500/20 font-semibold px-2 py-0.5 gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-amber-500 animate-ping" />
            WAITING
          </Badge>
        )
      case "completed":
        return (
          <Badge className="text-[9px] font-mono bg-blue-500/10 text-blue-400 border-blue-500/20 font-semibold px-2 py-0.5 gap-1.5">
            <CheckCircle2 className="h-2.5 w-2.5" />
            COMPLETED
          </Badge>
        )
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-sm font-mono font-semibold tracking-wider text-muted-foreground uppercase">
            Active Agents
          </h2>
          <p className="text-xs text-muted-foreground mt-0.5">LangGraph agent statuses and thread activity logs.</p>
        </div>
        <Button
          onClick={() => navigate("/agents")}
          variant="ghost"
          size="sm"
          className="text-xs gap-1 hover:text-primary cursor-pointer font-semibold py-0 h-7"
        >
          Manage
          <Bot className="h-3.5 w-3.5" />
        </Button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {agents.map((agent) => (
          <motion.div
            key={agent.id}
            variants={dashboardCardVariants}
            initial="initial"
            animate="animate"
            whileHover="hover"
            whileTap="tap"
          >
            <Card className="border-border/60 bg-card/25 backdrop-blur-md hover:border-primary/30 transition-all duration-300 relative group overflow-hidden h-full flex flex-col justify-between">
              <CardContent className="p-4 space-y-3.5">
                {/* Agent Header */}
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-2.5">
                    <div className={`h-8 w-8 rounded-lg border font-bold text-xs flex items-center justify-center shrink-0 shadow-sm ${agent.avatarColor}`}>
                      {agent.avatarText}
                    </div>
                    <div className="min-w-0">
                      <span className="font-bold text-xs text-foreground group-hover:text-primary transition-colors leading-none truncate block">
                        {agent.name}
                      </span>
                      <span className="text-[10px] text-muted-foreground leading-none mt-0.5 truncate block">
                        {agent.role}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Node Execution state */}
                {agent.activeNode && (
                  <div className="p-2 bg-secondary/30 rounded border border-border/40 font-mono text-[9px] flex items-center gap-1.5 text-muted-foreground">
                    <Loader2 className="h-3 w-3 text-primary animate-spin shrink-0" />
                    <span className="truncate">Node: <span className="text-foreground font-semibold">{agent.activeNode}</span></span>
                  </div>
                )}

                {/* Queue status */}
                <div className="flex items-center justify-between text-[10px] font-mono border-t border-border/40 pt-3">
                  <div className="flex items-center gap-1 text-muted-foreground">
                    <ClipboardList className="h-3 w-3 text-primary/80" />
                    <span>
                      {agent.taskCount > 0 ? `${agent.taskCount} tasks queued` : "No queue"}
                    </span>
                  </div>
                  {getStatusBadge(agent)}
                </div>

                {/* Execution timestamp */}
                <div className="flex items-center gap-1 text-[9px] font-mono text-muted-foreground/80">
                  <Calendar className="h-3 w-3 text-primary/60" />
                  <span>Last run: {agent.lastExecution}</span>
                </div>

              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
