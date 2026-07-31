import React, { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { CheckCircle2, Layers, Clock, X, Info } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

interface NotificationItem {
  id: string
  title: string
  message: string
  time: string
  type: "success" | "info" | "warning"
}

export const Notifications: React.FC = () => {
  const [notifications, setNotifications] = useState<NotificationItem[]>([
    {
      id: "nt-1",
      title: "Research Complete",
      message: "Orchestrated web agent finished compiling prompt optimization guides.",
      time: "2m ago",
      type: "success"
    },
    {
      id: "nt-2",
      title: "Project Saved",
      message: "Sync complete for workspace: Jarvis Core. 0 pending file modifications.",
      time: "15m ago",
      type: "info"
    },
    {
      id: "nt-3",
      title: "Memory Store Updated",
      message: "Cleaned up 12 expired session tokens from memory cache buffer.",
      time: "1h ago",
      type: "success"
    },
    {
      id: "nt-4",
      title: "Backup Sync Reminder",
      message: "System recommends a workspace backup. Vector dimensions have grown 12% today.",
      time: "3h ago",
      type: "warning"
    }
  ])

  const dismissNotification = (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    setNotifications((prev) => prev.filter((nt) => nt.id !== id))
  }

  const getIcon = (type: NotificationItem["type"]) => {
    switch (type) {
      case "success":
        return <CheckCircle2 className="h-4 w-4 text-emerald-400" />
      case "info":
        return <Layers className="h-4 w-4 text-primary" />
      case "warning":
        return <Info className="h-4 w-4 text-amber-400" />
    }
  }

  const getBorderColor = (type: NotificationItem["type"]) => {
    switch (type) {
      case "success":
        return "border-emerald-500/20 hover:border-emerald-500/40"
      case "info":
        return "border-primary/20 hover:border-primary/40"
      case "warning":
        return "border-amber-500/20 hover:border-amber-500/40"
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-sm font-mono font-semibold tracking-wider text-muted-foreground uppercase">
            Notifications
          </h2>
          <p className="text-xs text-muted-foreground mt-0.5">Urgent event warnings and task completion logs.</p>
        </div>
        {notifications.length > 0 && (
          <button
            onClick={() => setNotifications([])}
            className="text-[10px] font-mono text-muted-foreground hover:text-foreground cursor-pointer focus:outline-none hover:underline"
          >
            Clear All
          </button>
        )}
      </div>

      <div className="space-y-2">
        <AnimatePresence initial={false}>
          {notifications.length > 0 ? (
            notifications.map((nt) => (
              <motion.div
                key={nt.id}
                initial={{ opacity: 0, height: 0, y: -10 }}
                animate={{ opacity: 1, height: "auto", y: 0 }}
                exit={{ opacity: 0, height: 0, y: 10 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <Card className={`border bg-card/25 backdrop-blur-md transition-all duration-300 relative group ${getBorderColor(nt.type)}`}>
                  <CardContent className="p-3.5 flex items-start gap-3">
                    
                    <div className="pt-0.5 shrink-0">
                      {getIcon(nt.type)}
                    </div>

                    <div className="space-y-0.5 flex-1 min-w-0 pr-4">
                      <span className="font-bold text-xs text-foreground block">
                        {nt.title}
                      </span>
                      <p className="text-[10px] text-muted-foreground leading-normal">
                        {nt.message}
                      </p>
                      <span className="text-[9px] font-mono text-muted-foreground/60 flex items-center gap-1 pt-1">
                        <Clock className="h-2.5 w-2.5" />
                        {nt.time}
                      </span>
                    </div>

                    <button
                      onClick={(e) => dismissNotification(nt.id, e)}
                      className="absolute top-3 right-3 p-0.5 rounded hover:bg-secondary text-muted-foreground/45 hover:text-foreground opacity-0 group-hover:opacity-100 focus:opacity-100 transition-opacity cursor-pointer"
                      title="Dismiss"
                    >
                      <X className="h-3 w-3" />
                    </button>

                  </CardContent>
                </Card>
              </motion.div>
            ))
          ) : (
            <div className="p-6 border border-dashed border-border/60 bg-secondary/10 rounded-xl text-center flex flex-col items-center justify-center gap-2">
              <CheckCircle2 className="h-6 w-6 text-muted-foreground/40" />
              <div>
                <p className="text-xs font-semibold text-muted-foreground">All notifications cleared</p>
                <p className="text-[10px] text-muted-foreground/60 mt-0.5">We'll alert you if active threads find warnings.</p>
              </div>
            </div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
