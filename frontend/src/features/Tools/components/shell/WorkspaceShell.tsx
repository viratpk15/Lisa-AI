import React, { useEffect } from "react"
import {
  Wrench,
  Search,
  Terminal,
  Activity,
  ChevronRight,
  Command,
  PanelLeft,
  X,
  Layers,
} from "lucide-react"
import { useToolConsoleStore } from "../../store/useToolConsoleStore"

interface WorkspaceShellProps {
  title?: string
  subtitle?: string
  children: React.ReactNode
}

export function WorkspaceShell({
  title = "Tool Console",
  subtitle = "Native AI Engine Tool Discovery, Schema Inspection & Execution",
  children,
}: WorkspaceShellProps) {
  const toggleSidebar = useToolConsoleStore((s) => s.toggleSidebar)
  const commandPaletteOpen = useToolConsoleStore((s) => s.commandPaletteOpen)
  const setCommandPaletteOpen = useToolConsoleStore((s) => s.setCommandPaletteOpen)

  // Listen for Cmd+K keyboard shortcut
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault()
        setCommandPaletteOpen(!commandPaletteOpen)
      }
    }
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [commandPaletteOpen, setCommandPaletteOpen])

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] -m-6 bg-[#090D16] text-foreground font-sans overflow-hidden border-t border-border/40">
      {/* 1. Studio Header Bar */}
      <header className="h-12 px-4 bg-[#121826]/80 backdrop-blur-md border-b border-border/40 flex items-center justify-between z-10">
        <div className="flex items-center gap-3">
          <button
            onClick={toggleSidebar}
            className="p-1.5 text-muted-foreground hover:text-foreground hover:bg-secondary/50 rounded-lg cursor-pointer transition-all"
            title="Toggle Sidebar"
          >
            <PanelLeft className="h-4 w-4" />
          </button>

          <div className="flex items-center gap-2">
            <div className="p-1 bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 rounded">
              <Wrench className="h-4 w-4" />
            </div>
            <span className="text-xs font-bold tracking-wide uppercase text-foreground">Jarvis AIOS</span>
            <ChevronRight className="h-3.5 w-3.5 text-muted-foreground" />
            <span className="text-xs font-semibold text-cyan-400">Studio Framework</span>
          </div>
        </div>

        {/* Global Search & Command Palette Trigger */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setCommandPaletteOpen(true)}
            className="flex items-center gap-2 px-3 py-1.5 text-xs bg-secondary/40 border border-border/50 hover:border-cyan-500/40 text-muted-foreground hover:text-foreground rounded-lg cursor-pointer transition-all w-48 sm:w-64 justify-between shadow-xs"
          >
            <span className="flex items-center gap-1.5">
              <Search className="h-3.5 w-3.5 text-muted-foreground" />
              <span>Search Studio Commands...</span>
            </span>
            <kbd className="px-1.5 py-0.5 text-[10px] font-mono bg-secondary/80 border border-border/60 rounded text-muted-foreground">
              ⌘K
            </kbd>
          </button>

          <div className="hidden md:flex items-center gap-2 text-[11px] font-mono text-muted-foreground border-l border-border/40 pl-3">
            <span className="flex items-center gap-1.5 text-emerald-400">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              Engine Online
            </span>
          </div>
        </div>
      </header>

      {/* 2. Breadcrumb & Action Toolbar */}
      <div className="h-10 px-4 bg-secondary/20 border-b border-border/40 flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs">
          <span className="text-muted-foreground">Studios</span>
          <ChevronRight className="h-3.5 w-3.5 text-muted-foreground" />
          <span className="font-bold text-foreground">{title}</span>
          <span className="hidden sm:inline text-[11px] text-muted-foreground font-normal ml-2 border-l border-border/40 pl-2">
            {subtitle}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 text-[10px] font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 rounded font-semibold">
            v1.1.0 Native Engine
          </span>
        </div>
      </div>

      {/* 3. Main Workspace Split Layout */}
      <main className="flex-1 flex overflow-hidden">
        {/* Dynamic Studio Content */}
        <div className="flex-1 overflow-y-auto p-4 scrollbar-thin">{children}</div>
      </main>

      {/* 4. Bottom Status & Health Bar */}
      <footer className="h-7 px-4 bg-[#0D1117] border-t border-border/40 flex items-center justify-between text-[11px] font-mono text-muted-foreground">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1">
            <Activity className="h-3 w-3 text-cyan-400" />
            Backend API: <span className="text-foreground">http://127.0.0.1:8000</span>
          </span>
          <span className="hidden md:inline border-l border-border/40 pl-4">
            Sandbox Root: <span className="text-foreground">./workspace</span>
          </span>
        </div>

        <div className="flex items-center gap-3">
          <span>Latency: <span className="text-emerald-400">12ms</span></span>
          <span className="border-l border-border/40 pl-3">Ready</span>
        </div>
      </footer>

      {/* 5. Command Palette Modal (UI Overlay) */}
      {commandPaletteOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-start justify-center pt-20 z-50 p-4">
          <div className="bg-[#121826] border border-cyan-500/40 rounded-xl w-full max-w-xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center px-4 py-3 border-b border-border/40">
              <Command className="h-4 w-4 text-cyan-400 mr-2" />
              <input
                type="text"
                autoFocus
                placeholder="Type a command or search tools..."
                className="w-full bg-transparent text-sm text-foreground focus:outline-none placeholder:text-muted-foreground"
              />
              <button
                onClick={() => setCommandPaletteOpen(false)}
                className="p-1 text-muted-foreground hover:text-foreground cursor-pointer"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="p-2 space-y-1 text-xs">
              <div className="px-3 py-1.5 text-[10px] font-mono text-muted-foreground uppercase">
                Quick Studio Navigation
              </div>
              <button
                onClick={() => setCommandPaletteOpen(false)}
                className="w-full text-left px-3 py-2 rounded-lg hover:bg-cyan-500/10 text-foreground flex items-center justify-between cursor-pointer"
              >
                <span className="flex items-center gap-2">
                  <Wrench className="h-3.5 w-3.5 text-cyan-400" />
                  Tool Console Explorer
                </span>
                <kbd className="text-[10px] font-mono text-muted-foreground">Jump to /tools</kbd>
              </button>
              <button
                onClick={() => setCommandPaletteOpen(false)}
                className="w-full text-left px-3 py-2 rounded-lg hover:bg-cyan-500/10 text-foreground flex items-center justify-between cursor-pointer"
              >
                <span className="flex items-center gap-2">
                  <Terminal className="h-3.5 w-3.5 text-emerald-400" />
                  Execute Terminal Tool
                </span>
                <kbd className="text-[10px] font-mono text-muted-foreground">Run Command</kbd>
              </button>
              <button
                onClick={() => setCommandPaletteOpen(false)}
                className="w-full text-left px-3 py-2 rounded-lg hover:bg-cyan-500/10 text-foreground flex items-center justify-between cursor-pointer"
              >
                <span className="flex items-center gap-2">
                  <Layers className="h-3.5 w-3.5 text-violet-400" />
                  Filter by Category: System
                </span>
                <kbd className="text-[10px] font-mono text-muted-foreground">Filter</kbd>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
