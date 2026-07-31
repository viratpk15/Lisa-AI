import React, { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { ArrowRight, Search, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"
import { dashboardCardVariants } from "@/lib/motion"

export const Hero: React.FC = () => {
  const [greeting, setGreeting] = useState("Welcome")
  const userName = "Virat"

  useEffect(() => {
    const updateGreeting = () => {
      const hour = new Date().getHours()
      if (hour < 12) setGreeting("Good Morning")
      else if (hour < 18) setGreeting("Good Afternoon")
      else setGreeting("Good Evening")
    }

    updateGreeting()
    // Update every minute to keep greeting correct if left open
    const interval = setInterval(updateGreeting, 60000)
    return () => clearInterval(interval)
  }, [])

  const handleQuickSearch = () => {
    const event = new CustomEvent("open-command-palette")
    window.dispatchEvent(event)
  }

  const handleContinueWorking = () => {
    // Smooth scroll to Continue Working section
    const element = document.getElementById("continue-working-section")
    if (element) {
      element.scrollIntoView({ behavior: "smooth", block: "start" })
    }
  }

  return (
    <motion.div
      variants={dashboardCardVariants}
      initial="initial"
      animate="animate"
      whileHover="hover"
      className="relative overflow-hidden rounded-xl border border-border/60 bg-card/25 backdrop-blur-md p-6 sm:p-8"
    >
      {/* Decorative ambient gradient backdrop */}
      <div className="absolute top-0 right-0 w-80 h-80 bg-primary/5 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />
      <div className="absolute bottom-0 left-0 w-60 h-60 bg-primary/3 rounded-full blur-3xl pointer-events-none -ml-20 -mb-20" />

      <div className="relative z-10 space-y-4 max-w-2xl">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-primary/10 border border-primary/20 rounded-full text-xs font-mono font-medium text-primary">
          <Sparkles className="h-3.5 w-3.5" />
          <span>Jarvis Kernel v1.0.0-alpha</span>
        </div>

        <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight bg-linear-to-r from-foreground via-foreground/90 to-primary bg-clip-text text-transparent">
          {greeting}, {userName}
        </h1>

        <p className="text-sm sm:text-base text-muted-foreground leading-relaxed">
          Welcome back to your AI Operating System. All cognitive threads, vector memory indexers, and local tools are ready. What shall we orchestrate today?
        </p>

        <div className="flex flex-wrap items-center gap-3 pt-2">
          <Button
            onClick={handleContinueWorking}
            className="h-9.5 px-4 font-semibold text-xs gap-1.5 shadow-md shadow-primary/10 hover:shadow-primary/20 transition-all cursor-pointer"
          >
            Continue working
            <ArrowRight className="h-3.5 w-3.5" />
          </Button>

          <Button
            onClick={handleQuickSearch}
            variant="outline"
            className="h-9.5 px-4 font-semibold text-xs gap-2 border-border/80 hover:bg-secondary/60 cursor-pointer"
          >
            <Search className="h-3.5 w-3.5 text-muted-foreground" />
            Quick Search
            <kbd className="hidden sm:inline-flex h-5 select-none items-center gap-0.5 rounded border border-border/80 bg-secondary/80 px-1.5 font-mono text-[9px] font-medium text-muted-foreground/80">
              ⌘K
            </kbd>
          </Button>
        </div>
      </div>
    </motion.div>
  )
}
