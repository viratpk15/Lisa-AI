import React from "react"
import { TrendingUp, TrendingDown, Minus } from "lucide-react"

interface MetricsCardProps {
  title: string
  value: string | number
  unit?: string
  trend?: "up" | "down" | "neutral"
  trendValue?: string
  icon: React.ReactNode
  accentColor?: "cyan" | "emerald" | "amber" | "rose" | "violet"
}

export function MetricsCard({
  title,
  value,
  unit,
  trend,
  trendValue,
  icon,
  accentColor = "cyan",
}: MetricsCardProps) {
  const getAccentStyles = () => {
    switch (accentColor) {
      case "emerald":
        return {
          bg: "bg-emerald-500/10",
          border: "border-emerald-500/30",
          text: "text-emerald-400",
        }
      case "amber":
        return {
          bg: "bg-amber-500/10",
          border: "border-amber-500/30",
          text: "text-amber-400",
        }
      case "rose":
        return {
          bg: "bg-rose-500/10",
          border: "border-rose-500/30",
          text: "text-rose-400",
        }
      case "violet":
        return {
          bg: "bg-violet-500/10",
          border: "border-violet-500/30",
          text: "text-violet-400",
        }
      default:
        return {
          bg: "bg-cyan-500/10",
          border: "border-cyan-500/30",
          text: "text-cyan-400",
        }
    }
  }

  const styles = getAccentStyles()

  return (
    <div className="p-4 bg-secondary/15 border border-border/40 rounded-xl flex flex-col justify-between space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-mono text-muted-foreground uppercase">{title}</span>
        <div className={`p-1.5 rounded-lg border ${styles.bg} ${styles.border} ${styles.text}`}>
          {icon}
        </div>
      </div>

      <div className="flex items-baseline gap-1.5">
        <span className="text-2xl font-bold font-mono text-foreground">{value}</span>
        {unit && <span className="text-xs text-muted-foreground font-mono">{unit}</span>}
      </div>

      {trendValue && (
        <div className="flex items-center gap-1 text-[10px] font-mono">
          {trend === "up" ? (
            <TrendingUp className="h-3 w-3 text-emerald-400" />
          ) : trend === "down" ? (
            <TrendingDown className="h-3 w-3 text-rose-400" />
          ) : (
            <Minus className="h-3 w-3 text-muted-foreground" />
          )}
          <span
            className={
              trend === "up" ? "text-emerald-400" : trend === "down" ? "text-rose-400" : "text-muted-foreground"
            }
          >
            {trendValue}
          </span>
        </div>
      )}
    </div>
  )
}
