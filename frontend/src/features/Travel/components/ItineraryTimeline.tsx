/**
 * Lisa AIOS — Multi-Day Itinerary Timeline
 * Interactive day tabs, morning/afternoon/evening slots, meal recommendations & travel tips.
 */

import { useState } from "react"
import {
  Calendar,
  Sun,
  Sunset,
  Moon,
  Clock,
  MapPin,
  Utensils,
  Lightbulb,
  Ticket,
} from "lucide-react"
import type { Itinerary, ActivityItem } from "../types"
import { formatCurrency } from "../types"

interface ItineraryTimelineProps {
  itinerary: Itinerary
  currency: string
}

export function ItineraryTimeline({
  itinerary,
  currency,
}: ItineraryTimelineProps) {
  const [selectedDayIdx, setSelectedDayIdx] = useState(0)

  if (!itinerary || !itinerary.days || itinerary.days.length === 0) {
    return (
      <div className="p-6 rounded-2xl border border-dashed border-border/80 text-center text-xs text-muted-foreground">
        No itinerary days generated.
      </div>
    )
  }

  const currentDay = itinerary.days[selectedDayIdx] || itinerary.days[0]

  const getSlotIcon = (slot: string) => {
    switch (slot) {
      case "morning":
        return Sun
      case "afternoon":
        return Sunset
      case "evening":
      default:
        return Moon
    }
  }

  const getSlotColor = (slot: string) => {
    switch (slot) {
      case "morning":
        return "text-amber-400 bg-amber-500/10 border-amber-500/20"
      case "afternoon":
        return "text-orange-400 bg-orange-500/10 border-orange-500/20"
      case "evening":
      default:
        return "text-indigo-400 bg-indigo-500/10 border-indigo-500/20"
    }
  }

  return (
    <div className="space-y-4">
      {/* Header & Pace Indicator */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-primary/10 text-primary border border-primary/20">
              <Calendar className="h-4 w-4" />
            </span>
            <h3 className="text-base font-semibold text-foreground">
              {itinerary.total_days}-Day Curated Schedule
            </h3>
          </div>
          <p className="text-xs text-muted-foreground mt-0.5">
            Balanced time allocation with dedicated morning, afternoon, and evening exploration.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs self-start sm:self-auto">
          <span className="px-2.5 py-1 rounded-lg bg-secondary/60 text-muted-foreground border border-border/60 capitalize font-medium">
            Pace: {itinerary.pace}
          </span>
          <span className="font-mono text-muted-foreground bg-secondary/40 px-2.5 py-1 rounded-lg border border-border/60">
            Est. Day Spend:{" "}
            <strong className="text-foreground">
              {formatCurrency(currentDay.estimated_daily_spend, currency)}
            </strong>
          </span>
        </div>
      </div>

      {/* Day Selector Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-none">
        {itinerary.days.map((day, idx) => {
          const isActive = idx === selectedDayIdx
          return (
            <button
              key={day.day_number}
              type="button"
              onClick={() => setSelectedDayIdx(idx)}
              className={`px-4 py-2 rounded-xl text-xs font-medium whitespace-nowrap transition-all cursor-pointer flex items-center gap-2 border ${
                isActive
                  ? "bg-primary text-primary-foreground border-primary shadow-xs"
                  : "bg-secondary/40 text-muted-foreground hover:text-foreground hover:bg-secondary border-border/60"
              }`}
            >
              <span>Day {day.day_number}</span>
              <span className="text-[10px] opacity-80 line-clamp-1 max-w-30">
                {day.theme}
              </span>
            </button>
          )
        })}
      </div>

      {/* Day Header */}
      <div className="p-4 rounded-xl bg-card/60 border border-border/60 flex items-center justify-between">
        <div>
          <span className="text-[11px] font-mono text-primary uppercase font-bold tracking-wider">
            Day {currentDay.day_number} Focus
          </span>
          <h4 className="text-sm font-semibold text-foreground mt-0.5">
            {currentDay.theme}
          </h4>
        </div>
        {currentDay.date && (
          <span className="text-xs font-mono text-muted-foreground">
            {currentDay.date}
          </span>
        )}
      </div>

      {/* Structured Time Slots */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
        {currentDay.activities.map((activity: ActivityItem, idx: number) => {
          const Icon = getSlotIcon(activity.time_slot)
          const colorClass = getSlotColor(activity.time_slot)

          return (
            <div
              key={idx}
              className="rounded-2xl border border-border/70 bg-card/70 backdrop-blur-xs p-4 flex flex-col justify-between space-y-3 hover:border-border transition-all shadow-xs"
            >
              <div className="space-y-2.5">
                {/* Slot Tag & Duration */}
                <div className="flex items-center justify-between">
                  <span
                    className={`inline-flex items-center gap-1.5 text-[11px] font-semibold px-2.5 py-0.5 rounded-full border capitalize ${colorClass}`}
                  >
                    <Icon className="h-3 w-3" />
                    {activity.time_slot}
                  </span>

                  <span className="text-[11px] font-mono text-muted-foreground flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {activity.duration_mins} min
                  </span>
                </div>

                {/* Title & Description */}
                <div>
                  <h5 className="text-sm font-semibold text-foreground leading-snug">
                    {activity.title}
                  </h5>
                  <p className="text-xs text-muted-foreground mt-1 leading-relaxed">
                    {activity.description}
                  </p>
                </div>

                {/* Location */}
                <div className="text-[11px] text-muted-foreground flex items-center gap-1.5 pt-1">
                  <MapPin className="h-3.5 w-3.5 text-primary shrink-0" />
                  <span className="line-clamp-1">{activity.location}</span>
                </div>
              </div>

              {/* Footer Meta: Cost & Booking */}
              <div className="pt-2 border-t border-border/40 flex items-center justify-between text-xs font-mono">
                <span className="text-muted-foreground">
                  {activity.estimated_cost === 0
                    ? "Free entry"
                    : formatCurrency(activity.estimated_cost, currency)}
                </span>

                {activity.booking_required ? (
                  <span className="inline-flex items-center gap-1 text-[10px] text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-md border border-amber-500/20">
                    <Ticket className="h-3 w-3" />
                    Reservation Recommended
                  </span>
                ) : (
                  <span className="text-[10px] text-muted-foreground">
                    Walk-in welcome
                  </span>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Meal Suggestions for the Day */}
      {currentDay.meal_suggestions && currentDay.meal_suggestions.length > 0 && (
        <div className="p-3.5 rounded-xl bg-secondary/30 border border-border/50 flex flex-col sm:flex-row sm:items-center gap-2">
          <div className="flex items-center gap-2 text-xs font-semibold text-foreground shrink-0">
            <Utensils className="h-3.5 w-3.5 text-primary" />
            <span>Recommended Dining:</span>
          </div>
          <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
            {currentDay.meal_suggestions.map((meal: string, idx: number) => (
              <span
                key={idx}
                className="px-2.5 py-0.5 rounded-md bg-secondary/60 border border-border/40 text-[11px]"
              >
                {meal}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Destination Travel Tips Banner */}
      {itinerary.travel_tips && itinerary.travel_tips.length > 0 && (
        <div className="p-4 rounded-xl bg-primary/5 border border-primary/20 space-y-2">
          <div className="flex items-center gap-2 text-xs font-semibold text-primary">
            <Lightbulb className="h-4 w-4" />
            <span>Destination Insights & Travel Tips</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-muted-foreground">
            {itinerary.travel_tips.map((tip: string, idx: number) => (
              <div key={idx} className="flex items-start gap-2">
                <span className="text-primary font-bold">•</span>
                <span className="leading-relaxed">{tip}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
