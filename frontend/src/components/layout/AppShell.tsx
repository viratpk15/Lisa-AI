import { useState, useEffect } from "react"
import { Link, useLocation, Outlet } from "react-router"
import { useAuthStore } from "@/services/store/authStore"
import { motion, AnimatePresence } from "framer-motion"
import {
  LayoutDashboard,
  FolderOpen,
  Bot,
  Brain,
  ToyBrick,
  Settings,
  ChevronLeft,
  ChevronRight,
  User,
  LogOut,
  Bell,
  Cpu,
  Wifi,
  Database,
  Search,
  PanelRightOpen,
  FileText,
  Sparkles,
  RefreshCw,
  Compass,
  Command,
  Menu,
  X
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from "@/components/ui/dropdown-menu"
import { cn } from "@/lib/utils"
import { CommandPalette } from "@/components/common/CommandPalette"
import { InspectorPanel } from "@/components/layout/InspectorPanel"
import { springTransition } from "@/lib/motion"

interface NavItem {
  name: string
  path: string
  icon: typeof LayoutDashboard
}

interface NavGroup {
  groupName: string
  items: NavItem[]
}

const navigationConfig: NavGroup[] = [
  {
    groupName: "Overview",
    items: [
      { name: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
      { name: "Workspace", path: "/workspace", icon: FolderOpen }
    ]
  },
  {
    groupName: "Intelligence",
    items: [
      { name: "AI Agents", path: "/agents", icon: Bot },
      { name: "Memory", path: "/memory", icon: Brain }
    ]
  },
  {
    groupName: "OS Resources",
    items: [
      { name: "Files & Knowledge", path: "/files", icon: FileText },
      { name: "Tool Registry", path: "/tools", icon: ToyBrick },
      { name: "Model Registry", path: "/models", icon: Sparkles }
    ]
  },
  {
    groupName: "Configuration",
    items: [
      { name: "Settings", path: "/settings", icon: Settings }
    ]
  }
]

interface WorkspaceInfo {
  id: string
  name: string
  desc: string
  color: string
  shortcut: string
}

const workspacesList: WorkspaceInfo[] = [
  { id: "ws-1", name: "Jarvis", desc: "Main AIOS kernel & memory", color: "bg-primary", shortcut: "⌥ 1" },
  { id: "ws-2", name: "NeuroNet", desc: "Neural routing indexer", color: "bg-blue-500", shortcut: "⌥ 2" },
  { id: "ws-3", name: "Frontend", desc: "React UI client application", color: "bg-emerald-500", shortcut: "⌥ 3" },
  { id: "ws-4", name: "Backend", desc: "FastAPI endpoints & tools", color: "bg-amber-500", shortcut: "⌥ 4" },
  { id: "ws-5", name: "Research", desc: "LLM semantic evaluation logs", color: "bg-violet-500", shortcut: "⌥ 5" }
]

export default function AppShell() {
  const user = useAuthStore((state) => state.user)
  const clearAuth = useAuthStore((state) => state.clearAuth)
  const fallbackChar = user?.email ? user.email[0].toUpperCase() : "U"
  const displayName = user?.email ? user.email.split("@")[0] : "User"
  const userEmail = user?.email || "user@jarvis.ai"

  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    const saved = localStorage.getItem("sidebar_collapsed")
    return saved === "true"
  })
  const [inspectorOpen, setInspectorOpen] = useState(() => {
    const saved = localStorage.getItem("inspector_open")
    return saved === "true"
  })
  const [paletteOpen, setPaletteOpen] = useState(false)
  const [activeWorkspace, setActiveWorkspace] = useState<WorkspaceInfo>(workspacesList[0])
  const [currentTime, setCurrentTime] = useState(new Date())
  const [windowWidth, setWindowWidth] = useState(typeof window !== "undefined" ? window.innerWidth : 1200)

  const location = useLocation()

  // Track dynamic time for OS status bar and resize handler for responsive viewports
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    
    const handleResize = () => {
      const width = window.innerWidth
      setWindowWidth(width)
      // Automatically collapse sidebars if screens resize below breakpoints
      if (width < 1024) {
        setSidebarCollapsed(true)
      }
      if (width < 1280) {
        setInspectorOpen(false)
      }
    }

    window.addEventListener("resize", handleResize)
    handleResize() // Run on mount

    return () => {
      clearInterval(timer)
      window.removeEventListener("resize", handleResize)
    }
  }, [])

  // Listen for custom palette open trigger event
  useEffect(() => {
    const handleOpenPalette = () => setPaletteOpen(true)
    window.addEventListener("open-command-palette", handleOpenPalette)
    return () => window.removeEventListener("open-command-palette", handleOpenPalette)
  }, [])


  // Sync state toggles to LocalStorage
  useEffect(() => {
    localStorage.setItem("sidebar_collapsed", sidebarCollapsed.toString())
  }, [sidebarCollapsed])

  useEffect(() => {
    localStorage.setItem("inspector_open", inspectorOpen.toString())
  }, [inspectorOpen])

  // Listen to keyboard shortcut event bindings
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault()
        setPaletteOpen((prev) => !prev)
      }
      if ((e.metaKey || e.ctrlKey) && e.key === "b") {
        e.preventDefault()
        setSidebarCollapsed((prev) => !prev)
      }
      if ((e.metaKey || e.ctrlKey) && e.key === "i") {
        e.preventDefault()
        setInspectorOpen((prev) => !prev)
      }
      if (e.altKey && ["1", "2", "3", "4", "5"].includes(e.key)) {
        const index = parseInt(e.key) - 1
        if (workspacesList[index]) {
          e.preventDefault()
          setActiveWorkspace(workspacesList[index])
        }
      }
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [])

  const allNavItems = navigationConfig.flatMap((group) => group.items)
  const activeItem = allNavItems.find((item) => item.path === location.pathname) || allNavItems[0]

  const toggleSidebar = () => setSidebarCollapsed(!sidebarCollapsed)
  const toggleInspector = () => setInspectorOpen(!inspectorOpen)

  const formattedTime = currentTime.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false
  })

  // Mobile layout state variables
  const isMobile = windowWidth < 768
  const isSidebarDrawerOpen = !sidebarCollapsed && isMobile

  // Construct responsive variants locally using window size constants
  const responsiveSidebarVariants = {
    expanded: { 
      width: 260, 
      x: 0,
      opacity: 1, 
      display: "flex",
      transition: springTransition 
    },
    collapsed: { 
      width: isMobile ? 0 : 68, 
      x: isMobile ? -260 : 0,
      opacity: isMobile ? 0 : 1,
      transitionEnd: { display: isMobile ? "none" : "flex" },
      transition: springTransition 
    }
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background text-foreground font-sans antialiased select-none relative">
      
      {/* Click-away backdrop background overlay for mobile sidebar drawer */}
      <AnimatePresence>
        {isSidebarDrawerOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.4 }}
            exit={{ opacity: 0 }}
            onClick={() => setSidebarCollapsed(true)}
            className="fixed inset-0 z-40 bg-black/60 backdrop-blur-xs cursor-pointer md:hidden"
          />
        )}
      </AnimatePresence>

      {/* 1. Left Sidebar */}
      <motion.aside
        animate={sidebarCollapsed ? "collapsed" : "expanded"}
        variants={responsiveSidebarVariants}
        className={cn(
          "flex flex-col h-full border-r border-border/80 bg-sidebar select-none z-50 shrink-0",
          isMobile ? "absolute top-0 left-0 shadow-2xl h-full" : "relative"
        )}
      >
        {/* Toggle Collapse Trigger (Hidden on Mobile) */}
        {!isMobile && (
          <Button
            onClick={toggleSidebar}
            variant="outline"
            size="icon"
            className="absolute -right-3.5 top-6 h-7 w-7 rounded-full bg-sidebar border border-border/80 hover:bg-secondary cursor-pointer z-50 flex items-center justify-center text-muted-foreground shadow-sm"
          >
            {sidebarCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </Button>
        )}

        {/* Logo Zone */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-border/80 shrink-0">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center h-9 w-9 rounded-lg bg-primary text-primary-foreground font-bold text-lg shadow-lg shadow-primary/20 shrink-0">
              J
            </div>
            {(!sidebarCollapsed || isMobile) && (
              <span className="font-bold text-sm tracking-tight bg-linear-to-r from-foreground via-foreground/90 to-primary bg-clip-text text-transparent">
                Jarvis AIOS
              </span>
            )}
          </div>

          {/* Close Sidebar Drawer button (Visible only on Mobile) */}
          {isMobile && (
            <Button
              onClick={() => setSidebarCollapsed(true)}
              variant="ghost"
              size="icon"
              className="h-8 w-8 hover:bg-secondary text-muted-foreground hover:text-foreground shrink-0 cursor-pointer"
            >
              <X className="h-4.5 w-4.5" />
            </Button>
          )}
        </div>

        {/* Workspace Switcher */}
        <div className="p-3 border-b border-border/80 shrink-0">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className={cn(
                "w-full flex items-center gap-3 p-2 rounded-lg bg-secondary/30 border border-border/40 hover:bg-secondary/60 cursor-pointer transition-all outline-none text-left",
                sidebarCollapsed && !isMobile ? "justify-center" : ""
              )}>
                <div className={cn("h-4 w-4 rounded-full shrink-0 flex items-center justify-center border border-white/10 font-bold text-[8px] text-white", activeWorkspace.color)}>
                  {activeWorkspace.name[0]}
                </div>
                {(!sidebarCollapsed || isMobile) && (
                  <div className="flex-1 min-w-0 flex items-center justify-between">
                    <div>
                      <p className="text-xs font-semibold truncate text-foreground leading-none">{activeWorkspace.name}</p>
                      <p className="text-[9px] text-muted-foreground truncate mt-0.5 font-mono">{activeWorkspace.shortcut}</p>
                    </div>
                    <ChevronRight className="h-3 w-3 text-muted-foreground/60" />
                  </div>
                )}
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="w-64 border-border/80 bg-popover/90 backdrop-blur-md">
              <DropdownMenuLabel className="font-mono text-xs uppercase tracking-wider text-muted-foreground">Select Active Workspace</DropdownMenuLabel>
              <DropdownMenuSeparator className="bg-border/60" />
              {workspacesList.map((ws) => (
                <DropdownMenuItem
                  key={ws.id}
                  onClick={() => setActiveWorkspace(ws)}
                  className="cursor-pointer flex items-center justify-between py-2 text-xs"
                >
                  <div className="flex items-center gap-3">
                    <span className={cn("h-2.5 w-2.5 rounded-full shrink-0", ws.color)} />
                    <div>
                      <p className="font-semibold text-foreground leading-none">{ws.name}</p>
                      <p className="text-[10px] text-muted-foreground mt-0.5">{ws.desc}</p>
                    </div>
                  </div>
                  <span className="font-mono text-[9px] text-muted-foreground/80 bg-secondary px-1 py-0.5 rounded">{ws.shortcut}</span>
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Configuration Driven Nav Items */}
        <div className="flex-1 overflow-y-auto px-3 py-4">
          <nav className="space-y-6">
            {navigationConfig.map((group) => (
              <div key={group.groupName} className="space-y-1.5">
                {(!sidebarCollapsed || isMobile) && (
                  <h3 className="px-3 text-[10px] font-mono font-semibold tracking-wider text-muted-foreground uppercase">
                    {group.groupName}
                  </h3>
                )}
                <div className="space-y-0.5">
                  {group.items.map((item) => {
                    const Icon = item.icon
                    const isActive = location.pathname === item.path || (item.path === "/dashboard" && location.pathname === "/")

                    return (
                      <Link
                        key={item.path}
                        to={item.path}
                        onClick={() => isMobile && setSidebarCollapsed(true)}
                        className={cn(
                          "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 group relative cursor-pointer outline-none focus-visible:ring-1 focus-visible:ring-primary select-none",
                          isActive
                            ? "text-primary-foreground font-semibold"
                            : "text-muted-foreground hover:bg-secondary/60 hover:text-foreground"
                        )}
                      >
                        {isActive && (
                          <motion.div
                            layoutId="sidebarActiveItem"
                            className="absolute inset-0 bg-primary rounded-lg shadow-md shadow-primary/20"
                            transition={springTransition}
                          />
                        )}
                        <Icon className={cn("h-4 w-4 shrink-0 z-10", isActive ? "" : "group-hover:text-primary transition-colors")} />
                        {(!sidebarCollapsed || isMobile) && (
                          <span className="z-10">{item.name}</span>
                        )}
                        {sidebarCollapsed && !isMobile && (
                          <div className="absolute left-16 px-2 py-1 bg-popover text-popover-foreground text-xs rounded border border-border opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-50 shadow-md">
                            {item.name}
                          </div>
                        )}
                      </Link>
                    )
                  })}
                </div>
              </div>
            ))}
          </nav>
        </div>

        {/* User profile / Session footer */}
        <div className="p-3 border-t border-border/80 shrink-0">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <div className={cn(
                "flex items-center gap-3 p-2 rounded-lg hover:bg-secondary/60 cursor-pointer transition-all",
                sidebarCollapsed && !isMobile ? "justify-center" : ""
              )}>
                <Avatar className="h-8 w-8 border border-primary/20 shrink-0">
                  <AvatarFallback className="bg-primary/10 text-primary font-semibold text-xs">{fallbackChar}</AvatarFallback>
                </Avatar>
                {(!sidebarCollapsed || isMobile) && (
                  <div className="flex-1 text-left min-w-0">
                    <p className="text-xs font-semibold truncate text-foreground leading-none capitalize">{displayName}</p>
                    <p className="text-[10px] text-muted-foreground truncate mt-1">{userEmail}</p>
                  </div>
                )}
              </div>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-52 border-border/80 bg-popover/90 backdrop-blur-md">
              <DropdownMenuLabel className="font-mono text-xs uppercase tracking-wider text-muted-foreground">User Session</DropdownMenuLabel>
              <DropdownMenuSeparator className="bg-border/60" />
              <DropdownMenuItem className="cursor-pointer gap-2 text-xs">
                <User className="h-3.5 w-3.5" />
                Profile Details
              </DropdownMenuItem>
              <DropdownMenuItem className="cursor-pointer gap-2 text-xs">
                <Settings className="h-3.5 w-3.5" />
                Preference Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-border/60" />
              <DropdownMenuItem
                onClick={() => clearAuth()}
                className="cursor-pointer gap-2 text-xs text-destructive hover:bg-destructive/10"
              >
                <LogOut className="h-3.5 w-3.5" />
                Disconnect Session
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </motion.aside>

      {/* 2. Main Workspace Layout */}
      <div className="flex-1 flex flex-col h-full bg-background relative overflow-hidden">
        
        {/* Top Command Bar */}
        <header className="h-16 flex items-center justify-between px-4 border-b border-border/80 bg-background/50 backdrop-blur-md z-30 select-none shrink-0 gap-4">
          
          {/* Hamburger Sidebar Trigger Menu button (Visible only on mobile when sidebar is collapsed) */}
          {isMobile && (
            <Button
              onClick={() => setSidebarCollapsed(false)}
              variant="ghost"
              size="icon"
              className="h-8.5 w-8.5 hover:bg-secondary text-muted-foreground hover:text-foreground shrink-0 cursor-pointer"
            >
              <Menu className="h-4.5 w-4.5" />
            </Button>
          )}

          {/* Breadcrumbs (Hidden on Mobile) */}
          <div className="hidden sm:flex items-center gap-2 text-sm text-muted-foreground shrink-0">
            <span className="font-medium hover:text-foreground transition-colors flex items-center gap-1"><Compass className="h-3.5 w-3.5 text-primary" /> {activeWorkspace.name}</span>
            <span>/</span>
            <span className="font-semibold text-foreground">{activeItem.name}</span>
          </div>

          {/* Search Box palette launcher */}
          <button
            onClick={() => setPaletteOpen(true)}
            className="flex-1 max-w-md flex items-center justify-between px-3 py-2 rounded-lg bg-secondary/40 border border-border/60 text-muted-foreground/60 hover:text-foreground hover:border-primary/40 cursor-pointer transition-all text-xs outline-none min-w-0"
          >
            <div className="flex items-center gap-2 min-w-0">
              <Search className="h-3.5 w-3.5 shrink-0" />
              <span className="truncate hidden md:inline">Search workspace, code, or execute command prompt...</span>
              <span className="truncate inline md:hidden">Search...</span>
            </div>
            <div className="hidden sm:flex items-center gap-0.5 px-1.5 py-0.5 rounded border border-border/60 bg-secondary/80 text-[9px] font-mono font-medium shrink-0">
              <Command className="h-2.5 w-2.5 shrink-0" />
              <span>K</span>
            </div>
          </button>

          {/* Panel toggles & Notifications */}
          <div className="flex items-center gap-2 sm:gap-3 shrink-0">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 hover:bg-secondary cursor-pointer text-muted-foreground hover:text-foreground"
            >
              <Bell className="h-4.5 w-4.5" />
            </Button>
            <Separator orientation="vertical" className="h-4 bg-border hidden sm:block" />
            
            {/* Inspector Toggle button (Hidden on Mobile) */}
            <Button
              onClick={toggleInspector}
              variant={inspectorOpen ? "secondary" : "ghost"}
              size="icon"
              className="h-8 w-8 hover:bg-secondary cursor-pointer text-muted-foreground hover:text-foreground hidden md:flex"
            >
              <PanelRightOpen className="h-4.5 w-4.5" />
            </Button>
            
            <div className="flex items-center gap-1.5 px-2.5 py-1 bg-secondary/40 border border-border/60 rounded-full text-[10px] font-mono font-medium text-emerald-500 shrink-0">
              <Wifi className="h-3 w-3" />
              <span className="hidden sm:inline">CONNECTED</span>
            </div>
          </div>
        </header>

        {/* 3-Panel Workspace Container Grid */}
        <div className="flex-1 flex overflow-hidden w-full relative">
          
          {/* Main scroll viewport */}
          <div className={cn(
            "flex-1 h-full",
            location.pathname === "/workspace" ? "overflow-hidden" : "overflow-y-auto px-4 sm:px-6 py-6"
          )}>
            <main className={cn(
              "w-full h-full",
              location.pathname === "/workspace" ? "max-w-none" : "max-w-6xl mx-auto pb-8"
            )}>
              <AnimatePresence>
                <motion.div
                  key={location.pathname}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1, transition: { duration: 0.1 } }}
                  exit={{ opacity: 0, transition: { duration: 0.05 } }}
                  className={cn(location.pathname === "/workspace" ? "h-full w-full" : "")}
                >
                  <Outlet />
                </motion.div>
              </AnimatePresence>
            </main>
          </div>

          {/* 3. Right Inspector panel */}
          <InspectorPanel isOpen={inspectorOpen} onToggle={toggleInspector} />
        </div>

        {/* 4. Operating System status bar */}
        <footer className="h-9 border-t border-border/80 bg-sidebar/85 backdrop-blur px-4 sm:px-6 flex items-center justify-between text-[11px] font-mono text-muted-foreground select-none shrink-0 z-40">
          <div className="flex items-center gap-3 sm:gap-5 overflow-hidden">
            <div className="flex items-center gap-1.5 shrink-0">
              <Cpu className="h-3 w-3 text-primary/80" />
              <span>OS: <span className="text-emerald-500 font-semibold">Online</span></span>
            </div>
            <div className="hidden sm:flex items-center gap-1.5 shrink-0">
              <Sparkles className="h-3 w-3 text-primary/80" />
              <span>Model: <span className="text-foreground">Gemini 2.5</span></span>
            </div>
            <div className="hidden md:flex items-center gap-1.5 shrink-0">
              <FolderOpen className="h-3 w-3 text-primary/80" />
              <span>Scope: <span className="text-foreground">{activeWorkspace.name}</span></span>
            </div>
            <div className="flex items-center gap-1.5 shrink-0">
              <RefreshCw className="h-3 w-3 text-primary/80" />
              <span>Sync</span>
            </div>
          </div>
          
          <div className="flex items-center gap-3 sm:gap-5 shrink-0">
            <div className="hidden sm:flex items-center gap-1.5">
              <Database className="h-3 w-3 text-primary/80" />
              <span>1.2GB</span>
            </div>
            <div className="hidden sm:flex items-center gap-1.5">
              <Command className="h-3 w-3 text-primary/80" />
              <span>Tokens: 1.4k</span>
            </div>
            <div className="border-l border-border/60 pl-3 sm:pl-4 py-0.5 text-foreground font-semibold">
              {formattedTime}
            </div>
          </div>
        </footer>
      </div>

      {/* Command Palette dialog triggers */}
      <CommandPalette isOpen={paletteOpen} onClose={() => setPaletteOpen(false)} />
    </div>
  )
}
