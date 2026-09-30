/**
 * Lisa AIOS — Local Transport & Mobility Guide
 * Sequential transit routes (airport to hotel, sightseeing, return) with verified providers.
 */

import {
  Car,
  Train,
  Bus,
  Footprints,
  ExternalLink,
  ArrowRight,
  Clock,
  Compass,
} from "lucide-react"
import type { RouteGuide, TransportSegment } from "../types"
import { formatCurrency } from "../types"

interface TransportCardProps {
  routeGuide: RouteGuide
  currency: string
}

export const TransportCard: React.FC<TransportCardProps> = ({
  routeGuide,
  currency,
}) => {
  const getModeIcon = (mode: string) => {
    switch (mode) {
      case "metro":
      case "train":
        return Train
      case "taxi":
      case "ride_hail":
        return Car
      case "bus":
        return Bus
      case "walking":
        return Footprints
      default:
        return Compass
    }
  }

  const formatCost = (cost: number) => {
    if (cost === 0) return "Included / Free"
    return formatCurrency(cost, currency)
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <Compass className="h-4 w-4" />
            </span>
            <h3 className="text-base font-semibold text-foreground">Local Transit & Route Transfers</h3>
          </div>
          <p className="text-xs text-muted-foreground mt-0.5">
            Sequential point-to-point connections with estimated durations and verified provider links.
          </p>
        </div>

        <div className="text-xs font-mono text-muted-foreground bg-secondary/40 px-3 py-1.5 rounded-lg border border-border/60 self-start sm:self-auto">
          Est. Transit Total: <span className="font-bold text-foreground">{formatCurrency(routeGuide.total_estimated_cost, currency)}</span>
        </div>
      </div>

      {/* Sequential Segments */}
      <div className="space-y-2.5">
        {routeGuide.segments.map((seg: TransportSegment, idx: number) => {
          const Icon = getModeIcon(seg.mode)

          return (
            <div
              key={seg.segment_id || idx}
              className="rounded-xl border border-border/60 bg-card/60 backdrop-blur-xs p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:border-border transition-all"
            >
              <div className="flex items-start gap-3">
                <div className="p-2 rounded-lg bg-secondary/70 text-primary border border-border/50 shrink-0 mt-0.5">
                  <Icon className="h-4 w-4" />
                </div>

                <div className="space-y-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs font-semibold text-foreground">{seg.from_name}</span>
                    <ArrowRight className="h-3 w-3 text-muted-foreground" />
                    <span className="text-xs font-semibold text-foreground">{seg.to_name}</span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-secondary/80 text-muted-foreground border border-border/40 capitalize">
                      {seg.mode.replace("_", " ")}
                    </span>
                  </div>

                  {seg.notes && (
                    <p className="text-[11px] text-muted-foreground leading-relaxed">
                      {seg.notes}
                    </p>
                  )}
                </div>
              </div>

              {/* Time, Cost & Provider Link */}
              <div className="flex items-center gap-4 self-end sm:self-auto shrink-0">
                <div className="text-right font-mono text-xs">
                  <div className="flex items-center gap-1 text-muted-foreground justify-end text-[11px]">
                    <Clock className="h-3 w-3" />
                    <span>{seg.estimated_duration_mins} min</span>
                  </div>
                  <div className="font-bold text-foreground">
                    {formatCost(seg.estimated_cost)}
                  </div>
                </div>

                {seg.deep_link && (
                  <a
                    href={seg.deep_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-1.5 rounded-lg border border-border/60 bg-secondary/40 hover:bg-secondary text-muted-foreground hover:text-foreground transition-all cursor-pointer"
                    title={`Open ${seg.provider_name || "transit guide"}`}
                  >
                    <ExternalLink className="h-3.5 w-3.5" />
                  </a>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
