/**
 * Lisa AIOS — Travel Planner Master Page
 * Production trip planning orchestrator combining NLP requests, verified flights/hotels,
 * multi-day schedule, transparent budget breakdown, and booking safety gates.
 */

import { useState } from "react"
import { motion } from "framer-motion"
import {
  Plane,
  Hotel,
  Calendar,
  DollarSign,
  Compass,
  Sparkles,
  Printer,
  RotateCcw,
  AlertCircle,
  MapPin,
  Users,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { TripInputSection } from "./components/TripInputSection"
import { FlightOptionsCard } from "./components/FlightOptionsCard"
import { HotelOptionsCard } from "./components/HotelOptionsCard"
import { TransportCard } from "./components/TransportCard"
import { ItineraryTimeline } from "./components/ItineraryTimeline"
import { BudgetSummaryCard } from "./components/BudgetSummaryCard"
import { RouteGuideCard } from "./components/RouteGuideCard"
import { BookingConfirmationModal } from "./components/BookingConfirmationModal"
import {
  useCreatePlanMutation,
  useParsePromptMutation,
  useSelectFlightMutation,
  useSelectHotelMutation,
} from "./queries"
import { useTravelStore, type ActiveTab } from "./travelStore"
import { formatCurrency } from "./types"
import type {
  TripRequest,
  NaturalLanguageTripRequest,
  FlightOption,
  HotelOption,
} from "./types"

export default function TravelPage() {
  const activePlan = useTravelStore((s) => s.activePlan)
  const activeTab = useTravelStore((s) => s.activeTab)
  const storeIsPlanning = useTravelStore((s) => s.isPlanning)
  const loadingStepText = useTravelStore((s) => s.loadingStepText)
  const errorMessage = useTravelStore((s) => s.errorMessage)
  const setActivePlan = useTravelStore((s) => s.setActivePlan)
  const setActiveTab = useTravelStore((s) => s.setActiveTab)
  const setIsPlanning = useTravelStore((s) => s.setIsPlanning)
  const setErrorMessage = useTravelStore((s) => s.setErrorMessage)
  const resetTravel = useTravelStore((s) => s.reset)

  // Booking modal state
  const [bookingModalOpen, setBookingModalOpen] = useState(false)
  const [targetBookingItem, setTargetBookingItem] = useState<{
    itemType: "flight" | "hotel" | "activity" | "transport"
    itemId: string
    title: string
    providerName: string
    priceText?: string
    deepLink?: string
  } | null>(null)

  // API mutations
  const parsePromptMutation = useParsePromptMutation()
  const createPlanMutation = useCreatePlanMutation()
  const selectFlightMutation = useSelectFlightMutation()
  const selectHotelMutation = useSelectHotelMutation()

  const isPlanning = storeIsPlanning || parsePromptMutation.isPending || createPlanMutation.isPending
  const isUpdatingSelection = selectFlightMutation.isPending || selectHotelMutation.isPending

  // Handle Natural Language submission
  const handleNaturalLanguageSubmit = async (req: NaturalLanguageTripRequest) => {
    setErrorMessage(null)
    setIsPlanning(true, "Lisa is understanding your trip requirements and destination preferences...")

    try {
      // Step 1: Parse requirements
      const structuredReq = await parsePromptMutation.mutateAsync(req)

      // Step 2: Generate plan
      setIsPlanning(true, `Synthesizing flights to ${structuredReq.destination}, discovering stays, and compiling itinerary...`)
      const plan = await createPlanMutation.mutateAsync(structuredReq)
      setActivePlan(plan)
      setActiveTab("overview")
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to generate travel plan"
      setErrorMessage(msg)
    }
  }

  // Handle Structured Form submission
  const handleStructuredSubmit = async (req: TripRequest) => {
    setErrorMessage(null)
    setIsPlanning(true, `Searching flight routes to ${req.destination}, discovering accommodations, and budgeting...`)

    try {
      const plan = await createPlanMutation.mutateAsync(req)
      setActivePlan(plan)
      setActiveTab("overview")
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to generate travel plan"
      setErrorMessage(msg)
    }
  }

  // Handle Flight selection
  const handleSelectFlight = async (flightId: string) => {
    if (!activePlan) return
    try {
      const updatedPlan = await selectFlightMutation.mutateAsync({
        tripId: activePlan.trip_id,
        flightId,
      })
      setActivePlan(updatedPlan)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to update flight selection"
      setErrorMessage(msg)
    }
  }

  // Handle Hotel selection
  const handleSelectHotel = async (hotelId: string) => {
    if (!activePlan) return
    try {
      const updatedPlan = await selectHotelMutation.mutateAsync({
        tripId: activePlan.trip_id,
        hotelId,
      })
      setActivePlan(updatedPlan)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to update hotel selection"
      setErrorMessage(msg)
    }
  }

  // Handle Book Flight (Safety gate)
  const handleBookFlight = (flight: FlightOption) => {
    setTargetBookingItem({
      itemType: "flight",
      itemId: flight.id,
      title: `${flight.airline} (${flight.outbound_segments[0]?.departure_airport} → ${flight.outbound_segments[0]?.arrival_airport})`,
      providerName: flight.provider || "Google Flights",
      priceText: formatCurrency(flight.price, flight.currency || currency),
      deepLink: flight.deep_link,
    })
    setBookingModalOpen(true)
  }

  // Handle Book Hotel (Safety gate)
  const handleBookHotel = (hotel: HotelOption) => {
    setTargetBookingItem({
      itemType: "hotel",
      itemId: hotel.id,
      title: `${hotel.name} (${hotel.location})`,
      providerName: "Booking.com",
      priceText: formatCurrency(hotel.total_price, hotel.currency || currency),
      deepLink: hotel.booking_url,
    })
    setBookingModalOpen(true)
  }

  // Print / PDF Export
  const handlePrint = () => {
    window.print()
  }

  const currency = activePlan?.request.currency || "USD"
  const nights = activePlan?.itinerary.total_days ? Math.max(1, activePlan.itinerary.total_days - 1) : 1

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="max-w-6xl mx-auto space-y-6 py-2 px-2 sm:px-4 print:p-0 print:m-0"
    >
      {/* 1. Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-border/60 print:hidden">
        <div className="space-y-1">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-primary/10 text-primary border border-primary/20">
              <Plane className="h-5 w-5" />
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-foreground">
              Travel Planner
            </h1>
          </div>
          <p className="text-xs text-muted-foreground">
            Curated multi-day itineraries, flight & hotel comparisons, and transparent budget intelligence.
          </p>
        </div>

        {activePlan && (
          <div className="flex items-center gap-2 self-start sm:self-auto">
            <Button
              variant="outline"
              size="sm"
              onClick={handlePrint}
              className="text-xs gap-1.5 cursor-pointer"
            >
              <Printer className="h-3.5 w-3.5" />
              <span>Export Itinerary</span>
            </Button>

            <Button
              variant="ghost"
              size="sm"
              onClick={() => resetTravel()}
              className="text-xs gap-1.5 text-muted-foreground hover:text-foreground cursor-pointer"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              <span>New Search</span>
            </Button>
          </div>
        )}
      </div>

      {/* 2. Error Message Banner */}
      {errorMessage && (
        <div className="p-4 rounded-xl bg-destructive/10 border border-destructive/25 text-destructive flex items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{errorMessage}</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setErrorMessage(null)}
            className="text-xs h-7 px-2 cursor-pointer"
          >
            Dismiss
          </Button>
        </div>
      )}

      {/* 3. Input Section (Only show if no active plan or when in print mode) */}
      {!activePlan ? (
        <TripInputSection
          isLoading={isPlanning}
          loadingStepText={loadingStepText}
          onSubmitNaturalLanguage={handleNaturalLanguageSubmit}
          onSubmitStructured={handleStructuredSubmit}
        />
      ) : (
        /* 4. Active Trip Plan Display */
        <div className="space-y-6">
          {/* Trip Header Card */}
          <div className="rounded-2xl border border-border/70 bg-card/70 backdrop-blur-md p-5 shadow-xs space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
              <div className="space-y-1">
                <span className="text-[11px] font-mono text-primary uppercase font-bold tracking-wider">
                  Confirmed Itinerary Spec
                </span>
                <h2 className="text-xl font-bold text-foreground">
                  {activePlan.title}
                </h2>
                <p className="text-xs text-muted-foreground leading-relaxed max-w-2xl">
                  {activePlan.summary}
                </p>
              </div>

              <div className="text-right shrink-0">
                <div className="text-xs text-muted-foreground font-mono">Projected Total</div>
                <div className="text-2xl font-bold font-mono text-foreground">
                  {formatCurrency(activePlan.budget.total_projected, currency)}
                </div>
                <div className="text-[11px] text-emerald-400 font-mono">
                  {formatCurrency(activePlan.budget.total_verified, currency)} verified fares
                </div>
              </div>
            </div>

            {/* Trip Specs Bar */}
            <div className="flex flex-wrap items-center gap-2 sm:gap-4 pt-2 border-t border-border/40 text-xs text-muted-foreground font-mono">
              <span className="flex items-center gap-1.5">
                <MapPin className="h-3.5 w-3.5 text-primary" />
                {activePlan.request.origin} → {activePlan.request.destination}
              </span>
              <span>•</span>
              <span className="flex items-center gap-1.5">
                <Calendar className="h-3.5 w-3.5 text-primary" />
                {activePlan.request.departure_date}
                {activePlan.request.return_date ? ` to ${activePlan.request.return_date}` : ""}
              </span>
              <span>•</span>
              <span className="flex items-center gap-1.5">
                <Users className="h-3.5 w-3.5 text-primary" />
                {activePlan.request.travellers} traveller{activePlan.request.travellers > 1 ? "s" : ""}
              </span>
              <span>•</span>
              <span className="capitalize">{activePlan.request.cabin_class || "Economy"}</span>
            </div>
          </div>

          {/* Navigation Tabs (Overview, Itinerary, Flights, Hotels, Transit, Budget) */}
          <div className="flex gap-1.5 overflow-x-auto border-b border-border/60 pb-2 scrollbar-none print:hidden">
            {[
              { id: "overview", label: "Complete Travel Plan", icon: Sparkles },
              { id: "itinerary", label: "Day Schedule", icon: Calendar },
              { id: "flights", label: "Flights & Fares", icon: Plane },
              { id: "hotels", label: "Hotels & Stays", icon: Hotel },
              { id: "transit", label: "Transit & Readiness", icon: Compass },
              { id: "budget", label: "Financial Budget", icon: DollarSign },
            ].map((tab) => {
              const Icon = tab.icon
              const isActive = activeTab === tab.id
              return (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setActiveTab(tab.id as ActiveTab)}
                  className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-medium whitespace-nowrap transition-all cursor-pointer ${
                    isActive
                      ? "bg-secondary text-foreground border border-border shadow-xs"
                      : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
                  }`}
                >
                  <Icon className="h-3.5 w-3.5" />
                  <span>{tab.label}</span>
                </button>
              )
            })}
          </div>

          {/* Tab Views */}
          <div className="space-y-8">
            {/* View: Overview (Complete Integrated Plan — Day Schedule First) */}
            {activeTab === "overview" && (
              <div className="space-y-8">
                {/* 1. Multi-day Curated Itinerary (Traveler's Master Plan First) */}
                <ItineraryTimeline
                  itinerary={activePlan.itinerary}
                  currency={currency}
                />

                {/* 2. Destination Readiness & Route Guide */}
                <RouteGuideCard
                  routeGuide={activePlan.route_guide}
                  destination={activePlan.request.destination}
                />

                {/* 3. Recommended Flights & Fares */}
                <FlightOptionsCard
                  flights={activePlan.flight_options}
                  selectedFlightId={activePlan.selected_flight?.id}
                  currency={currency}
                  onSelectFlight={handleSelectFlight}
                  onBookFlight={handleBookFlight}
                  isUpdating={isUpdatingSelection}
                />

                {/* 4. Curated Hotels & Stays */}
                <HotelOptionsCard
                  hotels={activePlan.hotel_options}
                  selectedHotelId={activePlan.selected_hotel?.id}
                  currency={currency}
                  totalNights={nights}
                  onSelectHotel={handleSelectHotel}
                  onBookHotel={handleBookHotel}
                  isUpdating={isUpdatingSelection}
                />

                {/* 5. Local Transit */}
                <TransportCard
                  routeGuide={activePlan.route_guide}
                  currency={currency}
                />

                {/* 6. Budget Breakdown */}
                <BudgetSummaryCard
                  budget={activePlan.budget}
                  currency={currency}
                />
              </div>
            )}

            {/* View: Flights */}
            {activeTab === "flights" && (
              <FlightOptionsCard
                flights={activePlan.flight_options}
                selectedFlightId={activePlan.selected_flight?.id}
                currency={currency}
                onSelectFlight={handleSelectFlight}
                onBookFlight={handleBookFlight}
                isUpdating={isUpdatingSelection}
              />
            )}

            {/* View: Hotels */}
            {activeTab === "hotels" && (
              <HotelOptionsCard
                hotels={activePlan.hotel_options}
                selectedHotelId={activePlan.selected_hotel?.id}
                currency={currency}
                totalNights={nights}
                onSelectHotel={handleSelectHotel}
                onBookHotel={handleBookHotel}
                isUpdating={isUpdatingSelection}
              />
            )}

            {/* View: Itinerary */}
            {activeTab === "itinerary" && (
              <ItineraryTimeline
                itinerary={activePlan.itinerary}
                currency={currency}
              />
            )}

            {/* View: Transit & Guide */}
            {activeTab === "transit" && (
              <div className="space-y-6">
                <TransportCard
                  routeGuide={activePlan.route_guide}
                  currency={currency}
                />
                <RouteGuideCard
                  routeGuide={activePlan.route_guide}
                  destination={activePlan.request.destination}
                />
              </div>
            )}

            {/* View: Budget */}
            {activeTab === "budget" && (
              <BudgetSummaryCard
                budget={activePlan.budget}
                currency={currency}
              />
            )}
          </div>
        </div>
      )}

      {/* Safety Gate Confirmation Modal */}
      <BookingConfirmationModal
        isOpen={bookingModalOpen}
        onClose={() => setBookingModalOpen(false)}
        tripId={activePlan?.trip_id || "trip"}
        item={targetBookingItem}
      />
    </motion.div>
  )
}
