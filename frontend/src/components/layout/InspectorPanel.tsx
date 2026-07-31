import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import {
  Sparkles,
  Terminal,
  Activity,
  Compass,
  Database,
  SearchCode,
  Layers,
  PanelRightClose,
  FileText,
  Bookmark
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { panelVariants } from "@/lib/motion"

interface InspectorPanelProps {
  isOpen: boolean
  onToggle: () => void
}

type TabType = "thoughts" | "tools" | "debugger" | "context" | "memory" | "files" | "references"

export const InspectorPanel: React.FC<InspectorPanelProps> = ({ isOpen, onToggle }) => {
  const [activeTab, setActiveTab] = useState<TabType>("thoughts")
  const [windowWidth, setWindowWidth] = useState(typeof window !== "undefined" ? window.innerWidth : 1200)

  // Track window resizing for responsive overlay rendering
  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth)
    window.addEventListener("resize", handleResize)
    return () => window.removeEventListener("resize", handleResize)
  }, [])

  const tabs = [
    { id: "context", name: "Context", icon: Compass },
    { id: "memory", name: "Memory", icon: Database },
    { id: "files", name: "Files", icon: FileText },
    { id: "references", name: "References", icon: Bookmark },
    { id: "thoughts", name: "AI Thoughts", icon: Sparkles },
    { id: "tools", name: "Tool Output", icon: SearchCode },
    { id: "debugger", name: "Debugger", icon: Activity }
  ]

  const renderTabContent = () => {
    switch (activeTab) {
      case "context":
        return (
          <div className="space-y-4">
            <div className="p-3 bg-secondary/30 rounded-lg border border-border/50">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground font-mono mb-2">Active Session</h4>
              <div className="space-y-1.5 text-xs font-mono">
                <div className="flex justify-between"><span className="text-muted-foreground">Session ID:</span> <span className="text-foreground">ses_92f8a1</span></div>
                <div className="flex justify-between"><span className="text-muted-foreground">Model Bind:</span> <span className="text-primary font-medium">Gemini 2.5 Flash</span></div>
                <div className="flex justify-between"><span className="text-muted-foreground">Workspace:</span> <span className="text-foreground">Personal Cloud AI</span></div>
              </div>
            </div>
            <div className="p-3 bg-secondary/30 rounded-lg border border-border/50">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground font-mono mb-2">Contextual Weights</h4>
              <div className="space-y-1.5 text-xs">
                <div className="flex justify-between text-muted-foreground"><span>System prompt:</span> <span>1.2k tokens</span></div>
                <div className="flex justify-between text-muted-foreground"><span>Conversation history:</span> <span>3.4k tokens</span></div>
                <div className="flex justify-between text-muted-foreground"><span>Tool declarations:</span> <span>844 tokens</span></div>
              </div>
            </div>
          </div>
        )
      case "memory":
        return (
          <div className="space-y-3 font-mono text-xs">
            <div className="p-3 bg-secondary/30 rounded-lg border border-border/50">
              <div className="flex items-center gap-2 text-primary mb-2">
                <Layers className="h-4 w-4" />
                <span className="font-semibold text-xs uppercase tracking-wider">Semantic Store</span>
              </div>
              <div className="space-y-1">
                <div className="flex justify-between"><span className="text-muted-foreground">Vector Dimension:</span> <span className="text-foreground">1536 (Normalized)</span></div>
                <div className="flex justify-between"><span className="text-muted-foreground">Active Cache:</span> <span className="text-foreground">1,824 Vectors</span></div>
                <div className="flex justify-between"><span className="text-muted-foreground">Dirty Nodes:</span> <span className="text-amber-500">0 pending sync</span></div>
              </div>
            </div>
            <div className="space-y-1.5">
              <span className="text-[10px] text-muted-foreground uppercase font-semibold">Recent Memories Cached</span>
              <div className="space-y-1 p-2 bg-secondary/20 rounded border border-border/30 text-[10px]">
                <div className="text-primary truncate">key: usr_settings_language</div>
                <div className="text-muted-foreground text-[9px]">"value": "TypeScript/React 19"</div>
              </div>
              <div className="space-y-1 p-2 bg-secondary/20 rounded border border-border/30 text-[10px]">
                <div className="text-primary truncate">key: last_workspace_sync</div>
                <div className="text-muted-foreground text-[9px]">"value": "1784902573827"</div>
              </div>
            </div>
          </div>
        )
      case "thoughts":
        return (
          <div className="space-y-3 font-mono text-xs">
            <div className="flex items-center justify-between text-primary font-semibold text-[10px] uppercase border-b border-border/40 pb-1.5">
              <span>Reasoning Step</span>
              <span>Inference Cost</span>
            </div>
            <div className="space-y-3">
              <div className="flex gap-2">
                <span className="text-primary">[1]</span>
                <div>
                  <div className="font-semibold text-foreground">Query analysis</div>
                  <div className="text-[10px] text-muted-foreground mt-0.5">Identified navigation intent to dashboard panel.</div>
                </div>
              </div>
              <div className="flex gap-2">
                <span className="text-primary">[2]</span>
                <div>
                  <div className="font-semibold text-foreground">File structure lookup</div>
                  <div className="text-[10px] text-muted-foreground mt-0.5">Scanned filesystem routes matching search keys.</div>
                </div>
              </div>
              <div className="flex gap-2">
                <span className="text-primary">[3]</span>
                <div>
                  <div className="font-semibold text-foreground">Tool binding</div>
                  <div className="text-[10px] text-muted-foreground mt-0.5">Invoked local directory listing API tool.</div>
                </div>
              </div>
            </div>
          </div>
        )
      case "files":
        return (
          <div className="space-y-3">
            <div className="flex items-center justify-between text-[10px] font-mono text-muted-foreground border-b border-border/40 pb-1.5 uppercase font-semibold">
              <span>Attached File</span>
              <span>Size</span>
            </div>
            <div className="space-y-2 font-mono text-xs">
              <div className="p-2.5 bg-secondary/35 hover:bg-secondary/65 border border-border/50 rounded-lg flex items-center justify-between gap-3 group transition-colors">
                <div className="flex items-center gap-2 min-w-0">
                  <FileText className="h-4 w-4 text-primary shrink-0" />
                  <span className="truncate font-semibold text-foreground">src/App.tsx</span>
                </div>
                <span className="text-[10px] text-muted-foreground shrink-0">2.4 KB</span>
              </div>
              <div className="p-2.5 bg-secondary/35 hover:bg-secondary/65 border border-border/50 rounded-lg flex items-center justify-between gap-3 group transition-colors">
                <div className="flex items-center gap-2 min-w-0">
                  <FileText className="h-4 w-4 text-primary shrink-0" />
                  <span className="truncate font-semibold text-foreground">src/main.tsx</span>
                </div>
                <span className="text-[10px] text-muted-foreground shrink-0">1.1 KB</span>
              </div>
              <div className="p-2.5 bg-secondary/35 hover:bg-secondary/65 border border-border/50 rounded-lg flex items-center justify-between gap-3 group transition-colors">
                <div className="flex items-center gap-2 min-w-0">
                  <FileText className="h-4 w-4 text-primary shrink-0" />
                  <span className="truncate font-semibold text-foreground">AppShell.tsx</span>
                </div>
                <span className="text-[10px] text-muted-foreground shrink-0">22.8 KB</span>
              </div>
              <div className="p-2.5 bg-secondary/35 hover:bg-secondary/65 border border-border/50 rounded-lg flex items-center justify-between gap-3 group transition-colors">
                <div className="flex items-center gap-2 min-w-0">
                  <FileText className="h-4 w-4 text-primary shrink-0" />
                  <span className="truncate font-semibold text-foreground">package.json</span>
                </div>
                <span className="text-[10px] text-muted-foreground shrink-0">976 B</span>
              </div>
            </div>
          </div>
        )
      case "references":
        return (
          <div className="space-y-3">
            <div className="flex items-center justify-between text-[10px] font-mono text-muted-foreground border-b border-border/40 pb-1.5 uppercase font-semibold">
              <span>Active Reference Context</span>
              <span>Weight</span>
            </div>
            <div className="space-y-2 text-xs">
              <div className="p-2.5 bg-secondary/35 border border-border/50 rounded-lg flex flex-col gap-1 font-mono">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-primary font-semibold truncate text-[11px]">docs/06_MEMORY.md</span>
                  <span className="text-[9px] bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-1 py-0.5 rounded leading-none">CRITICAL</span>
                </div>
                <span className="text-[10px] text-muted-foreground">Local schema for context vectors managers.</span>
              </div>
              <div className="p-2.5 bg-secondary/35 border border-border/50 rounded-lg flex flex-col gap-1 font-mono">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-primary font-semibold truncate text-[11px]">.agents/AGENTS.md</span>
                  <span className="text-[9px] bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-1 py-0.5 rounded leading-none">CRITICAL</span>
                </div>
                <span className="text-[10px] text-muted-foreground">Standard AI Operating System constitution loaded.</span>
              </div>
              <div className="p-2.5 bg-secondary/35 border border-border/50 rounded-lg flex flex-col gap-1 font-mono">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-primary font-semibold truncate text-[11px]">web: react-19-motion</span>
                  <span className="text-[9px] bg-blue-500/20 text-blue-400 border border-blue-500/30 px-1 py-0.5 rounded leading-none">HIGH</span>
                </div>
                <span className="text-[10px] text-muted-foreground">Crawl summary of standard framer-motion transitions.</span>
              </div>
            </div>
          </div>
        )
      case "tools":
        return (
          <div className="space-y-3">
            <div className="p-3 bg-secondary/30 rounded-lg border border-border/50 font-mono text-xs">
              <div className="flex justify-between items-center mb-2 border-b border-border/40 pb-1.5">
                <span className="text-primary font-semibold">read_directory()</span>
                <Badge className="text-[9px] bg-emerald-500/25 border-emerald-500/20 text-emerald-400">SUCCESS</Badge>
              </div>
              <pre className="text-[9px] text-muted-foreground max-h-52 overflow-y-auto">
{`{
  "status": "success",
  "files": [
    "src/App.tsx",
    "src/main.tsx",
    "package.json"
  ]
}`}
              </pre>
            </div>
          </div>
        )
      case "debugger":
        return (
          <div className="space-y-4">
            <div className="p-3 bg-secondary/30 rounded-lg border border-border/50 font-mono text-xs">
              <h4 className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground mb-2">Performance Metrics</h4>
              <div className="space-y-1.5">
                <div className="flex justify-between"><span>Kernel Jitter:</span> <span className="text-emerald-400">&lt; 1ms</span></div>
                <div className="flex justify-between"><span>Socket Latency:</span> <span className="text-emerald-400">12ms</span></div>
                <div className="flex justify-between"><span>Memory Garbage Coll:</span> <span className="text-foreground">0.05MB</span></div>
              </div>
            </div>
            <div className="p-3 bg-secondary/30 rounded-lg border border-border/50 font-mono text-xs">
              <h4 className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground mb-2">Active Heap</h4>
              <div className="h-1.5 w-full bg-secondary rounded-full overflow-hidden mb-1">
                <div className="h-full bg-primary rounded-full" style={{ width: "42%" }} />
              </div>
              <div className="flex justify-between text-[10px] text-muted-foreground">
                <span>Heap Allocated: 3.4MB</span>
                <span>42% Capacity</span>
              </div>
            </div>
          </div>
        )
    }
  }

  // Float absolute when window size is tablet or small laptop
  const isOverlay = windowWidth < 1280

  return (
    <>
      {/* Click-away backdrop overlay for mobile/tablet screens when open */}
      <AnimatePresence>
        {isOverlay && isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.4 }}
            exit={{ opacity: 0 }}
            onClick={onToggle}
            className="fixed inset-0 z-40 bg-black/60 backdrop-blur-xs cursor-pointer"
          />
        )}
      </AnimatePresence>

      <motion.aside
        animate={isOpen ? "open" : "closed"}
        variants={panelVariants}
        className={cn(
          "h-full border-l border-border/80 bg-sidebar flex-col shrink-0 overflow-hidden relative select-none z-50",
          isOverlay ? "absolute top-0 right-0 shadow-2xl h-full" : "relative"
        )}
      >
        {/* Panel Header */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-border/80 shrink-0">
          <div className="flex items-center gap-2">
            <Terminal className="h-4 w-4 text-primary" />
            <span className="font-bold text-sm tracking-tight">System Inspector</span>
          </div>
          <Button
            onClick={onToggle}
            variant="ghost"
            size="icon-sm"
            className="hover:bg-secondary cursor-pointer text-muted-foreground hover:text-foreground"
          >
            <PanelRightClose className="h-4 w-4" />
          </Button>
        </div>

        {/* Resize Handle (Mock visual indicator) */}
        <div className="absolute top-0 left-0 w-px h-full bg-border/40 hover:bg-primary/50 cursor-ew-resize z-50 transition-colors" />

        {/* Tab Switcher Grid */}
        <div className="grid grid-cols-3 gap-1 p-2 bg-secondary/20 border-b border-border/50 shrink-0">
          {tabs.map((tab) => {
            const TabIcon = tab.icon
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as TabType)}
                className={cn(
                  "flex flex-col items-center justify-center p-1.5 rounded-md text-[9px] font-medium transition-all gap-1 cursor-pointer outline-none border relative select-none",
                  isActive
                    ? "text-primary-foreground font-semibold border-primary/50"
                    : "text-muted-foreground bg-transparent border-transparent hover:bg-secondary/40 hover:text-foreground"
                )}
              >
                {isActive && (
                  <motion.div
                    layoutId="inspectorActiveTab"
                    className="absolute inset-0 bg-primary rounded-md shadow-xs"
                    transition={{ type: "spring", stiffness: 400, damping: 32 }}
                  />
                )}
                <TabIcon className="h-3.5 w-3.5 z-10" />
                <span className="z-10">{tab.name}</span>
              </button>
            )
          })}
        </div>

        {/* Content Viewport */}
        <div className="flex-1 overflow-y-auto p-4">
          {renderTabContent()}
        </div>
      </motion.aside>
    </>
  )
}

// Badge replacement inline helper for radices
const Badge: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className }) => (
  <span className={cn("px-1.5 py-0.5 rounded-full text-[9px] font-medium border uppercase tracking-wider font-mono", className)}>
    {children}
  </span>
)
