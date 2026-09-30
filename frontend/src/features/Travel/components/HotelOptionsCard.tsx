/**
 * Lisa AIOS — Hotel Options Card
 * Curated accommodations with star ratings, user ratings, verified deep links & booking safety gate.
 */

import {
  Hotel,
  Star,
  MapPin,
  CheckCircle2,
  ExternalLink,
  ShieldCheck,
  Check,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import type { HotelOption } from "../types"
import { formatCurrency } from "../types"

interface HotelOptionsCardProps {
  hotels: HotelOption[]
  selectedHotelId?: string | null
  currency: string
  totalNights: number
  onSelectHotel: (hotelId: string) => void
  onBookHotel: (hotel: HotelOption) => void
  isUpdating?: boolean
}

export function HotelOptionsCard({
  hotels,
  selectedHotelId,
  currency,
  totalNights,
  onSelectHotel,
  onBookHotel,
  isUpdating,
}: HotelOptionsCardProps) {
  if (!hotels || hotels.length === 0) {
    return (
      <div className="p-6 rounded-2xl border border-dashed border-border/80 text-center text-xs text-muted-foreground">
        No hotel options available for this destination.
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Hotel className="h-4 w-4" />
            </span>
            <h3 className="text-base font-semibold text-foreground">Accommodations & Stays</h3>
          </div>
          <p className="text-xs text-muted-foreground mt-0.5">
            Curated stays matching location accessibility and verified guest reviews ({totalNights} nights).
          </p>
        </div>

        <div className="flex items-center gap-1.5 text-[11px] text-muted-foreground bg-secondary/40 px-2.5 py-1 rounded-lg border border-border/60 self-start sm:self-auto">
          <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
          <span>Verified Inventory (Booking.com)</span>
        </div>
      </div>

      {/* Grid of Hotels */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {hotels.map((hotel) => {
          const isSelected = selectedHotelId === hotel.id

          return (
            <div
              key={hotel.id}
              className={`rounded-2xl border transition-all flex flex-col justify-between p-4.5 bg-card/70 backdrop-blur-sm shadow-xs ${
                isSelected
                  ? "border-primary ring-1 ring-primary/40 bg-card/90"
                  : "border-border/70 hover:border-border"
              }`}
            >
              <div className="space-y-3">
                {/* Hotel Header & Rating */}
                <div className="flex items-start justify-between gap-2">
                  <div className="space-y-1">
                    <div className="flex items-center gap-1">
                      {Array.from({ length: hotel.star_rating }).map((_, i) => (
                        <Star key={i} className="h-3 w-3 fill-amber-400 text-amber-400" />
                      ))}
                    </div>
                    <h4 className="text-sm font-semibold text-foreground leading-snug line-clamp-1">
                      {hotel.name}
                    </h4>
                    <p className="text-[11px] text-muted-foreground flex items-center gap-1">
                      <MapPin className="h-3 w-3 shrink-0 text-primary" />
                      <span className="line-clamp-1">{hotel.location}</span>
                    </p>
                  </div>

                  <div className="text-right shrink-0">
                    <div className="inline-flex items-center gap-1 px-2 py-0.5 rounded-lg bg-primary/10 border border-primary/20 text-primary font-mono text-xs font-bold">
                      {hotel.user_rating.toFixed(1)}/10
                    </div>
                    {hotel.distance_to_center_km !== undefined && hotel.distance_to_center_km !== null && (
                      <div className="text-[10px] text-muted-foreground mt-0.5">
                        {hotel.distance_to_center_km} km to center
                      </div>
                    )}
                  </div>
                </div>

                {/* Price Breakdown */}
                <div className="p-2.5 rounded-xl bg-secondary/30 border border-border/50 flex items-center justify-between font-mono">
                  <div>
                    <div className="text-xs text-muted-foreground">Nightly</div>
                    <div className="text-sm font-bold text-foreground">
                      {formatCurrency(hotel.price_per_night, currency)}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-muted-foreground">Stay Total ({totalNights}n)</div>
                    <div className="text-sm font-bold text-emerald-400">
                      {formatCurrency(hotel.total_price, currency)}
                    </div>
                  </div>
                </div>

                {/* Rationale */}
                <div className="text-[11px] text-muted-foreground bg-secondary/20 p-2 rounded-lg border border-border/40">
                  <span className="font-semibold text-foreground/90">Why chosen: </span>
                  {hotel.rationale}
                </div>

                {/* Amenities Badges */}
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {hotel.amenities.slice(0, 4).map((amenity, idx) => (
                    <span
                      key={idx}
                      className="text-[10px] px-2 py-0.5 rounded-md bg-secondary/60 text-muted-foreground border border-border/40"
                    >
                      {amenity}
                    </span>
                  ))}
                </div>

                {/* Cancellation Policy */}
                <div className="text-[10px] text-emerald-400/90 flex items-center gap-1">
                  <Check className="h-3 w-3 shrink-0" />
                  <span>{hotel.cancellation_policy}</span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-4 flex items-center gap-2 mt-2">
                <Button
                  type="button"
                  variant={isSelected ? "default" : "secondary"}
                  size="sm"
                  disabled={isUpdating}
                  onClick={() => onSelectHotel(hotel.id)}
                  className="flex-1 text-xs gap-1.5 cursor-pointer font-medium"
                >
                  {isSelected ? (
                    <>
                      <CheckCircle2 className="h-3.5 w-3.5" />
                      <span>Selected in Plan</span>
                    </>
                  ) : (
                    <span>Select Stay</span>
                  )}
                </Button>

                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => onBookHotel(hotel)}
                  className="text-xs gap-1 cursor-pointer"
                  title="Review on verified Booking.com portal"
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
