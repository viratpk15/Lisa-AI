// frontend/src/features/Deployments/store/useDeploymentStudioStore.ts

import { create } from "zustand"
import type { DeploymentTabType } from "../types/deployments.types"

interface DeploymentStudioState {
  activeTab: DeploymentTabType
  setActiveTab: (tab: DeploymentTabType) => void

  selectedEnvId: string
  setSelectedEnvId: (envId: string) => void

  selectedProvider: string
  setSelectedProvider: (provider: string) => void

  isSecretModalOpen: boolean
  setSecretModalOpen: (isOpen: boolean) => void

  logs: Array<{ timestamp: string; level: string; message: string }>
  addLog: (log: { timestamp: string; level: string; message: string }) => void
  clearLogs: () => void
}

export const useDeploymentStudioStore = create<DeploymentStudioState>((set) => ({
  activeTab: "dashboard",
  setActiveTab: (tab) => set({ activeTab: tab }),

  selectedEnvId: "prod",
  setSelectedEnvId: (envId) => set({ selectedEnvId: envId }),

  selectedProvider: "docker",
  setSelectedProvider: (provider) => set({ selectedProvider: provider }),

  isSecretModalOpen: false,
  setSecretModalOpen: (isOpen) => set({ isSecretModalOpen: isOpen }),

  logs: [
    { timestamp: new Date().toLocaleTimeString(), level: "INFO", message: "Deployment Studio initialized" },
    { timestamp: new Date().toLocaleTimeString(), level: "INFO", message: "Connected to Production Target Cluster (3/3 Healthy)" },
  ],
  addLog: (log) => set((state) => ({ logs: [...state.logs, log] })),
  clearLogs: () => set({ logs: [] }),
}))
