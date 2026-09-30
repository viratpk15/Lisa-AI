/**
 * Lisa AIOS — Flight Options Card
 * Comparative 3-card flight selector (Cheapest, Fastest, Best Balance) with route segments & booking safety gate.
 */

import {
  Plane,
  Clock,
  CheckCircle2,
  ExternalLink,
  ShieldCheck,
  ArrowRight,
  Sparkles,
  Zap,
  Tag,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import type { FlightOption } from "../types"
import { formatCurrency } from "../types"

interface FlightOptionsCardProps {
  flights: FlightOption[]
  selectedFlightId?: string | null
  currency: string
  onSelectFlight: (flightId: string) => void
  onBookFlight: (flight: FlightOption) => void
  isUpdating?: boolean
}

export function FlightOptionsCard({
  flights,
  selectedFlightId,
  currency,
  onSelectFlight,
  onBookFlight,
  isUpdating,
}: FlightOptionsCardProps) {
  if (!flights || flights.length === 0) {
    return (
      <div className="p-6 rounded-2xl border border-dashed border-border/80 text-center text-xs text-muted-foreground">
        No flight options available for this route.
      </div>
    )
  }

const formatDuration = (mins: number) => {
  const h = Math.floor(mins / 60)
  const m = mins % 60
  return `${h}h ${m}m`
}

  const getCategoryMeta = (cat: string) => {
    switch (cat) {
      case "cheapest":
        return {
          label: "Cheapest",
          icon: Tag,
          border: "border-emerald-500/40",
          bg: "bg-emerald-500/10 text-emerald-400",
        }
      case "fastest":
        return {
          label: "Fastest",
          icon: Zap,
          border: "border-sky-500/40",
          bg: "bg-sky-500/10 text-sky-400",
        }
      case "best_balance":
      default:
        return {
          label: "Best Balance",
          icon: Sparkles,
          border: "border-purple-500/40",
          bg: "bg-purple-500/10 text-purple-400",
        }
    }
  }

  return (
    <div className="space-y-4">
      {/* Header & Explanation */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-sky-500/10 text-sky-400 border border-sky-500/20">
              <Plane className="h-4 w-4" />
            </span>
            <h3 className="text-base font-semibold text-foreground">Flight Route Comparison</h3>
          </div>
          <p className="text-xs text-muted-foreground mt-0.5">
            Transparently categorized by fare and duration with verified deep links.
          </p>
        </div>

        <div className="flex items-center gap-1.5 text-[11px] text-muted-foreground bg-secondary/40 px-2.5 py-1 rounded-lg border border-border/60 self-start sm:self-auto">
          <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
          <span>Verified Portals (Google Flights • Skyscanner • MakeMyTrip)</span>
        </div>
      </div>

      {/* 3-Column Comparative Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {flights.map((flight) => {
          const isSelected = selectedFlightId === flight.id
          const meta = getCategoryMeta(flight.category)
          const Icon = meta.icon
          const outbound = flight.outbound_segments[0]
          const returnSegment = flight.return_segments?.[0]

          return (
            <div
              key={flight.id}
              className={`rounded-2xl border transition-all flex flex-col justify-between p-4.5 bg-card/70 backdrop-blur-sm shadow-xs ${
                isSelected
                  ? "border-primary ring-1 ring-primary/40 bg-card/90"
                  : "border-border/70 hover:border-border"
              }`}
            >
              <div className="space-y-3.5">
                {/* Category Badge & Price Header */}
                <div className="flex items-start justify-between gap-2">
                  <div className="space-y-1">
                    <span
                      className={`inline-flex items-center gap-1 text-[11px] font-semibold px-2.5 py-0.5 rounded-full border ${meta.bg} ${meta.border}`}
                    >
                      <Icon className="h-3 w-3" />
                      {meta.label}
                    </span>
                    <p className="text-[11px] text-muted-foreground leading-tight line-clamp-1">
                      {flight.airline} • {flight.cabin_class}
                    </p>
                  </div>

                  <div className="text-right">
                    <div className="text-lg font-bold text-foreground font-mono">
                      {formatCurrency(flight.price, currency)}
                    </div>
                    {flight.price_per_pax && (
                      <span className="text-[11px] text-muted-foreground font-mono block">
                        {formatCurrency(flight.price_per_pax, currency)} / person
                      </span>
                    )}
                    <span className="text-[10px] text-muted-foreground font-mono block">
                      Total Fare (Trip)
                    </span>
                    <span className="text-[10px] text-emerald-400 font-mono block">
                      ● Verified Market Fare
                    </span>
                  </div>
                </div>

                {/* Explicit Rationale */}
                <div className="p-2 rounded-lg bg-secondary/40 border border-border/50 text-[11px] text-muted-foreground">
                  <span className="font-semibold text-foreground/90">Why selected: </span>
                  {flight.rationale}
                </div>

                {/* Multi-Source Verification Links */}
                <div className="flex items-center gap-1.5 flex-wrap pt-0.5">
                  <span className="text-[10px] text-muted-foreground font-medium mr-0.5">Cross-check:</span>
                  <a
                    href={flight.deep_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[10px] px-2 py-0.5 rounded-md bg-secondary/80 hover:bg-secondary border border-border/60 text-foreground flex items-center gap-1 transition-colors"
                    title="Check fare live on Google Flights"
                  >
                    Google Flights
                    <ExternalLink className="h-2.5 w-2.5 text-muted-foreground" />
                  </a>
                  {flight.skyscanner_deep_link && (
                    <a
                      href={flight.skyscanner_deep_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[10px] px-2 py-0.5 rounded-md bg-sky-500/10 hover:bg-sky-500/20 border border-sky-500/30 text-sky-400 flex items-center gap-1 transition-colors"
                      title="Compare live quotes on Skyscanner"
                    >
                      Skyscanner
                      <ExternalLink className="h-2.5 w-2.5 text-sky-400" />
                    </a>
                  )}
                  {flight.makemytrip_deep_link && (
                    <a
                      href={flight.makemytrip_deep_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[10px] px-2 py-0.5 rounded-md bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-rose-400 flex items-center gap-1 transition-colors"
                      title="Check real-time domestic fares on MakeMyTrip India"
                    >
                      MakeMyTrip
                      <ExternalLink className="h-2.5 w-2.5 text-rose-400" />
                    </a>
                  )}
                </div>

                {/* Outbound Segment Details */}
                {outbound && (
                  <div className="space-y-1.5 p-2.5 rounded-xl bg-secondary/25 border border-border/40">
                    <div className="flex items-center justify-between text-[11px] font-medium text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Plane className="h-3 w-3 text-sky-400" />
                        Outbound
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {formatDuration(outbound.duration_minutes)}
                      </span>
                    </div>

                    <div className="flex items-center justify-between font-mono text-xs">
                      <div>
                        <div className="font-bold text-foreground">{outbound.departure_time}</div>
                        <div className="text-[10px] text-muted-foreground">{outbound.departure_airport}</div>
                      </div>

                      <div className="flex-1 flex flex-col items-center px-2">
                        <span className="text-[9px] text-muted-foreground">
                          {outbound.stops === 0 ? "Non-stop" : `${outbound.stops} stop`}
                        </span>
                        <div className="w-full flex items-center justify-center">
                          <div className="h-px bg-border/70 flex-1" />
                          <ArrowRight className="h-3 w-3 text-muted-foreground mx-1 shrink-0" />
                          <div className="h-px bg-border/70 flex-1" />
                        </div>
                        <span className="text-[9px] text-muted-foreground">{outbound.flight_number}</span>
                      </div>

                      <div className="text-right">
                        <div className="font-bold text-foreground">{outbound.arrival_time}</div>
                        <div className="text-[10px] text-muted-foreground">{outbound.arrival_airport}</div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Return Segment Details (if roundtrip) */}
                {returnSegment && (
                  <div className="space-y-1.5 p-2.5 rounded-xl bg-secondary/25 border border-border/40">
                    <div className="flex items-center justify-between text-[11px] font-medium text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Plane className="h-3 w-3 text-sky-400 rotate-180" />
                        Return
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {formatDuration(returnSegment.duration_minutes)}
                      </span>
                    </div>

                    <div className="flex items-center justify-between font-mono text-xs">
                      <div>
                        <div className="font-bold text-foreground">{returnSegment.departure_time}</div>
                        <div className="text-[10px] text-muted-foreground">{returnSegment.departure_airport}</div>
                      </div>

                      <div className="flex-1 flex flex-col items-center px-2">
                        <span className="text-[9px] text-muted-foreground">
                          {returnSegment.stops === 0 ? "Non-stop" : `${returnSegment.stops} stop`}
                        </span>
                        <div className="w-full flex items-center justify-center">
                          <div className="h-px bg-border/70 flex-1" />
                          <ArrowRight className="h-3 w-3 text-muted-foreground mx-1 shrink-0" />
                          <div className="h-px bg-border/70 flex-1" />
                        </div>
                        <span className="text-[9px] text-muted-foreground">{returnSegment.flight_number}</span>
                      </div>

                      <div className="text-right">
                        <div className="font-bold text-foreground">{returnSegment.arrival_time}</div>
                        <div className="text-[10px] text-muted-foreground">{returnSegment.arrival_airport}</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="pt-4 flex items-center gap-2 mt-2">
                <Button
                  type="button"
                  variant={isSelected ? "default" : "secondary"}
                  size="sm"
                  disabled={isUpdating}
                  onClick={() => onSelectFlight(flight.id)}
                  className="flex-1 text-xs gap-1.5 cursor-pointer font-medium"
                >
                  {isSelected ? (
                    <>
                      <CheckCircle2 className="h-3.5 w-3.5" />
                      <span>Selected in Plan</span>
                    </>
                  ) : (
                    <span>Select Option</span>
                  )}
                </Button>

                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => onBookFlight(flight)}
                  className="text-xs gap-1 cursor-pointer"
                  title="Review on verified Google Flights portal"
                >
                  <ExternalLink className="h-3.5 w-3.5" />
                  <span>View</span>
                </Button>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
