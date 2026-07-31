import { Bot, MessageSquarePlus, Compass } from "lucide-react"

interface EmptyStateProps {
  onSelectPrompt: (prompt: string) => void
  onNewChat: () => void
}

export const EmptyState: React.FC<EmptyStateProps> = ({ onSelectPrompt, onNewChat }) => {
  const suggestions = [
    "Review standard security rules in docs/09_SECURITY.md",
    "Generate Pytest units for the FastAPI memory indexes",
    "Identify optimization paths for AppShell layout updates",
    "Draft a walkthrough for vector registry migrations"
  ]

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8 max-w-2xl mx-auto text-center h-full select-none">
      {/* Visual illustration: Pulse rings with cognitive kernel symbol */}
      <div className="relative mb-6 flex items-center justify-center">
        <div className="absolute inset-0 h-20 w-20 bg-primary/10 rounded-full blur-xl animate-pulse" />
        <div className="relative border border-primary/20 bg-card/45 backdrop-blur px-5 py-5 rounded-2xl flex items-center justify-center shadow-lg">
          <Bot className="h-10 w-10 text-primary" />
        </div>
      </div>

      <h2 className="text-xl font-extrabold tracking-tight text-foreground">
        Jarvis AIOS Cognitive Workspace
      </h2>
      
      <p className="text-xs sm:text-sm text-muted-foreground mt-2 max-w-md leading-relaxed">
        Your virtualization layer is fully online. Memory registers are synchronized. Ask a question or choose an execution path below.
      </p>

      {/* Suggested prompts grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full mt-8">
        {suggestions.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => onSelectPrompt(prompt)}
            className="p-3 text-left bg-secondary/25 hover:bg-secondary/60 border border-border/60 hover:border-primary/30 rounded-xl transition-all duration-300 group outline-none focus-visible:ring-1 focus-visible:ring-primary cursor-pointer flex gap-2.5 items-start"
          >
            <Compass className="h-4 w-4 text-primary/70 group-hover:scale-110 transition-transform mt-0.5 shrink-0" />
            <span className="text-xs font-semibold text-muted-foreground group-hover:text-foreground transition-colors leading-relaxed line-clamp-2">
              {prompt}
            </span>
          </button>
        ))}
      </div>

      {/* Quick actions */}
      <button
        onClick={onNewChat}
        className="mt-8 px-4 py-2 border border-primary/35 bg-primary/10 hover:bg-primary text-foreground hover:text-primary-foreground font-semibold text-xs rounded-xl cursor-pointer transition-all flex items-center gap-2 shadow-md shadow-primary/5 focus-visible:ring-1 focus-visible:ring-primary outline-none"
      >
        <MessageSquarePlus className="h-4 w-4" />
        Initialize Conversation
      </button>
    </div>
  )
}
