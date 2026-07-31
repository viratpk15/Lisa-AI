import React from "react"
import { useNavigate } from "react-router"
import { motion } from "framer-motion"
import {
  MessageSquare,
  FolderPlus,
  Upload,
  Search,
  Brain,
  Bot,
  ScrollText,
  Compass
} from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { dashboardCardVariants } from "@/lib/motion"

interface QuickActionItem {
  id: string
  title: string
  subtitle: string
  icon: typeof MessageSquare
  color: string
  path: string
  action?: () => void
}

export const QuickActions: React.FC = () => {
  const navigate = useNavigate()

  const actions: QuickActionItem[] = [
    {
      id: "new-chat",
      title: "New Conversation",
      subtitle: "Initialize a new cognitive session",
      icon: MessageSquare,
      color: "text-primary bg-primary/10 border-primary/20",
      path: "/workspace"
    },
    {
      id: "new-project",
      title: "New Project",
      subtitle: "Map directory and set project scopes",
      icon: FolderPlus,
      color: "text-blue-500 bg-blue-500/10 border-blue-500/20",
      path: "/workspace"
    },
    {
      id: "upload-files",
      title: "Upload Files",
      subtitle: "Feed text documents to context engine",
      icon: Upload,
      color: "text-emerald-500 bg-emerald-500/10 border-emerald-500/20",
      path: "/files"
    },
    {
      id: "research",
      title: "Deep Research",
      subtitle: "Instruct web agent to crawl & summarize",
      icon: Compass,
      color: "text-violet-500 bg-violet-500/10 border-violet-500/20",
      path: "/agents"
    },
    {
      id: "planner",
      title: "Agent Planner",
      subtitle: "Decompose tasks into graph plans",
      icon: ScrollText,
      color: "text-amber-500 bg-amber-500/10 border-amber-500/20",
      path: "/agents"
    },
    {
      id: "search",
      title: "Global Search",
      subtitle: "Lookup in vector and filesystem stores",
      icon: Search,
      color: "text-sky-500 bg-sky-500/10 border-sky-500/20",
      path: "/files",
      action: () => {
        const event = new CustomEvent("open-command-palette")
        window.dispatchEvent(event)
      }
    },
    {
      id: "memory",
      title: "Semantic Memory",
      subtitle: "Inspect session history & cache",
      icon: Brain,
      color: "text-pink-500 bg-pink-500/10 border-pink-500/20",
      path: "/memory"
    },
    {
      id: "agents",
      title: "Active Agents",
      subtitle: "Monitor LangGraph state machine status",
      icon: Bot,
      color: "text-rose-500 bg-rose-500/10 border-rose-500/20",
      path: "/agents"
    }
  ]

  const handleAction = (item: QuickActionItem) => {
    if (item.action) {
      item.action()
    } else {
      navigate(item.path)
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-sm font-mono font-semibold tracking-wider text-muted-foreground uppercase">
          Quick Actions
        </h2>
        <p className="text-xs text-muted-foreground mt-0.5">Quickly trigger core OS subroutines or navigate features.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {actions.map((item) => {
          const Icon = item.icon
          return (
            <motion.div
              key={item.id}
              variants={dashboardCardVariants}
              initial="initial"
              animate="animate"
              whileHover="hover"
              whileTap="tap"
              className="h-full"
            >
              <Card
                onClick={() => handleAction(item)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault()
                    handleAction(item)
                  }
                }}
                tabIndex={0}
                className="h-full border-border/60 bg-card/25 backdrop-blur-md hover:border-primary/30 transition-all duration-300 cursor-pointer outline-none focus-visible:ring-1 focus-visible:ring-primary flex flex-col justify-between group overflow-hidden"
              >
                <CardContent className="p-4 flex flex-col gap-3">
                  <div className={`p-2.5 rounded-lg border w-fit ${item.color} group-hover:scale-105 transition-transform duration-300`}>
                    <Icon className="h-4 w-4" />
                  </div>
                  <div className="space-y-1">
                    <h3 className="text-xs font-bold text-foreground group-hover:text-primary transition-colors">
                      {item.title}
                    </h3>
                    <p className="text-[10px] text-muted-foreground leading-relaxed">
                      {item.subtitle}
                    </p>
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
