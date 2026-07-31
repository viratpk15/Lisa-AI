// frontend/src/features/Workflows/WorkflowPage.tsx

import { WorkspaceShell } from "../Tools/components/shell/WorkspaceShell"
import { useWorkflowStudioStore } from "./store/useWorkflowStudioStore"
import { WorkflowCanvas } from "./components/builder/WorkflowCanvas"
import { NodePaletteSidebar } from "./components/builder/NodePaletteSidebar"
import { NodePropertyInspector } from "./components/builder/NodePropertyInspector"
import { WorkflowExecutionConsole } from "./components/console/WorkflowExecutionConsole"
import { WorkflowAnalyticsDashboard } from "./components/analytics/WorkflowAnalyticsDashboard"
import { WorkflowLibraryPanel } from "./components/library/WorkflowLibraryPanel"
import type { WorkflowTabType } from "./types/workflows.types"
import { GitBranch, Library, Activity } from "lucide-react"

export default function WorkflowPage() {
  const activeTab = useWorkflowStudioStore((s) => s.activeTab)
  const setActiveTab = useWorkflowStudioStore((s) => s.setActiveTab)

  const tabs: { id: WorkflowTabType; label: string; icon: any }[] = [
    { id: "canvas", label: "Visual Graph Canvas", icon: GitBranch },
    { id: "library", label: "Template Library", icon: Library },
    { id: "analytics", label: "Workflow Analytics", icon: Activity },
  ]

  return (
    <WorkspaceShell
      title="Workflow Studio"
      subtitle="Visual graph builder compiling visual node-edge diagrams directly into native LangGraph StateGraph executables."
    >
      <div className="space-y-4">
        {/* Navigation Bar */}
        <div className="flex items-center justify-between border-b border-border/40 pb-3 font-mono">
          <div className="flex items-center gap-2">
            {tabs.map((tab) => {
              const Icon = tab.icon
              const isSelected = activeTab === tab.id
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-3 py-1.5 text-xs font-bold rounded-lg cursor-pointer transition-all ${
                    isSelected
                      ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 shadow-sm"
                      : "text-muted-foreground hover:text-foreground hover:bg-secondary/40"
                  }`}
                >
                  <Icon className={`h-3.5 w-3.5 ${isSelected ? "text-cyan-400" : "text-muted-foreground"}`} />
                  <span>{tab.label}</span>
                </button>
              )}
            )}
          </div>
        </div>

        {/* Viewport Panels */}
        {activeTab === "canvas" && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
              <div className="lg:col-span-3">
                <NodePaletteSidebar />
              </div>
              <div className="lg:col-span-6">
                <WorkflowCanvas />
              </div>
              <div className="lg:col-span-3">
                <NodePropertyInspector />
              </div>
            </div>

            <WorkflowExecutionConsole />
          </div>
        )}

        {activeTab === "library" && <WorkflowLibraryPanel />}

        {activeTab === "analytics" && <WorkflowAnalyticsDashboard />}
      </div>
    </WorkspaceShell>
  )
}
