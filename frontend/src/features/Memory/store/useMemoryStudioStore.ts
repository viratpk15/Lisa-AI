// frontend/src/features/Memory/store/useMemoryStudioStore.ts

import { create } from "zustand"
import type { MemoryTabType, MemoryTierFilterType } from "../types/memory.types"

interface MemoryStudioState {
  activeTab: MemoryTabType
  selectedSessionId: string
  selectedMemoryId: string | null
  tierFilter: MemoryTierFilterType
  
  // Recall Bench State
  recallQuery: string
  recallTopK: number
  recallAlpha: number
  isRecalling: boolean

  // Actions
  setActiveTab: (tab: MemoryTabType) => void
  setSelectedSessionId: (id: string) => void
  setSelectedMemoryId: (id: string | null) => void
  setTierFilter: (filter: MemoryTierFilterType) => void
  setRecallQuery: (q: string) => void
  setRecallTopK: (k: number) => void
  setRecallAlpha: (a: number) => void
  setIsRecalling: (v: boolean) => void
  resetStore: () => void
}

export const useMemoryStudioStore = create<MemoryStudioState>((set) => ({
  activeTab: "timeline",
  selectedSessionId: "default",
  selectedMemoryId: null,
  tierFilter: "all",

  recallQuery: "vector search latency",
  recallTopK: 5,
  recallAlpha: 0.5,
  isRecalling: false,

  setActiveTab: (tab) => set({ activeTab: tab }),
  setSelectedSessionId: (id) => set({ selectedSessionId: id }),
  setSelectedMemoryId: (id) => set({ selectedMemoryId: id }),
  setTierFilter: (filter) => set({ tierFilter: filter }),

  setRecallQuery: (recallQuery) => set({ recallQuery }),
  setRecallTopK: (recallTopK) => set({ recallTopK }),
  setRecallAlpha: (recallAlpha) => set({ recallAlpha }),
  setIsRecalling: (isRecalling) => set({ isRecalling }),

  resetStore: () =>
    set({
      activeTab: "timeline",
      selectedSessionId: "default",
      selectedMemoryId: null,
      tierFilter: "all",
      recallQuery: "vector search latency",
      recallTopK: 5,
      recallAlpha: 0.5,
      isRecalling: false,
    }),
}))
