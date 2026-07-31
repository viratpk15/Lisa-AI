import { useEffect, useState, useRef } from "react"
import { useNavigate } from "react-router"
import { motion } from "framer-motion"
import {
  Search,
  LayoutDashboard,
  FolderOpen,
  Bot,
  Brain,
  ToyBrick,
  Settings,
  RefreshCw,
  Play,
  Terminal,
  Columns,
  Sparkles,
  SearchCode
} from "lucide-react"
import { Dialog, DialogContent } from "@/components/ui/dialog"
import { dialogVariants, commandPaletteItemVariants } from "@/lib/motion"
import { cn } from "@/lib/utils"

interface CommandPaletteProps {
  isOpen: boolean
  onClose: () => void
}

interface CommandItem {
  id: string
  name: string
  category: string
  shortcut?: string
  icon: typeof Search
  action: () => void
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({ isOpen, onClose }) => {
  const [search, setSearch] = useState("")
  const [activeIndex, setActiveIndex] = useState(0)
  const navigate = useNavigate()
  const listRef = useRef<HTMLDivElement>(null)

  const commands: CommandItem[] = [
    // Navigation
    { id: "nav-dash", name: "Go to Dashboard", category: "Navigation", shortcut: "G D", icon: LayoutDashboard, action: () => { navigate("/dashboard"); onClose(); } },
    { id: "nav-work", name: "Go to Workspaces", category: "Navigation", shortcut: "G W", icon: FolderOpen, action: () => { navigate("/workspace"); onClose(); } },
    { id: "nav-agent", name: "Go to AI Agents", category: "Navigation", shortcut: "G A", icon: Bot, action: () => { navigate("/agents"); onClose(); } },
    { id: "nav-mem", name: "Go to Memory Manager", category: "Navigation", shortcut: "G M", icon: Brain, action: () => { navigate("/memory"); onClose(); } },
    { id: "nav-tool", name: "Go to Tool Registry", category: "Navigation", shortcut: "G T", icon: ToyBrick, action: () => { navigate("/tools"); onClose(); } },
    { id: "nav-set", name: "Go to Settings", category: "Navigation", shortcut: "G S", icon: Settings, action: () => { navigate("/settings"); onClose(); } },
    
    // System Actions
    { id: "sys-sync", name: "Sync Vector Database", category: "System", shortcut: "⌘ S", icon: RefreshCw, action: () => { console.log("Sync vectors"); onClose(); } },
    { id: "sys-start", name: "Start Code Orchestrator", category: "System", shortcut: "⌥ P", icon: Play, action: () => { console.log("Start agent"); onClose(); } },
    { id: "sys-kernel", name: "Restart AIOS Kernel", category: "System", shortcut: "⇧ K", icon: Terminal, action: () => { console.log("Restart OS"); onClose(); } },
    
    // Commands/Controls
    { id: "cmd-sidebar", name: "Toggle Left Sidebar", category: "Controls", shortcut: "⌘ B", icon: Columns, action: () => { console.log("Toggle sidebar"); onClose(); } },
    { id: "cmd-search", name: "Find in Files", category: "Controls", shortcut: "⌘ F", icon: SearchCode, action: () => { console.log("Find files"); onClose(); } },
    { id: "cmd-prompt", name: "Configure System Prompt", category: "Controls", shortcut: "⌥ P", icon: Sparkles, action: () => { navigate("/settings"); onClose(); } }
  ]

  // Filter commands
  const filtered = commands.filter((cmd) =>
    cmd.name.toLowerCase().includes(search.toLowerCase()) ||
    cmd.category.toLowerCase().includes(search.toLowerCase())
  )

  // Reset active item when filter changes
  useEffect(() => {
    setActiveIndex(0)
  }, [search])

  // Key navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return

      if (e.key === "ArrowDown") {
        e.preventDefault()
        setActiveIndex((prev) => (prev + 1) % filtered.length)
      } else if (e.key === "ArrowUp") {
        e.preventDefault()
        setActiveIndex((prev) => (prev - 1 + filtered.length) % filtered.length)
      } else if (e.key === "Enter") {
        e.preventDefault()
        if (filtered[activeIndex]) {
          filtered[activeIndex].action()
        }
      }
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [isOpen, activeIndex, filtered])

