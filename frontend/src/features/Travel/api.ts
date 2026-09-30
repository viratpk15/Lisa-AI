/**
 * Lisa AIOS — Travel Planner API Client
 */

import { apiClient } from "@/services/api/apiClient"
import type {
  TripRequest,
  NaturalLanguageTripRequest,
  FlightSearchResponse,
  HotelSearchResponse,
  Itinerary,
  TravelPlan,
  BookingActionRequest,
  BookingActionResponse,
} from "./types"

export async function parseTravelPromptApi(
  req: NaturalLanguageTripRequest
): Promise<TripRequest> {
  return apiClient.post<TripRequest>("/api/v1/travel/parse-prompt", req, {
    timeoutMs: 45000,
  })
}

export async function createTravelPlanApi(
  req: TripRequest
): Promise<TravelPlan> {
  return apiClient.post<TravelPlan>("/api/v1/travel/plan", req, {
    timeoutMs: 60000,
  })
}

export async function getTravelPlanApi(tripId: string): Promise<TravelPlan> {
  return apiClient.get<TravelPlan>(`/api/v1/travel/plan/${tripId}`)
}

export async function searchFlightsApi(
  req: TripRequest
): Promise<FlightSearchResponse> {
  return apiClient.post<FlightSearchResponse>("/api/v1/travel/flights/search", req, {
    timeoutMs: 30000,
  })
}

export async function searchHotelsApi(
  req: TripRequest
): Promise<HotelSearchResponse> {
  return apiClient.post<HotelSearchResponse>("/api/v1/travel/hotels/search", req, {
    timeoutMs: 30000,
  })
}

export async function generateItineraryApi(
  req: TripRequest
): Promise<Itinerary> {
  return apiClient.post<Itinerary>("/api/v1/travel/itinerary/generate", req, {
    timeoutMs: 45000,
  })
}

export async function selectFlightApi(
  tripId: string,
  flightId: string
): Promise<TravelPlan> {
  return apiClient.post<TravelPlan>(`/api/v1/travel/plan/${tripId}/select-flight`, {
    flight_id: flightId,
  })
}

export async function selectHotelApi(
  tripId: string,
  hotelId: string
): Promise<TravelPlan> {
  return apiClient.post<TravelPlan>(`/api/v1/travel/plan/${tripId}/select-hotel`, {
    hotel_id: hotelId,
  })
}

export async function prepareBookingApi(
  req: BookingActionRequest
): Promise<BookingActionResponse> {
  return apiClient.post<BookingActionResponse>("/api/v1/travel/booking/prepare", req)
}
