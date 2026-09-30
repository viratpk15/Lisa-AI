/**
 * Lisa AIOS — Travel Planner React Query Hooks
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import {
  parseTravelPromptApi,
  createTravelPlanApi,
  getTravelPlanApi,
  searchFlightsApi,
  searchHotelsApi,
  generateItineraryApi,
  selectFlightApi,
  selectHotelApi,
  prepareBookingApi,
} from "./api"
import type {
  TripRequest,
  NaturalLanguageTripRequest,
  TravelPlan,
  FlightSearchResponse,
  HotelSearchResponse,
  Itinerary,
  BookingActionRequest,
  BookingActionResponse,
} from "./types"

export const travelQueryKeys = {
  all: () => ["travel"] as const,
  plan: (tripId: string) => [...travelQueryKeys.all(), "plan", tripId] as const,
  flights: (req: TripRequest) => [...travelQueryKeys.all(), "flights", req.origin, req.destination, req.departure_date] as const,
  hotels: (req: TripRequest) => [...travelQueryKeys.all(), "hotels", req.destination, req.departure_date] as const,
}

export function useTravelPlanQuery(tripId: string | null) {
  return useQuery<TravelPlan>({
    queryKey: travelQueryKeys.plan(tripId ?? ""),
    queryFn: () => getTravelPlanApi(tripId!),
    enabled: Boolean(tripId),
    staleTime: 60_000,
  })
}

export function useParsePromptMutation() {
  return useMutation<TripRequest, Error, NaturalLanguageTripRequest>({
    mutationFn: parseTravelPromptApi,
  })
}

export function useCreatePlanMutation() {
  const queryClient = useQueryClient()
  return useMutation<TravelPlan, Error, TripRequest>({
    mutationFn: createTravelPlanApi,
    onSuccess: (data) => {
      queryClient.setQueryData(travelQueryKeys.plan(data.trip_id), data)
    },
  })
}

export function useSearchFlightsMutation() {
  return useMutation<FlightSearchResponse, Error, TripRequest>({
    mutationFn: searchFlightsApi,
  })
}

export function useSearchHotelsMutation() {
  return useMutation<HotelSearchResponse, Error, TripRequest>({
    mutationFn: searchHotelsApi,
  })
}

export function useGenerateItineraryMutation() {
  return useMutation<Itinerary, Error, TripRequest>({
    mutationFn: generateItineraryApi,
  })
}

export function useSelectFlightMutation() {
  const queryClient = useQueryClient()
  return useMutation<TravelPlan, Error, { tripId: string; flightId: string }>({
    mutationFn: ({ tripId, flightId }) => selectFlightApi(tripId, flightId),
    onSuccess: (data) => {
      queryClient.setQueryData(travelQueryKeys.plan(data.trip_id), data)
    },
  })
}

export function useSelectHotelMutation() {
  const queryClient = useQueryClient()
  return useMutation<TravelPlan, Error, { tripId: string; hotelId: string }>({
    mutationFn: ({ tripId, hotelId }) => selectHotelApi(tripId, hotelId),
    onSuccess: (data) => {
      queryClient.setQueryData(travelQueryKeys.plan(data.trip_id), data)
    },
  })
}

export function usePrepareBookingMutation() {
  return useMutation<BookingActionResponse, Error, BookingActionRequest>({
    mutationFn: prepareBookingApi,
  })
}
