import { useState, useEffect } from "react"
import { Link, useLocation, useNavigate, Outlet } from "react-router"
import { useAuthStore } from "@/services/store/authStore"
import { motion, AnimatePresence } from "framer-motion"
import {
  Home,
  Bot,
  Mail,
  FolderOpen,
  Settings,
  ChevronLeft,
  ChevronRight,
  User,
  LogOut,
  Search,
  PanelRightOpen,
  Command,
  Menu,
  X,
  Code,
  Briefcase,
  Plane
} from "lucide-react"
import { Button } from "@/components/ui/button"
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
  icon: typeof Home
}

const primaryNavItems: NavItem[] = [
  { name: "Home", path: "/", icon: Home },
  { name: "Assistant", path: "/assistant", icon: Bot },
  { name: "Email", path: "/email", icon: Mail },
  { name: "Files", path: "/files", icon: FolderOpen },
  { name: "Jobs", path: "/jobs", icon: Briefcase },
  { name: "Travel", path: "/travel", icon: Plane },
]

export default function AppShell() {
  const user = useAuthStore((state) => state.user)
  const clearAuth = useAuthStore((state) => state.clearAuth)
  const navigate = useNavigate()
  const fallbackChar = user?.email ? user.email[0].toUpperCase() : "L"
  const displayName = user?.email ? user.email.split("@")[0] : "User"
  const userEmail = user?.email || "user@lisa.ai"

  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    const saved = localStorage.getItem("sidebar_collapsed")
    return saved === "true"
  })
  const [inspectorOpen, setInspectorOpen] = useState(() => {
    const saved = localStorage.getItem("inspector_open")
    return saved === "true"
  })
  const [paletteOpen, setPaletteOpen] = useState(false)
  const [windowWidth, setWindowWidth] = useState(typeof window !== "undefined" ? window.innerWidth : 1200)

  const location = useLocation()

  // Track resize handler for responsive viewports
  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth
      setWindowWidth(width)
      if (width < 1024) {
        setSidebarCollapsed(true)
      }
      if (width < 1280) {
        setInspectorOpen(false)
      }
    }

    window.addEventListener("resize", handleResize)
    handleResize()

    return () => {
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
    let lastKey = ""
    let lastKeyTime = 0

    const handleKeyDown = (e: KeyboardEvent) => {
      const activeEl = document.activeElement
      const isInput = activeEl?.tagName === "INPUT" || activeEl?.tagName === "TEXTAREA" || (activeEl as HTMLElement)?.isContentEditable

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

      // Two-key navigation chords (e.g. G then T for Travel, G then H for Home, etc.)
      if (!isInput && !e.metaKey && !e.ctrlKey && !e.altKey) {
        const now = Date.now()
        if (lastKey === "g" && (now - lastKeyTime) < 1000) {
          if (e.key === "t" || e.key === "T") {
            e.preventDefault()
            navigate("/travel")
          } else if (e.key === "j" || e.key === "J") {
            e.preventDefault()
            navigate("/jobs")
          } else if (e.key === "h" || e.key === "H") {
            e.preventDefault()
            navigate("/")
          } else if (e.key === "a" || e.key === "A") {
            e.preventDefault()
            navigate("/assistant")
          } else if (e.key === "e" || e.key === "E") {
            e.preventDefault()
            navigate("/email")
          } else if (e.key === "f" || e.key === "F") {
            e.preventDefault()
            navigate("/files")
          } else if (e.key === "s" || e.key === "S") {
            e.preventDefault()
            navigate("/settings")
          }
          lastKey = ""
          return
        }

        if (e.key === "g" || e.key === "G") {
          lastKey = "g"
          lastKeyTime = now
        } else {
          lastKey = ""
        }
      }
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [navigate])

  const toggleSidebar = () => setSidebarCollapsed(!sidebarCollapsed)
  const toggleInspector = () => setInspectorOpen(!inspectorOpen)

  // Mobile layout state variables
  const isMobile = windowWidth < 768
  const isSidebarDrawerOpen = !sidebarCollapsed && isMobile

  const isRouteActive = (path: string) => {
    if (path === "/") {
      return location.pathname === "/" || location.pathname === "/dashboard"
    }
    return location.pathname === path || location.pathname.startsWith(`${path}/`)
  }

  // Construct responsive variants locally using window size constants
  const responsiveSidebarVariants = {
    expanded: { 
      width: 250, 
      x: 0,
      opacity: 1, 
      display: "flex",
      transition: springTransition 
    },
    collapsed: { 
      width: isMobile ? 0 : 68, 
      x: isMobile ? -250 : 0,
      opacity: isMobile ? 0 : 1,
      transitionEnd: { display: isMobile ? "none" : "flex" },
      transition: springTransition 
    }
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background text-foreground font-sans antialiased select-none relative">
      
      {/* Click-away backdrop overlay for mobile sidebar drawer */}
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
          "flex flex-col h-full border-r border-border/70 bg-sidebar select-none z-50 shrink-0",
          isMobile ? "absolute top-0 left-0 shadow-2xl h-full" : "relative"
        )}
      >
        {/* Toggle Collapse Trigger (Hidden on Mobile) */}
        {!isMobile && (
          <Button
            onClick={toggleSidebar}
            variant="outline"
            size="icon"
            aria-label={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            className="absolute -right-3.5 top-6 h-7 w-7 rounded-full bg-sidebar border border-border/80 hover:bg-secondary cursor-pointer z-50 flex items-center justify-center text-muted-foreground shadow-sm"
          >
            {sidebarCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </Button>
        )}

        {/* Logo Zone */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-border/70 shrink-0">
          <Link to="/" className="flex items-center gap-3 outline-none">
            <div className="flex items-center justify-center h-9 w-9 rounded-xl bg-primary text-primary-foreground font-bold text-base shadow-sm shrink-0">
              L
            </div>
            {(!sidebarCollapsed || isMobile) && (
              <span className="font-bold text-base tracking-tight text-foreground">
                Lisa
              </span>
            )}
          </Link>

          {/* Close Sidebar Drawer button (Visible only on Mobile) */}
          {isMobile && (
            <Button
              onClick={() => setSidebarCollapsed(true)}
              variant="ghost"
              size="icon"
              aria-label="Close navigation menu"
              className="h-8 w-8 hover:bg-secondary text-muted-foreground hover:text-foreground shrink-0 cursor-pointer"
            >
              <X className="h-4.5 w-4.5" />
            </Button>
          )}
        </div>

        {/* Primary 4 Nav Items */}
        <div className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
          <nav className="space-y-1">
            {primaryNavItems.map((item) => {
              const Icon = item.icon
              const active = isRouteActive(item.path)

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => isMobile && setSidebarCollapsed(true)}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors group relative cursor-pointer outline-none select-none",
                    active
                      ? "text-primary-foreground font-semibold"
                      : "text-muted-foreground hover:bg-secondary/60 hover:text-foreground"
                  )}
                >
                  {active && (
                    <motion.div
                      layoutId="sidebarActiveItem"
                      className="absolute inset-0 bg-primary rounded-lg shadow-sm"
                      transition={springTransition}
                    />
                  )}
                  <Icon className={cn("h-4 w-4 shrink-0 z-10", active ? "text-primary-foreground" : "text-muted-foreground group-hover:text-foreground")} />
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
          </nav>
        </div>

        {/* Settings Navigation Item (Divider above) */}
        <div className="px-3 pb-2 pt-1 border-t border-border/70 shrink-0">
          <Link
            to="/settings"
            onClick={() => isMobile && setSidebarCollapsed(true)}
            className={cn(
              "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors group relative cursor-pointer outline-none select-none",
              isRouteActive("/settings")
                ? "text-primary-foreground font-semibold"
                : "text-muted-foreground hover:bg-secondary/60 hover:text-foreground"
            )}
          >
            {isRouteActive("/settings") && (
              <motion.div
                layoutId="sidebarActiveItem"
                className="absolute inset-0 bg-primary rounded-lg shadow-sm"
                transition={springTransition}
              />
            )}
            <Settings className={cn("h-4 w-4 shrink-0 z-10", isRouteActive("/settings") ? "text-primary-foreground" : "text-muted-foreground group-hover:text-foreground")} />
            {(!sidebarCollapsed || isMobile) && (
              <span className="z-10">Settings</span>
            )}
            {sidebarCollapsed && !isMobile && (
              <div className="absolute left-16 px-2 py-1 bg-popover text-popover-foreground text-xs rounded border border-border opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-50 shadow-md">
                Settings
              </div>
            )}
          </Link>
        </div>

        {/* User profile / Session footer */}
        <div className="p-3 border-t border-border/70 shrink-0">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <div className={cn(
                "flex items-center gap-3 p-2 rounded-lg hover:bg-secondary/60 cursor-pointer transition-all outline-none",
                sidebarCollapsed && !isMobile ? "justify-center" : ""
              )}>
                <Avatar className="h-8 w-8 border border-border shrink-0">
                  <AvatarFallback className="bg-primary/10 text-primary font-semibold text-xs">{fallbackChar}</AvatarFallback>
                </Avatar>
                {(!sidebarCollapsed || isMobile) && (
                  <div className="flex-1 text-left min-w-0">
                    <p className="text-xs font-semibold truncate text-foreground leading-none capitalize">{displayName}</p>
                    <p className="text-[10px] text-muted-foreground truncate mt-1">Personal AIOS</p>
                  </div>
                )}
              </div>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56 border-border/80 bg-popover/95 backdrop-blur-md">
              <DropdownMenuLabel className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
                {userEmail}
              </DropdownMenuLabel>
              <DropdownMenuSeparator className="bg-border/60" />
              <DropdownMenuItem
                onClick={() => navigate("/settings/account")}
                className="cursor-pointer gap-2 text-xs"
              >
                <User className="h-3.5 w-3.5" />
                Profile Details
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => navigate("/settings")}
                className="cursor-pointer gap-2 text-xs"
              >
                <Settings className="h-3.5 w-3.5" />
                Preference Settings
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => navigate("/settings/developer")}
                className="cursor-pointer gap-2 text-xs"
              >
                <Code className="h-3.5 w-3.5" />
                Developer / AIOS
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-border/60" />
              <DropdownMenuItem
                onClick={() => clearAuth()}
                className="cursor-pointer gap-2 text-xs text-destructive hover:bg-destructive/10"
              >
                <LogOut className="h-3.5 w-3.5" />
                Sign Out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </motion.aside>

      {/* 2. Main Content Area */}
      <div className="flex-1 flex flex-col h-full bg-background relative overflow-hidden">
        
        {/* Top Command Bar */}
        <header className="h-16 flex items-center justify-between px-4 sm:px-6 border-b border-border/70 bg-background/50 backdrop-blur-md z-30 select-none shrink-0 gap-4">
          
          {/* Hamburger Sidebar Trigger Menu button (Visible only on mobile when sidebar is collapsed) */}
          {isMobile && (
            <Button
              onClick={() => setSidebarCollapsed(false)}
              variant="ghost"
              size="icon"
              aria-label="Open navigation menu"
              className="h-8.5 w-8.5 hover:bg-secondary text-muted-foreground hover:text-foreground shrink-0 cursor-pointer"
            >
              <Menu className="h-4.5 w-4.5" />
            </Button>
          )}

          {/* Search Box palette launcher */}
          <button
            onClick={() => setPaletteOpen(true)}
            className="flex-1 max-w-md flex items-center justify-between px-3 py-2 rounded-lg bg-secondary/30 border border-border/50 text-muted-foreground/70 hover:text-foreground hover:border-primary/40 cursor-pointer transition-all text-xs outline-none min-w-0"
          >
            <div className="flex items-center gap-2 min-w-0">
              <Search className="h-3.5 w-3.5 shrink-0" />
              <span className="truncate hidden sm:inline">Search, ask, or execute command...</span>
              <span className="truncate inline sm:hidden">Search...</span>
            </div>
            <div className="hidden sm:flex items-center gap-0.5 px-1.5 py-0.5 rounded border border-border/60 bg-secondary/80 text-[9px] font-mono font-medium shrink-0">
              <Command className="h-2.5 w-2.5 shrink-0" />
              <span>K</span>
            </div>
          </button>

          {/* Right Header Controls */}
          <div className="flex items-center gap-2 shrink-0">
            {/* Inspector Toggle button */}
            <Button
              onClick={toggleInspector}
              variant={inspectorOpen ? "secondary" : "ghost"}
              size="icon"
              aria-label={inspectorOpen ? "Close inspector" : "Open inspector"}
              className="h-8 w-8 hover:bg-secondary cursor-pointer text-muted-foreground hover:text-foreground"
              title="Toggle Inspector (⌘I)"
            >
              <PanelRightOpen className="h-4.5 w-4.5" />
            </Button>
          </div>
        </header>

        {/* Viewport & Inspector Container */}
        <div className="flex-1 flex overflow-hidden w-full relative">
          
          {/* Main scroll viewport */}
          <div className={cn(
            "flex-1 h-full",
            location.pathname === "/assistant" || location.pathname === "/workspace"
              ? "overflow-hidden"
              : "overflow-y-auto px-4 sm:px-8 py-6"
          )}>
            <main className={cn(
              "w-full h-full",
              location.pathname === "/assistant" || location.pathname === "/workspace"
                ? "max-w-none"
                : "max-w-5xl mx-auto pb-8"
            )}>
              <AnimatePresence mode="wait">
                <motion.div
                  key={location.pathname}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1, transition: { duration: 0.12 } }}
                  exit={{ opacity: 0, transition: { duration: 0.06 } }}
                  className={cn(
                    location.pathname === "/assistant" || location.pathname === "/workspace"
                      ? "h-full w-full"
                      : ""
                  )}
                >
                  <Outlet />
                </motion.div>
              </AnimatePresence>
            </main>
          </div>

          {/* Right Inspector panel */}
          <InspectorPanel isOpen={inspectorOpen} onToggle={toggleInspector} />
        </div>
      </div>

      {/* Command Palette */}
      <CommandPalette isOpen={paletteOpen} onClose={() => setPaletteOpen(false)} />
    </div>
  )
}
