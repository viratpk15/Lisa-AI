import React from "react"
import { Sparkles, Mail, FileText, Calendar, Search } from "lucide-react"

interface EmptyStateProps {
  onSelectPrompt: (prompt: string) => void
  onNewChat: () => void
}

export const EmptyState: React.FC<EmptyStateProps> = ({ onSelectPrompt }) => {
  const suggestions = [
    {
      text: "What's important in my email today?",
      desc: "Check urgent messages and action items",
      icon: Mail,
    },
    {
      text: "Summarize my latest files",
      desc: "Review uploaded knowledge and documents",
      icon: FileText,
    },
    {
      text: "Help me plan my day",
      desc: "Organize tasks and prioritize upcoming deadlines",
      icon: Calendar,
    },
    {
      text: "Research something for me",
      desc: "Ask questions, analyze concepts, or synthesize topics",
      icon: Search,
    },
  ]

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 sm:p-8 max-w-2xl mx-auto text-center h-full select-none">
      {/* Lisa Brand Avatar Visual */}
      <div className="relative mb-6 flex items-center justify-center">
        <div className="absolute inset-0 h-20 w-20 bg-primary/10 rounded-full blur-xl animate-pulse" />
        <div className="relative border border-primary/20 bg-card/60 backdrop-blur px-5 py-5 rounded-2xl flex items-center justify-center shadow-lg">
          <Sparkles className="h-10 w-10 text-primary" />
        </div>
      </div>

      <h2 className="text-2xl font-bold tracking-tight text-foreground">
        Hi, I'm Lisa.
      </h2>
      
      <p className="text-xs sm:text-sm text-muted-foreground mt-2 max-w-md leading-relaxed">
        I can help you understand your email, work with your files, research information, and get things done.
      </p>

      {/* Suggested prompts grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full mt-8">
        {suggestions.map((item, idx) => {
          const Icon = item.icon
          return (
            <button
              key={idx}
              onClick={() => onSelectPrompt(item.text)}
              className="p-3.5 text-left bg-secondary/20 hover:bg-secondary/50 border border-border/60 hover:border-primary/40 rounded-xl transition-all duration-200 group outline-none focus-visible:ring-1 focus-visible:ring-primary cursor-pointer flex gap-3 items-start shadow-xs"
            >
              <div className="p-2 rounded-lg bg-primary/10 text-primary shrink-0 group-hover:scale-105 transition-transform mt-0.5">
                <Icon className="h-4 w-4" />
              </div>
              <div className="space-y-0.5 min-w-0">
                <p className="text-xs font-semibold text-foreground group-hover:text-primary transition-colors leading-snug">
                  {item.text}
                </p>
                <p className="text-[11px] text-muted-foreground line-clamp-1">
                  {item.desc}
                </p>
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