  // Scroll active item into view
  useEffect(() => {
    if (listRef.current) {
      const activeEl = listRef.current.children[activeIndex] as HTMLElement
      if (activeEl) {
        activeEl.scrollIntoView({ block: "nearest" })
      }
    }
  }, [activeIndex])

  // Group commands by category
  const groups: { [key: string]: CommandItem[] } = {}
  filtered.forEach((cmd) => {
    if (!groups[cmd.category]) groups[cmd.category] = []
    groups[cmd.category].push(cmd)
  })

  // Flatten active indexes across groups
  let absoluteIndex = 0
  const renderedGroups = Object.entries(groups).map(([category, items]) => {
    const section = (
      <div key={category} className="space-y-1">
        <div className="px-3 py-1.5 text-[10px] font-mono font-semibold tracking-wider text-muted-foreground uppercase">
          {category}
        </div>
        {items.map((item) => {
          const currentAbsIndex = absoluteIndex
          absoluteIndex++
          const isSelected = activeIndex === currentAbsIndex
          const Icon = item.icon

          return (
            <motion.button
              key={item.id}
              onClick={item.action}
              onMouseEnter={() => setActiveIndex(currentAbsIndex)}
              variants={commandPaletteItemVariants}
              whileTap="tap"
              className={cn(
                "w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm transition-all text-left outline-none cursor-pointer",
                isSelected
                  ? "bg-primary text-primary-foreground font-medium"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              <div className="flex items-center gap-3">
                <Icon className={cn("h-4 w-4 shrink-0", isSelected ? "text-primary-foreground" : "text-primary/75")} />
                <span>{item.name}</span>
              </div>
              {item.shortcut && (
                <div className={cn(
                  "px-2 py-0.5 rounded text-[10px] font-mono font-medium border tracking-wide",
                  isSelected
                    ? "bg-primary-foreground/20 border-primary-foreground/20 text-primary-foreground"
                    : "bg-secondary border-border text-muted-foreground"
                )}>
                  {item.shortcut}
                </div>
              )}
            </motion.button>
          )
        })}
      </div>
    )
    return section
  })

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent 
        showCloseButton={false}
        className="max-w-2xl bg-card/90 border border-border/80 backdrop-blur-lg p-0 shadow-2xl overflow-hidden rounded-xl"
      >
        <motion.div
          initial="initial"
          animate="animate"
          exit="exit"
          variants={dialogVariants}
          className="flex flex-col h-[400px] w-full"
        >
          {/* Search box */}
          <div className="flex items-center gap-3 px-4 border-b border-border/80 h-14 shrink-0">
            <Search className="h-4.5 w-4.5 text-muted-foreground/80 shrink-0" />
            <input
              type="text"
              placeholder="Search workspaces, agents, or trigger OS actions..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="flex-1 bg-transparent border-0 outline-none text-sm text-foreground placeholder:text-muted-foreground/60 w-full"
              autoFocus
            />
            <div className="px-2 py-0.5 rounded text-[9px] font-mono border border-border/50 bg-secondary/50 text-muted-foreground/80">
              ESC
            </div>
          </div>

          {/* List Area */}
          <div className="flex-1 overflow-y-auto p-3 space-y-4">
            {filtered.length > 0 ? (
              <div ref={listRef} className="space-y-4">
                {renderedGroups}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground gap-2 p-6">
                <Search className="h-8 w-8 text-muted-foreground/45" />
                <div>
                  <p className="text-sm font-semibold">No commands found</p>
                  <p className="text-xs text-muted-foreground/60 mt-1">Try querying general navigation terms or workspace configurations.</p>
                </div>
              </div>
            )}
          </div>

          {/* Footer Navigation Hints */}
          <div className="h-10 bg-secondary/40 border-t border-border/80 px-4 flex items-center justify-between text-[10px] font-mono text-muted-foreground shrink-0 select-none">
            <div className="flex items-center gap-3">
              <span className="flex items-center gap-1"><span className="border border-border/60 bg-secondary px-1 py-0.5 rounded">↑↓</span> Navigate</span>
              <span className="flex items-center gap-1"><span className="border border-border/60 bg-secondary px-1.5 py-0.5 rounded">↵</span> Select</span>
            </div>
            <span>Jarvis AIOS Command Prompt</span>
          </div>
        </motion.div>
      </DialogContent>
    </Dialog>
  )
}
