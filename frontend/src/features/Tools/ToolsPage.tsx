import { Play, Terminal, History, AlertTriangle, Activity } from "lucide-react"
import { WorkspaceShell } from "./components/shell/WorkspaceShell"
import { ToolExplorer } from "./components/explorer/ToolExplorer"
import { ToolInspector } from "./components/inspector/ToolInspector"
import { ToolRunner } from "./components/runner/ToolRunner"
import { ExecutionConsole } from "./components/console/ExecutionConsole"
import { ExecutionHistory } from "./components/history/ExecutionHistory"
import { ApprovalQueue } from "./components/approvals/ApprovalQueue"
import { ObservabilityPanel } from "./components/observability/ObservabilityPanel"
import { useToolConsoleStore } from "./store/useToolConsoleStore"

export default function ToolsPage() {
  const activeTab = useToolConsoleStore((s) => s.activeTab)
  const setActiveTab = useToolConsoleStore((s) => s.setActiveTab)
  const pendingApprovals = useToolConsoleStore((s) => s.pendingApprovals)
  const executionHistory = useToolConsoleStore((s) => s.executionHistory)

  return (
    <WorkspaceShell
      title="Tool Console"
      subtitle="Interactive Tool Runner, Live SSE Console & Real-Time Observability Analytics"
    >
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-full items-start">
        {/* Left Column: Tool Explorer */}
        <div className="lg:col-span-4 xl:col-span-3">
          <ToolExplorer />
        </div>

        {/* Center Main Stage Column: Dynamic Runner, Console, History, Approvals, Observability */}
        <div className="lg:col-span-8 xl:col-span-6 space-y-4">
          {/* Navigation Tab Bar */}
          <div className="flex items-center gap-1.5 p-1 bg-secondary/20 border border-border/40 rounded-xl overflow-x-auto">
            <button
              onClick={() => setActiveTab("runner")}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg cursor-pointer transition-all ${
                activeTab === "runner"
                  ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 shadow-xs"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/40"
              }`}
            >
              <Play className="h-3.5 w-3.5" />
              Tool Runner
            </button>

            <button
              onClick={() => setActiveTab("console")}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg cursor-pointer transition-all ${
                activeTab === "console"
                  ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 shadow-xs"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/40"
              }`}
            >
              <Terminal className="h-3.5 w-3.5" />
              Live Console
            </button>

            <button
              onClick={() => setActiveTab("history")}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg cursor-pointer transition-all ${
                activeTab === "history"
                  ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 shadow-xs"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/40"
              }`}
            >
              <History className="h-3.5 w-3.5" />
              History ({executionHistory.length})
            </button>

            <button
              onClick={() => setActiveTab("approvals")}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg cursor-pointer transition-all relative ${
                activeTab === "approvals"
                  ? "bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-xs"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/40"
              }`}
            >
              <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />
              Approvals
              {pendingApprovals.length > 0 && (
                <span className="ml-1 px-1.5 py-0.2 text-[10px] font-mono font-bold bg-amber-500 text-black rounded-full">
                  {pendingApprovals.length}
                </span>
              )}
            </button>

            <button
              onClick={() => setActiveTab("metrics")}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg cursor-pointer transition-all ${
                activeTab === "metrics"
                  ? "bg-violet-500/20 text-violet-300 border border-violet-500/40 shadow-xs"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/40"
              }`}
            >
              <Activity className="h-3.5 w-3.5 text-violet-400" />
              Observability
            </button>
          </div>

          {/* Active Tab Content View */}
          {activeTab === "runner" && <ToolRunner />}
          {activeTab === "console" && <ExecutionConsole />}
          {activeTab === "history" && <ExecutionHistory />}
          {activeTab === "approvals" && <ApprovalQueue />}
          {activeTab === "metrics" && <ObservabilityPanel />}
        </div>

        {/* Right Column: Tool Inspector */}
        <div className="hidden xl:block xl:col-span-3 sticky top-0">
          <ToolInspector />
        </div>
      </div>
    </WorkspaceShell>
  )
}
