import { CheckCircle2, ShieldAlert, Zap, Clock, AlertTriangle } from "lucide-react"
import type { PermissionLevel } from "../../types/tools.types"

interface StatusChipProps {
  type: "permission" | "approval" | "streaming" | "async" | "enabled"
  value?: string | boolean | PermissionLevel
}

export function StatusChip({ type, value }: StatusChipProps) {
  if (type === "permission") {
    const level = (value as PermissionLevel) || "USER"
    const isHighPrivilege = level === "ADMIN" || level === "SYSTEM" || level === "INTERNAL"
    return (
      <span
        className={`inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-mono font-semibold rounded border ${
          isHighPrivilege
            ? "bg-rose-500/10 text-rose-400 border-rose-500/30"
            : "bg-cyan-500/10 text-cyan-400 border-cyan-500/30"
        }`}
      >
        <ShieldAlert className="h-3 w-3" />
        {level}
      </span>
    )
  }

  if (type === "approval") {
    const requires = Boolean(value)
    if (!requires) return null
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-mono font-semibold rounded bg-amber-500/10 text-amber-400 border border-amber-500/30">
        <AlertTriangle className="h-3 w-3" />
        Approval Required
      </span>
    )
  }

  if (type === "streaming") {
    const supports = Boolean(value)
    if (!supports) return null
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-mono font-semibold rounded bg-violet-500/10 text-violet-400 border border-violet-500/30">
        <Zap className="h-3 w-3" />
        SSE Stream
      </span>
    )
  }

  if (type === "async") {
    const supports = Boolean(value)
    if (!supports) return null
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-mono font-semibold rounded bg-blue-500/10 text-blue-400 border border-blue-500/30">
        <Clock className="h-3 w-3" />
        Async
      </span>
    )
  }

  if (type === "enabled") {
    const isEnabled = value !== false
    return (
      <span
        className={`inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-mono font-semibold rounded border ${
          isEnabled
            ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
            : "bg-gray-500/10 text-gray-400 border-gray-500/30"
        }`}
      >
        <CheckCircle2 className="h-3 w-3" />
        {isEnabled ? "Active" : "Disabled"}
      </span>
    )
  }

  return null
}
