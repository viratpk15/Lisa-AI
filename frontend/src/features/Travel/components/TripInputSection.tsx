/**
 * Lisa AIOS — Travel Planner Input Section
 * Dual-mode: Natural language prompt with prompt chips + expandable structured filters.
 */

import { useState } from "react"
import {
  Sparkles,
  SlidersHorizontal,
  ChevronDown,
  ChevronUp,
  MapPin,
  Calendar,
  Users,
  DollarSign,
  Plane,
  Loader2,
  ArrowRight,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import type { TripRequest, NaturalLanguageTripRequest } from "../types"

interface TripInputSectionProps {
  isLoading: boolean
  loadingStepText?: string
  onSubmitNaturalLanguage: (req: NaturalLanguageTripRequest) => void
  onSubmitStructured: (req: TripRequest) => void
}

const EXAMPLE_PROMPTS = [
  "5 days in Tokyo for 2 foodies under $3500 in May",
  "Weekend in Paris departing next Friday, central boutique hotel",
  "10-day cultural trip to Rome, Florence, & Venice for $4500",
  "Family trip to London for 4 with museum passes and metro guides",
]

export function TripInputSection({
  isLoading,
  loadingStepText,
  onSubmitNaturalLanguage,
  onSubmitStructured,
}: TripInputSectionProps) {
  const [nlQuery, setNlQuery] = useState("")
  const [showFilters, setShowFilters] = useState(false)

  // Structured form state
  const [origin, setOrigin] = useState("SFO")
  const [destination, setDestination] = useState("Tokyo, Japan")
  const [departureDate, setDepartureDate] = useState(() => {
    const d = new Date()
    d.setDate(d.getDate() + 14)
    return d.toISOString().split("T")[0]
  })
  const [returnDate, setReturnDate] = useState(() => {
    const d = new Date()
    d.setDate(d.getDate() + 20)
    return d.toISOString().split("T")[0]
  })
  const [travellers, setTravellers] = useState(2)
  const [budget, setBudget] = useState<number | undefined>(25000)
  const [currency, setCurrency] = useState("INR")
  const [cabinClass, setCabinClass] = useState("economy")
  const [hotelPreference, setHotelPreference] = useState("central")
  const [travelStyle, setTravelStyle] = useState("balanced")

  const handleNlSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!nlQuery.trim() || isLoading) return
    onSubmitNaturalLanguage({ query: nlQuery.trim() })
  }

  const handleChipClick = (prompt: string) => {
    setNlQuery(prompt)
    if (!isLoading) {
      onSubmitNaturalLanguage({ query: prompt })
    }
  }

  const handleStructuredSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!destination.trim() || isLoading) return
    onSubmitStructured({
      origin: origin.trim() || "BLR",
      destination: destination.trim(),
      departure_date: departureDate,
      return_date: returnDate || null,
      travellers: Number(travellers) || 1,
      budget: budget ? Number(budget) : null,
      currency,
      cabin_class: cabinClass,
      hotel_preference: hotelPreference,
      travel_style: travelStyle,
      room_count: Math.ceil((Number(travellers) || 1) / 2),
    })
  }

  return (
    <div className="rounded-2xl border border-border/70 bg-card/60 backdrop-blur-md p-5 sm:p-6 shadow-xs space-y-4">
      {/* Top Banner & Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-1">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-primary/10 text-primary border border-primary/20">
              <Sparkles className="h-4 w-4" />
            </span>
            <h2 className="text-base font-semibold text-foreground">Plan Your Next Journey</h2>
          </div>
          <p className="text-xs text-muted-foreground mt-0.5">
            Describe your trip in natural language or customize precise flight, hotel, and pacing criteria.
          </p>
        </div>

        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => setShowFilters((prev) => !prev)}
          className="text-xs gap-1.5 self-start sm:self-auto cursor-pointer"
        >
          <SlidersHorizontal className="h-3.5 w-3.5" />
          <span>{showFilters ? "Simple Search" : "Detailed Filters"}</span>
          {showFilters ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
        </Button>
      </div>

      {/* Mode A: Natural Language Prompt Input */}
      {!showFilters ? (
        <div className="space-y-4">
          <form onSubmit={handleNlSubmit} className="relative flex flex-col rounded-xl border border-border/70 bg-secondary/40 focus-within:border-primary/50 focus-within:ring-1 focus-within:ring-primary/40 transition-all shadow-inner overflow-hidden">
            <textarea
              value={nlQuery}
              onChange={(e) => setNlQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && (e.metaKey || e.ctrlKey || !e.shiftKey)) {
                  e.preventDefault()
                  handleNlSubmit(e)
                }
              }}
              rows={4}
              placeholder="Describe your desired trip in detail...&#10;e.g. 5 days in Kasol from Bangalore departing next Friday for 2 people with scenic stays, local trekking, and budget under ₹25,000..."
              disabled={isLoading}
              className="w-full bg-transparent p-4 text-sm text-foreground placeholder:text-muted-foreground/60 outline-none resize-y min-h-27.5 font-sans"
            />
            <div className="flex items-center justify-between px-3 py-2 border-t border-border/40 bg-secondary/30">
              <span className="text-[11px] text-muted-foreground/70 hidden sm:inline">
                Tip: Press <kbd className="font-mono bg-background/60 px-1 py-0.5 rounded text-[10px] border border-border/40">Enter</kbd> or <kbd className="font-mono bg-background/60 px-1 py-0.5 rounded text-[10px] border border-border/40">⌘ Enter</kbd> to plan. <kbd className="font-mono bg-background/60 px-1 py-0.5 rounded text-[10px] border border-border/40">Shift+Enter</kbd> for new line.
              </span>
              <Button
                type="submit"
                disabled={!nlQuery.trim() || isLoading}
                className="ml-auto px-4 py-2 text-xs font-semibold gap-1.5 rounded-lg cursor-pointer"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    <span>Planning Trip...</span>
                  </>
                ) : (
                  <>
                    <span>Create Complete Travel Plan</span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </>
                )}
              </Button>
            </div>
          </form>

          {/* Prompt Chips */}
          <div className="space-y-1.5">
            <span className="text-[11px] font-medium text-muted-foreground/80 tracking-wide uppercase">
              Quick Suggestions:
            </span>
            <div className="flex flex-wrap gap-2">
              {EXAMPLE_PROMPTS.map((prompt, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleChipClick(prompt)}
                  disabled={isLoading}
                  className="text-xs px-3 py-1.5 rounded-lg border border-border/50 bg-secondary/30 hover:bg-secondary hover:border-primary/40 text-muted-foreground hover:text-foreground transition-all cursor-pointer text-left"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        </div>
      ) : (
        /* Mode B: Detailed Structured Filters */
        <form onSubmit={handleStructuredSubmit} className="space-y-4 pt-2">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
            {/* Origin */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                <Plane className="h-3.5 w-3.5 text-primary" />
                Origin Airport / City
              </label>
              <Input
                value={origin}
                onChange={(e) => setOrigin(e.target.value)}
                placeholder="e.g. SFO or San Francisco"
                className="h-9 text-xs bg-secondary/40"
                required
              />
            </div>

            {/* Destination */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                <MapPin className="h-3.5 w-3.5 text-primary" />
                Destination City
              </label>
              <Input
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                placeholder="e.g. Tokyo, Paris, Rome"
                className="h-9 text-xs bg-secondary/40"
                required
              />
            </div>

            {/* Departure Date */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                <Calendar className="h-3.5 w-3.5 text-primary" />
                Departure Date
              </label>
              <Input
                type="date"
                value={departureDate}
                onChange={(e) => setDepartureDate(e.target.value)}
                className="h-9 text-xs bg-secondary/40"
                required
              />
            </div>

            {/* Return Date */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                <Calendar className="h-3.5 w-3.5 text-primary" />
                Return Date
              </label>
              <Input
                type="date"
                value={returnDate}
                onChange={(e) => setReturnDate(e.target.value)}
                className="h-9 text-xs bg-secondary/40"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3">
            {/* Travellers */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                <Users className="h-3.5 w-3.5 text-primary" />
                Travellers
              </label>
              <Input
                type="number"
                min="1"
                max="16"
                value={travellers}
                onChange={(e) => setTravellers(Number(e.target.value))}
                className="h-9 text-xs bg-secondary/40"
              />
            </div>

            {/* Budget */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                <DollarSign className="h-3.5 w-3.5 text-primary" />
                Target Budget
              </label>
              <div className="flex gap-1.5">
                <Input
                  type="number"
                  placeholder="Optional"
                  value={budget ?? ""}
                  onChange={(e) => setBudget(e.target.value ? Number(e.target.value) : undefined)}
                  className="h-9 text-xs bg-secondary/40 flex-1"
                />
                <select
                  value={currency}
                  onChange={(e) => setCurrency(e.target.value)}
                  className="h-9 px-2 text-xs rounded-md bg-secondary/40 border border-border/70 text-foreground outline-none"
                >
                  <option value="INR">INR (₹)</option>
                  <option value="USD">USD ($)</option>
                  <option value="EUR">EUR (€)</option>
                  <option value="GBP">GBP (£)</option>
                  <option value="AED">AED</option>
                  <option value="AUD">AUD ($)</option>
                </select>
              </div>
            </div>

            {/* Cabin Class */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground">Cabin Class</label>
              <select
                value={cabinClass}
                onChange={(e) => setCabinClass(e.target.value)}
                className="w-full h-9 px-2 text-xs rounded-md bg-secondary/40 border border-border/70 text-foreground outline-none"
              >
                <option value="economy">Economy</option>
                <option value="premium_economy">Premium Economy</option>
                <option value="business">Business</option>
                <option value="first">First Class</option>
              </select>
            </div>

            {/* Hotel Preference */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground">Hotel Style</label>
              <select
                value={hotelPreference}
                onChange={(e) => setHotelPreference(e.target.value)}
                className="w-full h-9 px-2 text-xs rounded-md bg-secondary/40 border border-border/70 text-foreground outline-none"
              >
                <option value="central">Central & Convenient</option>
                <option value="boutique">Boutique & Aesthetic</option>
                <option value="luxury">Luxury 5-Star</option>
                <option value="budget">Value & Budget</option>
              </select>
            </div>

            {/* Pace */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground">Itinerary Pace</label>
              <select
                value={travelStyle}
                onChange={(e) => setTravelStyle(e.target.value)}
                className="w-full h-9 px-2 text-xs rounded-md bg-secondary/40 border border-border/70 text-foreground outline-none"
              >
                <option value="relaxed">Relaxed (1-2 stops/day)</option>
                <option value="balanced">Balanced (2-3 stops/day)</option>
                <option value="intense">Active / Packed</option>
              </select>
            </div>
          </div>

          <div className="flex justify-end pt-1">
            <Button
              type="submit"
              disabled={isLoading}
              className="gap-2 text-xs font-medium cursor-pointer"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  <span>Generating Itinerary...</span>
                </>
              ) : (
                <>
                  <span>Build Custom Trip Plan</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </>
              )}
            </Button>
          </div>
        </form>
      )}

      {/* Loading Step Indicator */}
      {isLoading && (
        <div className="flex items-center gap-3 p-3 rounded-xl bg-primary/10 border border-primary/20 text-primary text-xs animate-pulse">
          <Loader2 className="h-4 w-4 animate-spin shrink-0" />
          <span>
            {loadingStepText || "Lisa is synthesizing route connections, accommodations, and curated activities..."}
          </span>
        </div>
      )}
    </div>
  )
}
