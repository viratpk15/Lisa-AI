import { create } from "zustand"
import type { ToolResult, ConsoleLogEntry, PendingApprovalItem } from "../types/tools.types"

export type StudioTab = "explorer" | "runner" | "console" | "history" | "approvals" | "metrics"

interface ToolConsoleState {
  selectedToolName: string | null
  searchQuery: string
  selectedCategory: string | null
  selectedTag: string | null
  sidebarCollapsed: boolean
  commandPaletteOpen: boolean
  activeTab: StudioTab

  // Execution & Live Logs State
  formParameters: Record<string, any>
  latestResult: ToolResult | null
  executionHistory: ToolResult[]
  pendingApprovals: PendingApprovalItem[]
  consoleLogs: ConsoleLogEntry[]
  isExecuting: boolean
  isStreaming: boolean
  autoScroll: boolean
  isPaused: boolean

  // Actions
  setSelectedToolName: (name: string | null) => void
  setSearchQuery: (query: string) => void
  setSelectedCategory: (category: string | null) => void
  setSelectedTag: (tag: string | null) => void
  toggleSidebar: () => void
  setCommandPaletteOpen: (open: boolean) => void
  setActiveTab: (tab: StudioTab) => void
  resetFilters: () => void

  // Execution Actions
  setFormParameters: (params: Record<string, any>) => void
  updateFormParameter: (key: string, value: any) => void
  setLatestResult: (result: ToolResult | null) => void
  addExecutionHistory: (result: ToolResult) => void
  clearExecutionHistory: () => void
  addPendingApproval: (item: PendingApprovalItem) => void
  removePendingApproval: (executionId: string) => void
  addConsoleLog: (type: ConsoleLogEntry["type"], message: string, executionId?: string) => void
  clearConsoleLogs: () => void
  setIsExecuting: (executing: boolean) => void
  setIsStreaming: (streaming: boolean) => void
  setAutoScroll: (autoScroll: boolean) => void
  setIsPaused: (paused: boolean) => void
}

export const useToolConsoleStore = create<ToolConsoleState>((set) => ({
  selectedToolName: "filesystem",
  searchQuery: "",
  selectedCategory: null,
  selectedTag: null,
  sidebarCollapsed: false,
  commandPaletteOpen: false,
  activeTab: "runner",

  formParameters: {},
  latestResult: null,
  executionHistory: [],
  pendingApprovals: [],
  consoleLogs: [],
  isExecuting: false,
  isStreaming: false,
  autoScroll: true,
  isPaused: false,

  setSelectedToolName: (name) => set({ selectedToolName: name, latestResult: null }),
  setSearchQuery: (query) => set({ searchQuery: query }),
  setSelectedCategory: (category) => set({ selectedCategory: category }),
  setSelectedTag: (tag) => set({ selectedTag: tag }),
  toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
  setCommandPaletteOpen: (open) => set({ commandPaletteOpen: open }),
  setActiveTab: (tab) => set({ activeTab: tab }),
  resetFilters: () => set({ searchQuery: "", selectedCategory: null, selectedTag: null }),

  setFormParameters: (params) => set({ formParameters: params }),
  updateFormParameter: (key, value) =>
    set((state) => ({ formParameters: { ...state.formParameters, [key]: value } })),
  setLatestResult: (result) => set({ latestResult: result }),
  addExecutionHistory: (result) =>
    set((state) => ({ executionHistory: [result, ...state.executionHistory] })),
  clearExecutionHistory: () => set({ executionHistory: [] }),
  addPendingApproval: (item) =>
    set((state) => ({ pendingApprovals: [item, ...state.pendingApprovals] })),
  removePendingApproval: (executionId) =>
    set((state) => ({
      pendingApprovals: state.pendingApprovals.filter((a) => a.execution_id !== executionId),
    })),
  addConsoleLog: (type, message, executionId) =>
    set((state) => {
      if (state.isPaused) return state
      const entry: ConsoleLogEntry = {
        id: `log_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`,
        timestamp: new Date().toLocaleTimeString(),
        type,
        message,
        executionId,
      }
      return { consoleLogs: [...state.consoleLogs, entry] }
    }),
  clearConsoleLogs: () => set({ consoleLogs: [] }),
  setIsExecuting: (executing) => set({ isExecuting: executing }),
  setIsStreaming: (streaming) => set({ isStreaming: streaming }),
  setAutoScroll: (autoScroll) => set({ autoScroll: autoScroll }),
  setIsPaused: (paused) => set({ isPaused: paused }),
}))
