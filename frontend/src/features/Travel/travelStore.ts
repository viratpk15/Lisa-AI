/**
 * Lisa AIOS — Travel Planner Global State Store
 * Persists active travel plan, tabs, and background generation status across navigation.
 */

import { create } from "zustand"
import { persist } from "zustand/middleware"
import type { TravelPlan, TripRequest, NaturalLanguageTripRequest } from "./types"

export type ActiveTab = "overview" | "flights" | "hotels" | "itinerary" | "transit" | "budget"

interface TravelState {
  activePlan: TravelPlan | null
  activeTab: ActiveTab
  isPlanning: boolean
  loadingStepText?: string
  errorMessage: string | null
  lastRequest: TripRequest | NaturalLanguageTripRequest | null

  setActivePlan: (plan: TravelPlan | null) => void
  setActiveTab: (tab: ActiveTab) => void
  setIsPlanning: (isPlanning: boolean, stepText?: string) => void
  setErrorMessage: (msg: string | null) => void
  setLastRequest: (req: TripRequest | NaturalLanguageTripRequest | null) => void
  reset: () => void
}

export const useTravelStore = create<TravelState>()(
  persist(
    (set) => ({
      activePlan: null,
      activeTab: "overview",
      isPlanning: false,
      loadingStepText: undefined,
      errorMessage: null,
      lastRequest: null,

      setActivePlan: (plan) => set({ activePlan: plan, isPlanning: false, loadingStepText: undefined, errorMessage: null }),
      setActiveTab: (tab) => set({ activeTab: tab }),
      setIsPlanning: (isPlanning, stepText) => set({ isPlanning, loadingStepText: stepText }),
      setErrorMessage: (msg) => set({ errorMessage: msg, isPlanning: false, loadingStepText: undefined }),
      setLastRequest: (req) => set({ lastRequest: req }),
      reset: () => set({ activePlan: null, isPlanning: false, loadingStepText: undefined, errorMessage: null, activeTab: "overview" }),
    }),
    {
      name: "lisa_travel_store",
      partialize: (state) => ({
        activePlan: state.activePlan,
        activeTab: state.activeTab,
      }),
    }
  )
)
