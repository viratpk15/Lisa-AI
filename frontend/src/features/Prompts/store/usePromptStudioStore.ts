import { create } from "zustand"
import type { PromptExecution } from "../types/prompts.types"

export type PromptTab = "editor" | "playground" | "compare" | "versions" | "eval" | "analytics" | "templates"

interface PromptStudioState {
  selectedPromptId: string | null
  activeTab: PromptTab
  searchQuery: string
  selectedFolderId: string | null
  selectedTag: string | null

  // Draft Editor State
  systemPromptDraft: string
  userPromptDraft: string
  parsedVariables: Record<string, string>
  isDirty: boolean

  // Playground Config State
  selectedModels: string[]
  temperature: number
  topP: number
  maxTokens: number
  isExecuting: boolean
  isStreaming: boolean
  streamOutput: string

  // Execution History & Benchmark Results
  latestExecutions: PromptExecution[]
  comparisonResults: PromptExecution[]
  aiAssistModalOpen: boolean

  // Actions
  setSelectedPromptId: (id: string | null) => void
  setActiveTab: (tab: PromptTab) => void
  setSearchQuery: (q: string) => void
  setSelectedFolderId: (folderId: string | null) => void
  setSelectedTag: (tag: string | null) => void

  setDraftContent: (system: string, user: string) => void
  updateVariableValue: (key: string, val: string) => void
  setSelectedModels: (models: string[]) => void
  setTemperature: (temp: number) => void
  setTopP: (topP: number) => void
  setMaxTokens: (tokens: number) => void

  setIsExecuting: (executing: boolean) => void
  setIsStreaming: (streaming: boolean) => void
  appendStreamOutput: (chunk: string) => void
  clearStreamOutput: () => void

  setLatestExecutions: (execs: PromptExecution[]) => void
  setComparisonResults: (results: PromptExecution[]) => void
  setAiAssistModalOpen: (open: boolean) => void
}

export const usePromptStudioStore = create<PromptStudioState>((set) => ({
  selectedPromptId: "prompt_default_sql",
  activeTab: "editor",
  searchQuery: "",
  selectedFolderId: null,
  selectedTag: null,

  systemPromptDraft: "You are an expert PostgreSQL database administrator.",
  userPromptDraft: "Write a SQL query to fetch {{metrics}} from {{table_name}}.",
  parsedVariables: { metrics: "count(*)", table_name: "users" },
  isDirty: false,

  selectedModels: ["gpt-4o", "claude-3.5-sonnet"],
  temperature: 0.7,
  topP: 0.95,
  maxTokens: 2048,
  isExecuting: false,
  isStreaming: false,
  streamOutput: "",

  latestExecutions: [],
  comparisonResults: [],
  aiAssistModalOpen: false,

  setSelectedPromptId: (id) => set({ selectedPromptId: id }),
  setActiveTab: (tab) => set({ activeTab: tab }),
  setSearchQuery: (q) => set({ searchQuery: q }),
  setSelectedFolderId: (folderId) => set({ selectedFolderId: folderId }),
  setSelectedTag: (tag) => set({ selectedTag: tag }),

  setDraftContent: (system, user) => set({ systemPromptDraft: system, userPromptDraft: user, isDirty: true }),
  updateVariableValue: (key, val) =>
    set((state) => ({ parsedVariables: { ...state.parsedVariables, [key]: val } })),
  setSelectedModels: (models) => set({ selectedModels: models }),
  setTemperature: (temp) => set({ temperature: temp }),
  setTopP: (topP) => set({ topP: topP }),
  setMaxTokens: (tokens) => set({ maxTokens: tokens }),

  setIsExecuting: (executing) => set({ isExecuting: executing }),
  setIsStreaming: (streaming) => set({ isStreaming: streaming }),
  appendStreamOutput: (chunk) => set((state) => ({ streamOutput: state.streamOutput + chunk })),
  clearStreamOutput: () => set({ streamOutput: "" }),

  setLatestExecutions: (execs) => set({ latestExecutions: execs }),
  setComparisonResults: (results) => set({ comparisonResults: results }),
  setAiAssistModalOpen: (open) => set({ aiAssistModalOpen: open }),
}))
