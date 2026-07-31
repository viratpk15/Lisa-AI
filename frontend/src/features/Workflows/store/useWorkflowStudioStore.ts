// frontend/src/features/Workflows/store/useWorkflowStudioStore.ts

import { create } from "zustand"
import type { WorkflowTabType, WorkflowNode, WorkflowEdge } from "../types/workflows.types"

interface WorkflowStudioState {
  activeTab: WorkflowTabType
  setActiveTab: (tab: WorkflowTabType) => void

  activeWorkflowId: string
  setActiveWorkflowId: (id: string) => void

  mode: "edit" | "debug" | "run"
  setMode: (mode: "edit" | "debug" | "run") => void

  selectedNodeId: string | null
  setSelectedNodeId: (nodeId: string | null) => void

  nodes: WorkflowNode[]
  edges: WorkflowEdge[]
  setNodes: (nodes: WorkflowNode[]) => void
  setEdges: (edges: WorkflowEdge[]) => void
  addNode: (node: WorkflowNode) => void
  updateNodeConfig: (nodeId: string, config: Record<string, any>) => void

  breakpoints: Set<string>
  toggleBreakpoint: (nodeId: string) => void

  activeExecutionId: string | null
  setActiveExecutionId: (execId: string | null) => void
  executionLogs: Array<{ node_id: string; status: string; message: string }>
  addExecutionLog: (log: { node_id: string; status: string; message: string }) => void
  clearExecutionLogs: () => void
}

export const useWorkflowStudioStore = create<WorkflowStudioState>((set) => ({
  activeTab: "canvas",
  setActiveTab: (tab) => set({ activeTab: tab }),

  activeWorkflowId: "wf_agent_tool_pipeline",
  setActiveWorkflowId: (id) => set({ activeWorkflowId: id }),

  mode: "edit",
  setMode: (mode) => set({ mode }),

  selectedNodeId: "node_agent",
  setSelectedNodeId: (nodeId) => set({ selectedNodeId: nodeId }),

  nodes: [
    { id: "node_start", type: "custom", position: { x: 100, y: 150 }, data: { label: "HTTP Ingress", node_type: "http", config: { method: "GET" } } },
    { id: "node_agent", type: "custom", position: { x: 350, y: 150 }, data: { label: "Coding Agent", node_type: "agent", config: { agent_id: "code_assistant" } } },
    { id: "node_tool", type: "custom", position: { x: 600, y: 150 }, data: { label: "Python Execution", node_type: "tool", config: { tool_name: "python_interpreter" } } },
    { id: "node_approval", type: "custom", position: { x: 850, y: 150 }, data: { label: "Human Approval", node_type: "approval", config: { approver_role: "admin" } } },
  ],

  edges: [
    { id: "e1-2", source: "node_start", target: "node_agent" },
    { id: "e2-3", source: "node_agent", target: "node_tool" },
    { id: "e3-4", source: "node_tool", target: "node_approval" },
  ],

  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),
  addNode: (node) => set((state) => ({ nodes: [...state.nodes, node] })),
  updateNodeConfig: (nodeId, config) =>
    set((state) => ({
      nodes: state.nodes.map((n) =>
        n.id === nodeId ? { ...n, data: { ...n.data, config: { ...n.data.config, ...config } } } : n
      ),
    })),

  breakpoints: new Set(["node_tool"]),
  toggleBreakpoint: (nodeId) =>
    set((state) => {
      const next = new Set(state.breakpoints)
      if (next.has(nodeId)) next.delete(nodeId)
      else next.add(nodeId)
      return { breakpoints: next }
    }),

  activeExecutionId: null,
  setActiveExecutionId: (execId) => set({ activeExecutionId: execId }),
  executionLogs: [],
  addExecutionLog: (log) => set((state) => ({ executionLogs: [...state.executionLogs, log] })),
  clearExecutionLogs: () => set({ executionLogs: [] }),
}))
