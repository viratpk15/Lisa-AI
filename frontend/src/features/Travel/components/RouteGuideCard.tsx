/**
 * Lisa AIOS — Route Guide & Pre-Departure Checklist
 * Interactive preparation checklist and mobility tips for international travel.
 */

import { useState } from "react"
import {
  CheckSquare,
  Square,
  ShieldCheck,
  ClipboardList,
} from "lucide-react"
import type { RouteGuide } from "../types"

interface RouteGuideCardProps {
  routeGuide: RouteGuide
  destination: string
}

export function RouteGuideCard({
  routeGuide,
  destination,
}: RouteGuideCardProps) {
  const [checkedItems, setCheckedItems] = useState<Record<number, boolean>>({})

  const toggleCheck = (idx: number) => {
    setCheckedItems((prev) => ({
      ...prev,
      [idx]: !prev[idx],
    }))
  }

  const items = routeGuide.preparation_items || [
    "Verify passport validity (at least 6 months beyond travel dates)",
    "Check visa requirements and electronic entry forms",
    "Acquire local transit card or load digital pass to mobile wallet",
    "Download offline maps in Google Maps or Apple Maps",
    "Bring appropriate destination power adapter and voltage converter",
    "Notify credit card issuers of travel dates to prevent fraud locks",
  ]

  const completedCount = Object.values(checkedItems).filter(Boolean).length

  return (
    <div className="rounded-2xl border border-border/70 bg-card/60 backdrop-blur-md p-5 sm:p-6 shadow-xs space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-primary/10 text-primary border border-primary/20">
              <ClipboardList className="h-4 w-4" />
            </span>
            <h3 className="text-base font-semibold text-foreground">
              Pre-Departure Readiness Checklist
            </h3>
          </div>
          <p className="text-xs text-muted-foreground mt-0.5">
            Essential documentation, connectivity, and mobility items for {destination}.
          </p>
        </div>

        <div className="text-xs font-mono text-muted-foreground bg-secondary/40 px-3 py-1.5 rounded-lg border border-border/60 self-start sm:self-auto flex items-center gap-2">
          <ShieldCheck className="h-3.5 w-3.5 text-primary" />
          <span>
            {completedCount} of {items.length} Ready
          </span>
        </div>
      </div>

      {/* Interactive Checklist */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-1">
        {items.map((item: string, idx: number) => {
          const isDone = !!checkedItems[idx]

          return (
            <button
              key={idx}
              type="button"
              onClick={() => toggleCheck(idx)}
              className={`p-3 rounded-xl border text-left text-xs transition-all flex items-start gap-2.5 cursor-pointer select-none ${
                isDone
                  ? "bg-secondary/20 border-border/40 text-muted-foreground line-through"
                  : "bg-secondary/40 border-border/70 text-foreground hover:bg-secondary/60 hover:border-primary/40"
              }`}
            >
              {isDone ? (
                <CheckSquare className="h-4 w-4 text-emerald-400 shrink-0 mt-0.5" />
              ) : (
                <Square className="h-4 w-4 text-muted-foreground shrink-0 mt-0.5" />
              )}
              <span className="leading-snug">{item}</span>
            </button>
          )
        })}
      </div>
    </div>
  )
}
