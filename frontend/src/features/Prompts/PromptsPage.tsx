import { Code, Play, Columns, GitCommit, Award, Activity, Sparkles } from "lucide-react"
import { WorkspaceShell } from "../Tools/components/shell/WorkspaceShell"
import { PromptLibrary } from "./components/library/PromptLibrary"
import { MonacoPromptEditor } from "./components/editor/MonacoPromptEditor"
import { VariablesPanel } from "./components/variables/VariablesPanel"
import { MultiModelPlayground } from "./components/playground/MultiModelPlayground"
import { VersionDiffViewer } from "./components/versions/VersionDiffViewer"
import { PromptComparisonGrid } from "./components/compare/PromptComparisonGrid"
import { EvaluationSuitePanel } from "./components/evaluation/EvaluationSuitePanel"
import { PromptAnalyticsPanel } from "./components/analytics/PromptAnalyticsPanel"
import { TemplateMarketplace } from "./components/marketplace/TemplateMarketplace"
import { AIAssistantModal } from "./components/assistant/AIAssistantModal"
import { usePromptStudioStore } from "./store/usePromptStudioStore"

export default function PromptsPage() {
  const activeTab = usePromptStudioStore((s) => s.activeTab)
  const setActiveTab = usePromptStudioStore((s) => s.setActiveTab)

  return (
    <WorkspaceShell
      title="Prompt Studio"
      subtitle="Commercial Prompt Engineering Workspace & Version Control System"
    >
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-full items-start">
        {/* Left Column: Prompt Library */}
        <div className="lg:col-span-4 xl:col-span-3">
          <PromptLibrary />
        </div>

        {/* Center Main Stage Column: Editor, Playground, Compare, Versions, Eval, Analytics, Templates */}
        <div className="lg:col-span-8 xl:col-span-6 space-y-4">
          {/* Stage Tab Navigation */}
          <div className="flex items-center gap-1.5 p-1 bg-secondary/20 border border-border/40 rounded-xl overflow-x-auto">
            <button
              onClick={() => setActiveTab("editor")}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg cursor-pointer transition-all ${
                activeTab === "editor"
                  ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 shadow-xs"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/40"
              }`}
            >
              <Code className="h-3.5 w-3.5" />
              Prompt Editor
            </button>

            <button
              onClick={() => setActiveTab("playground")}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg cursor-pointer transition-all ${
                activeTab === "playground"
                  ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 shadow-xs"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/40"
              }`}
            >
              <Play className="h-3.5 w-3.5" />
              Playground
            </button>

            <button
              onClick={() => setActiveTab("compare")}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg cursor-pointer transition-all ${
                activeTab === "compare"
                  ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 shadow-xs"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/40"
              }`}
            >
              <Columns className="h-3.5 w-3.5" />
              A/B Compare
            </button>

            <button
              onClick={() => setActiveTab("versions")}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg cursor-pointer transition-all ${
                activeTab === "versions"
                  ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 shadow-xs"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/40"
              }`}
            >
              <GitCommit className="h-3.5 w-3.5" />
              Versions
            </button>

            <button
              onClick={() => setActiveTab("eval")}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg cursor-pointer transition-all ${
                activeTab === "eval"
                  ? "bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-xs"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/40"
              }`}
            >
              <Award className="h-3.5 w-3.5 text-amber-400" />
              Evaluation
            </button>

            <button
              onClick={() => setActiveTab("analytics")}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg cursor-pointer transition-all ${
                activeTab === "analytics"
                  ? "bg-violet-500/20 text-violet-300 border border-violet-500/40 shadow-xs"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/40"
              }`}
            >
              <Activity className="h-3.5 w-3.5 text-violet-400" />
              Analytics
            </button>

            <button
              onClick={() => setActiveTab("templates")}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg cursor-pointer transition-all ${
                activeTab === "templates"
                  ? "bg-violet-500/20 text-violet-300 border border-violet-500/40 shadow-xs"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/40"
              }`}
            >
              <Sparkles className="h-3.5 w-3.5 text-violet-400" />
              Templates
            </button>
          </div>

          {/* Active Tab View */}
          {activeTab === "editor" && <MonacoPromptEditor />}
          {activeTab === "playground" && <MultiModelPlayground />}
          {activeTab === "compare" && <PromptComparisonGrid />}
          {activeTab === "versions" && <VersionDiffViewer />}
          {activeTab === "eval" && <EvaluationSuitePanel />}
          {activeTab === "analytics" && <PromptAnalyticsPanel />}
          {activeTab === "templates" && <TemplateMarketplace />}
        </div>

        {/* Right Column: Variables & Controls Inspector */}
        <div className="hidden xl:block xl:col-span-3 sticky top-0">
          <VariablesPanel />
        </div>
      </div>

      {/* AI Assistant Optimization Overlay */}
      <AIAssistantModal />
    </WorkspaceShell>
  )
}
