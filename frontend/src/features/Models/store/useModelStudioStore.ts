// frontend/src/features/Models/store/useModelStudioStore.ts

import { create } from "zustand"
import type { ModelTabType } from "../types/models.types"

interface ModelStudioState {
  activeTab: ModelTabType
  setActiveTab: (tab: ModelTabType) => void

  selectedModelId: string
  setSelectedModelId: (modelId: string) => void

  benchmarkPromptTokens: number
  setBenchmarkPromptTokens: (tokens: number) => void
  benchmarkCompletionTokens: number
  setBenchmarkCompletionTokens: (tokens: number) => void

  costPromptTokens: number
  setCostPromptTokens: (tokens: number) => void
  costCompletionTokens: number
  setCostCompletionTokens: (tokens: number) => void
  costMonthlyRequests: number
  setCostMonthlyRequests: (reqs: number) => void
}

export const useModelStudioStore = create<ModelStudioState>((set) => ({
  activeTab: "registry",
  setActiveTab: (tab) => set({ activeTab: tab }),

  selectedModelId: "gemini-2.5-flash",
  setSelectedModelId: (modelId) => set({ selectedModelId: modelId }),

  benchmarkPromptTokens: 100,
  setBenchmarkPromptTokens: (tokens) => set({ benchmarkPromptTokens: tokens }),
  benchmarkCompletionTokens: 500,
  setBenchmarkCompletionTokens: (tokens) => set({ benchmarkCompletionTokens: tokens }),

  costPromptTokens: 1000,
  setCostPromptTokens: (tokens) => set({ costPromptTokens: tokens }),
  costCompletionTokens: 500,
  setCostCompletionTokens: (tokens) => set({ costCompletionTokens: tokens }),
  costMonthlyRequests: 10000,
  setCostMonthlyRequests: (reqs) => set({ costMonthlyRequests: reqs }),
}))
