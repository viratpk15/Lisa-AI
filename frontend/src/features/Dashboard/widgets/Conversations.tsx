import React from "react"
import { useNavigate } from "react-router"
import { motion } from "framer-motion"
import { MessageSquare, Pin, ArrowRight, Sparkles, BrainCircuit } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { dashboardCardVariants } from "@/lib/motion"

interface ConversationItem {
  id: string
  title: string
  preview: string
  time: string
  pinned: boolean
  model: string
  isStreaming: boolean
}

export const Conversations: React.FC = () => {
  const navigate = useNavigate()

  const conversations: ConversationItem[] = [
    {
      id: "c1",
      title: "Debug FastAPI memory leak in vector index cache",
      preview: "We analyzed the heap allocations and found that the index registry wasn't garbage collecting old scopes...",
      time: "10 minutes ago",
      pinned: true,
      model: "Gemini 2.5 Pro",
      isStreaming: true
    },
    {
      id: "c2",
      title: "Integrate framer-motion page variants in app shell",
      preview: "Can you list the standard motion configurations loaded from src/lib/motion.ts and ensure they match...",
      time: "2 hours ago",
      pinned: true,
      model: "Gemini 2.5 Flash",
      isStreaming: false
    },
    {
      id: "c3",
      title: "Draft system prompt instructions for agents",
      preview: "Initialize the OS guide using AGENTS.md rules. Specify LangGraph composition over business duplication...",
      time: "Yesterday",
      pinned: false,
      model: "Gemini 2.5 Pro",
      isStreaming: false
    }
  ]

  const handleContinue = (id: string) => {
    navigate(`/workspace?session_id=${id}`, { state: { sessionId: id } })
  }

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-sm font-mono font-semibold tracking-wider text-muted-foreground uppercase">
          Recent Conversations
        </h2>
        <p className="text-xs text-muted-foreground mt-0.5">Quick access to active dialog threads and model prompts.</p>
      </div>

      <div className="space-y-3">
        {conversations.map((chat) => (
          <motion.div
            key={chat.id}
            variants={dashboardCardVariants}
            initial="initial"
            animate="animate"
            whileHover="hover"
            whileTap="tap"
          >
            <Card className="border-border/60 bg-card/25 backdrop-blur-md hover:border-primary/30 transition-all duration-300 relative group overflow-hidden">
              <CardContent className="p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                
                {/* Information zone */}
                <div className="space-y-1.5 flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <div className="p-1 rounded bg-secondary/50 border border-border/40 text-primary shrink-0">
                      <MessageSquare className="h-3.5 w-3.5" />
                    </div>
                    <span className="font-bold text-xs text-foreground group-hover:text-primary transition-colors truncate max-w-70 sm:max-w-100">
                      {chat.title}
                    </span>
                    {chat.pinned && (
                      <Pin className="h-3 w-3 text-primary fill-primary/30 rotate-45 shrink-0" />
                    )}
                    {chat.isStreaming && (
                      <span className="inline-flex items-center gap-1 text-[9px] font-mono text-emerald-400 bg-emerald-400/5 px-2 py-0.5 rounded border border-emerald-400/15">
                        <BrainCircuit className="h-2.5 w-2.5 animate-pulse" />
                        STREAMING
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] text-muted-foreground truncate leading-relaxed">
                    {chat.preview}
                  </p>
                </div>

                {/* Meta tags and Actions */}
                <div className="flex items-center gap-3 sm:self-center shrink-0 w-full sm:w-auto justify-between sm:justify-start border-t sm:border-t-0 border-border/40 pt-2 sm:pt-0">
                  <div className="flex items-center gap-2 text-[10px] font-mono">
                    <span className="text-muted-foreground">{chat.time}</span>
                    <Badge variant="outline" className="text-[9px] bg-secondary/50 border-border/60 font-mono gap-1 text-muted-foreground">
                      <Sparkles className="h-2.5 w-2.5 text-primary" />
                      {chat.model}
                    </Badge>
                  </div>
                  <Button
                    onClick={() => handleContinue(chat.id)}
                    variant="ghost"
                    size="sm"
                    className="h-7 text-xs gap-1 hover:text-primary cursor-pointer font-semibold py-0"
                  >
                    Open
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Button>
                </div>

              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
