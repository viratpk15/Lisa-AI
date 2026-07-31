import React from "react"
import { MessageSquare, Folder, Bookmark, Layers, Bot, Settings } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

interface TimelineEvent {
  id: string
  title: string
  description: string
  time: string
  type: "conversation" | "project" | "research" | "memory" | "agent" | "system"
}

export const Timeline: React.FC = () => {
  const events: TimelineEvent[] = [
    {
      id: "ev-1",
      title: "Agent Finished Execution",
      description: "Frontend Agent successfully resolved layout constraints for widgets/Hero.tsx and verified type safety.",
      time: "10 minutes ago",
      type: "agent"
    },
    {
      id: "ev-2",
      title: "Memory Index Updated",
      description: "Synchronized 14 new semantic vectors representing user project choices and context variables.",
      time: "32 minutes ago",
      type: "memory"
    },
    {
      id: "ev-3",
      title: "Conversation Created",
      description: "Initialized new conversation: 'Debug FastAPI memory leak in vector index cache' bound to Gemini 2.5 Pro.",
      time: "1 hour ago",
      type: "conversation"
    },
    {
      id: "ev-4",
      title: "Project Scope Updated",
      description: "Added file mapping path 'frontend/src/features/Dashboard/widgets' to Jarvis AIOS workspace context.",
      time: "2 hours ago",
      type: "project"
    },
    {
      id: "ev-5",
      title: "Deep Research Saved",
      description: "Saved web crawlers summaries on 'Vite React 19 Framer-Motion layout guide' (12 pages parsed).",
      time: "Yesterday",
      type: "research"
    }
  ]

  const getEventIcon = (type: TimelineEvent["type"]) => {
    const classStr = "h-3.5 w-3.5 text-foreground"
    switch (type) {
      case "agent":
        return <Bot className={classStr} />
      case "memory":
        return <Layers className={classStr} />
      case "conversation":
        return <MessageSquare className={classStr} />
      case "project":
        return <Folder className={classStr} />
      case "research":
        return <Bookmark className={classStr} />
      case "system":
        return <Settings className={classStr} />
    }
  }

  const getEventBadgeColor = (type: TimelineEvent["type"]) => {
    switch (type) {
      case "agent":
        return "border-emerald-500/20 bg-emerald-500/10 text-emerald-400"
      case "memory":
        return "border-blue-500/20 bg-blue-500/10 text-blue-400"
      case "conversation":
        return "border-primary/20 bg-primary/10 text-primary"
      case "project":
        return "border-amber-500/20 bg-amber-500/10 text-amber-400"
      case "research":
        return "border-violet-500/20 bg-violet-500/10 text-violet-400"
      case "system":
        return "border-zinc-500/20 bg-zinc-500/10 text-zinc-400"
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-sm font-mono font-semibold tracking-wider text-muted-foreground uppercase">
          Activity Feed
        </h2>
        <p className="text-xs text-muted-foreground mt-0.5">Chronological system kernel event timeline.</p>
      </div>

      <Card className="border-border/60 bg-card/25 backdrop-blur-md overflow-hidden relative">
        <CardContent className="p-5">
          <div className="relative border-l border-border/80 pl-6 space-y-6">
            
            {events.map((ev) => (
              <div key={ev.id} className="relative group">
                
                {/* Timeline Dot with Icon */}
                <div className={`absolute -left-8.75 top-0.5 p-1 rounded-md border flex items-center justify-center shadow-sm shrink-0 transition-transform duration-200 group-hover:scale-105 ${getEventBadgeColor(ev.type)}`}>
                  {getEventIcon(ev.type)}
                </div>

                {/* Content */}
                <div className="space-y-1">
                  <div className="flex items-center justify-between gap-4 flex-wrap">
                    <span className="font-bold text-xs text-foreground group-hover:text-primary transition-colors">
                      {ev.title}
                    </span>
                    <span className="text-[10px] font-mono text-muted-foreground">
                      {ev.time}
                    </span>
                  </div>
                  <p className="text-[11px] text-muted-foreground leading-relaxed">
                    {ev.description}
                  </p>
                </div>

              </div>
            ))}

          </div>
        </CardContent>
      </Card>
    </div>
  )
}
