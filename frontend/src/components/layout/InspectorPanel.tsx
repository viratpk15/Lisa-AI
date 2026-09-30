import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import {
  Sparkles,
  PanelRightClose,
  Mail,
  Info,
  ShieldCheck,
  ShieldAlert,
  FileText,
  ListTodo,
  Bot
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { panelVariants } from "@/lib/motion"
import { useInspectorStore } from "@/features/Workspace/inspectorStore"

interface InspectorPanelProps {
  isOpen: boolean
  onToggle: () => void
}

type TabType = "context" | "email"

export const InspectorPanel: React.FC<InspectorPanelProps> = ({ isOpen, onToggle }) => {
  const [activeTab, setActiveTab] = useState<TabType>("context")
  const [windowWidth, setWindowWidth] = useState(typeof window !== "undefined" ? window.innerWidth : 1200)

  const aiContext = useInspectorStore((s) => s.aiContext)
  const emailContext = useInspectorStore((s) => s.emailContext)

  // Track window resizing for responsive overlay rendering
  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth)
    window.addEventListener("resize", handleResize)
    return () => window.removeEventListener("resize", handleResize)
  }, [])

  const tabs = [
    { id: "context" as const, name: "AI Context", icon: Sparkles },
    { id: "email" as const, name: "Email Context", icon: Mail },
  ]

  const renderTabContent = () => {
    switch (activeTab) {
      case "context":
        if (!aiContext) {
          return (
            <div className="flex flex-col items-center justify-center p-8 text-center text-muted-foreground space-y-3">
              <div className="p-3 rounded-full bg-secondary/50 border border-border/40">
                <Sparkles className="h-6 w-6 text-primary/70" />
              </div>
              <div className="space-y-1.5">
                <p className="text-xs font-semibold text-foreground">No active context</p>
                <p className="text-[11px] text-muted-foreground max-w-[210px] leading-relaxed">
                  Context details and active capability status will appear here during conversations with Lisa.
                </p>
              </div>
            </div>
          )
        }

        return (
          <div className="space-y-4 text-xs">
            {/* Session Card */}
            <div className="p-3.5 rounded-xl border border-border/60 bg-secondary/20 space-y-2">
              <div className="flex items-center gap-2 text-foreground font-semibold">
                <Bot className="h-4 w-4 text-primary shrink-0" />
                <span className="truncate">{aiContext.sessionTitle || "Current Conversation"}</span>
              </div>
              <div className="flex items-center justify-between text-[11px] font-mono text-muted-foreground pt-1 border-t border-border/40">
                <span>Model:</span>
                <span className="text-foreground font-medium">{aiContext.model || "Lisa Standard"}</span>
              </div>
              <div className="flex items-center justify-between text-[11px] font-mono text-muted-foreground">
                <span>Status:</span>
                <span className={cn(
                  "font-medium capitalize",
                  aiContext.status === "thinking" ? "text-amber-400 animate-pulse" :
                  aiContext.status === "streaming" ? "text-emerald-400" :
                  "text-muted-foreground"
                )}>
                  {aiContext.status === "thinking" ? "Thinking..." :
                   aiContext.status === "streaming" ? "Generating response..." :
                   "Idle"}
                </span>
              </div>
            </div>

            {/* Active Attachment / Source */}
            {aiContext.activeAttachment && (
              <div className="p-3 rounded-xl border border-border/60 bg-secondary/20 space-y-1.5">
                <div className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground font-semibold flex items-center gap-1.5">
                  <FileText className="h-3.5 w-3.5 text-primary" />
                  <span>Referenced Document</span>
                </div>
                <p className="text-xs text-foreground font-medium truncate">{aiContext.activeAttachment}</p>
              </div>
            )}

            {/* Capability Overview */}
            <div className="p-3 rounded-xl border border-border/40 bg-secondary/10 space-y-1 text-muted-foreground leading-relaxed">
              <p className="font-semibold text-foreground text-[11px]">Active Capabilities</p>
              <p className="text-[10px]">
                Lisa can reference your connected files, summarize emails, and retrieve information to assist your workflow.
              </p>
            </div>
          </div>
        )

      case "email":
        if (!emailContext) {
          return (
            <div className="flex flex-col items-center justify-center p-8 text-center text-muted-foreground space-y-3">
              <div className="p-3 rounded-full bg-secondary/50 border border-border/40">
                <Mail className="h-6 w-6 text-primary/70" />
              </div>
              <div className="space-y-1.5">
                <p className="text-xs font-semibold text-foreground">No active context</p>
                <p className="text-[11px] text-muted-foreground max-w-[210px] leading-relaxed">
                  Select an email from your inbox to inspect classification, priority, action items, and sender verification.
                </p>
              </div>
            </div>
          )
        }

        return (
          <div className="space-y-4 text-xs">
            {/* Email Header Overview */}
            <div className="p-3.5 rounded-xl border border-border/60 bg-secondary/20 space-y-2">
              <p className="font-semibold text-foreground truncate">{emailContext.subject || "(No Subject)"}</p>
              <p className="text-[11px] text-muted-foreground truncate">{emailContext.sender}</p>

              <div className="flex items-center justify-between pt-2 border-t border-border/40">
                <span className="text-[11px] font-mono text-muted-foreground">Category</span>
                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-secondary border border-border/50 uppercase">
                  {emailContext.category || "Unclassified"}
                </span>
              </div>

              {emailContext.priority_score !== null && (
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-mono text-muted-foreground">Priority Score</span>
                  <span className={cn(
                    "text-[11px] font-mono font-bold px-2 py-0.5 rounded border",
                    emailContext.priority_score >= 80 ? "bg-amber-500/10 text-amber-400 border-amber-500/30" :
                    emailContext.priority_score >= 50 ? "bg-cyan-500/10 text-cyan-400 border-cyan-500/30" :
                    "bg-secondary text-muted-foreground border-border/50"
                  )}>
                    {emailContext.priority_score} / 100
                  </span>
                </div>
              )}
            </div>

            {/* Sender Authentication Verification */}
            <div className="p-3.5 rounded-xl border border-border/60 bg-secondary/20 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-mono font-semibold text-muted-foreground uppercase">Sender Security</span>
                {emailContext.verification?.is_verified ? (
                  <span className="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/30 flex items-center gap-1">
                    <ShieldCheck className="h-3 w-3" /> Verified
                  </span>
                ) : (
                  <span className="text-[10px] font-mono font-bold text-muted-foreground bg-secondary px-2 py-0.5 rounded border border-border/50 flex items-center gap-1">
                    <ShieldAlert className="h-3 w-3" /> Unverified
                  </span>
                )}
              </div>

              <div className="grid grid-cols-3 gap-1 pt-1 text-center font-mono text-[10px]">
                <div className="p-1.5 rounded bg-secondary/40 border border-border/40">
                  <div className="text-muted-foreground">SPF</div>
                  <div className="font-bold text-foreground mt-0.5">{emailContext.verification?.spf_status || "N/A"}</div>
                </div>
                <div className="p-1.5 rounded bg-secondary/40 border border-border/40">
                  <div className="text-muted-foreground">DKIM</div>
                  <div className="font-bold text-foreground mt-0.5">{emailContext.verification?.dkim_status || "N/A"}</div>
                </div>
                <div className="p-1.5 rounded bg-secondary/40 border border-border/40">
                  <div className="text-muted-foreground">DMARC</div>
                  <div className="font-bold text-foreground mt-0.5">{emailContext.verification?.dmarc_status || "N/A"}</div>
                </div>
              </div>
            </div>

            {/* Action Items / Deadlines */}
            <div className="p-3.5 rounded-xl border border-border/60 bg-secondary/20 space-y-2">
              <div className="flex items-center gap-1.5 text-foreground font-semibold">
                <ListTodo className="h-3.5 w-3.5 text-primary" />
                <span>Action Items</span>
              </div>
              {emailContext.action_items && emailContext.action_items.length > 0 ? (
                <ul className="space-y-1.5 pl-1">
                  {emailContext.action_items.map((act, i) => (
                    <li key={i} className="text-muted-foreground text-[11px] flex items-start gap-2">
                      <span className="text-primary font-bold">•</span>
                      <span>{act}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-[11px] text-muted-foreground">No action required for this message.</p>
              )}

              {emailContext.deadline && (
                <div className="pt-2 border-t border-border/40 text-[11px] font-mono text-muted-foreground">
                  <span>Deadline: </span>
                  <span className="text-amber-400 font-semibold">{emailContext.deadline}</span>
                </div>
              )}
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
          "h-full border-l border-border/80 bg-sidebar flex flex-col shrink-0 overflow-hidden relative select-none z-50",
          isOverlay ? "absolute top-0 right-0 shadow-2xl h-full" : "relative"
        )}
      >
        {/* Panel Header */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-border/80 shrink-0">
          <div className="flex items-center gap-2">
            <Info className="h-4 w-4 text-primary" />
            <span className="font-bold text-sm tracking-tight">Inspector</span>
          </div>
          <Button
            onClick={onToggle}
            variant="ghost"
            size="icon-sm"
            aria-label="Close inspector"
            className="hover:bg-secondary cursor-pointer text-muted-foreground hover:text-foreground"
          >
            <PanelRightClose className="h-4 w-4" />
          </Button>
        </div>

        {/* Tab Switcher */}
        <div className="grid grid-cols-2 gap-1 p-2 bg-secondary/20 border-b border-border/50 shrink-0">
          {tabs.map((tab) => {
            const TabIcon = tab.icon
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  "flex items-center justify-center p-2 rounded-md text-xs font-medium transition-all gap-1.5 cursor-pointer outline-none border relative select-none",
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
