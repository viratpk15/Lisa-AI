/**
 * Lisa AIOS — Travel Planner Types & Schemas
 */

export function formatCurrency(amount: number | null | undefined, currency: string = "INR"): string {
  if (amount == null || isNaN(amount)) return "—"
  const c = (currency || "INR").toUpperCase()
  let sym = "₹"
  if (c === "USD") sym = "$"
  else if (c === "EUR") sym = "€"
  else if (c === "GBP") sym = "£"
  else if (c === "AED") sym = "AED "
  else if (c === "INR") sym = "₹"
  else sym = `${currency} `
  return `${sym}${Math.round(amount).toLocaleString()}`
}

export interface TripRequest {
  origin: string
  destination: string
  departure_date: string
  return_date?: string | null
  travellers: number
  budget?: number | null
  currency: string
  cabin_class?: string
  hotel_preference?: string | null
  room_count?: number
  travel_style?: string | null
  activities?: string[]
  food_preferences?: string[]
  transport_preferences?: string[]
  accessibility_needs?: string | null
  raw_query?: string | null
}

export interface NaturalLanguageTripRequest {
  query: string
  current_date?: string | null
}

export interface FlightSegment {
  flight_number: string
  airline: string
  airline_code?: string
  departure_airport: string
  arrival_airport: string
  departure_time: string
  arrival_time: string
  duration_minutes: number
  stops: number
  baggage_info?: string | null
}

export interface FlightOption {
  id: string
  provider: string
  category: "cheapest" | "fastest" | "best_balance" | "standard"
  rationale: string
  price: number
  price_per_pax?: number | null
  currency: string
  duration_minutes: number
  stops: number
  airline: string
  outbound_segments: FlightSegment[]
  return_segments: FlightSegment[]
  deep_link: string
  skyscanner_deep_link?: string | null
  makemytrip_deep_link?: string | null
  is_verified: boolean
  cabin_class: string
}

export interface FlightSearchResponse {
  origin: string
  destination: string
  departure_date: string
  return_date?: string | null
  travellers: number
  flights: FlightOption[]
  has_live_gds: boolean
  disclaimer: string
}

export interface HotelOption {
  id: string
  name: string
  location: string
  address?: string | null
  star_rating: number
  user_rating: number
  reviews_count?: number | null
  price_per_night: number
  total_price: number
  currency: string
  distance_to_center_km?: number | null
  amenities: string[]
  cancellation_policy: string
  image_url?: string | null
  booking_url: string
  is_verified: boolean
  rationale: string
}

export interface HotelSearchResponse {
  destination: string
  check_in: string
  check_out: string
  total_nights: number
  guests: number
  rooms: number
  hotels: HotelOption[]
  has_live_inventory: boolean
  disclaimer: string
}

export interface TransportSegment {
  segment_id: string
  from_name: string
  to_name: string
  mode: "metro" | "taxi" | "ride_hail" | "bus" | "walking" | "ferry" | "train"
  estimated_duration_mins: number
  estimated_cost: number
  currency: string
  is_verified: boolean
  deep_link?: string | null
  provider_name?: string | null
  notes?: string | null
}

export interface RouteGuide {
  segments: TransportSegment[]
  total_estimated_cost: number
  currency: string
  preparation_items: string[]
}

export interface ActivityItem {
  time_slot: "morning" | "afternoon" | "evening"
  title: string
  description: string
  location: string
  duration_mins: number
  estimated_cost: number
  booking_required: boolean
  opening_hours?: string | null
  verified_status: string
  booking_link?: string | null
}

export interface DayPlan {
  day_number: number
  date?: string | null
  theme: string
  activities: ActivityItem[]
  meal_suggestions: string[]
  estimated_daily_spend: number
  daily_transport: TransportSegment[]
}

export interface Itinerary {
  destination: string
  total_days: number
  pace: "relaxed" | "balanced" | "intense"
  days: DayPlan[]
  travel_tips: string[]
}

export interface BudgetCategory {
  category: "Flights" | "Hotel" | "Local transport" | "Food" | "Activities" | "Other"
  verified_amount: number
  estimated_amount: number
  currency: string
  is_verified: boolean
  notes: string
}

export interface TripBudget {
  user_budget: number
  currency: string
  categories: BudgetCategory[]
  total_verified: number
  total_estimated: number
  total_projected: number
  remaining_balance: number
  status: "within_budget" | "exceeded" | "unspecified"
  disclaimer: string
}

export interface TravelPlan {
  trip_id: string
  title: string
  summary: string
  request: TripRequest
  flight_options: FlightOption[]
  selected_flight?: FlightOption | null
  hotel_options: HotelOption[]
  selected_hotel?: HotelOption | null
  route_guide: RouteGuide
  itinerary: Itinerary
  budget: TripBudget
  created_at: string
}

export interface BookingActionRequest {
  trip_id: string
  item_type: "flight" | "hotel" | "activity" | "transport"
  item_id: string
  user_confirmed: boolean
}

export interface BookingActionResponse {
  status: "prepared" | "confirmed_redirect" | "rejected"
  action_url?: string | null
  provider_name: string
  item_type: string
  message: string
  safety_notice: string
}
