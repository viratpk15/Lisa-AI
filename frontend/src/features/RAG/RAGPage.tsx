import { Database, Scissors, Sliders, Award, Activity, Share2 } from "lucide-react"
import { WorkspaceShell } from "../Tools/components/shell/WorkspaceShell"
import { DatasetLibrary } from "./components/library/DatasetLibrary"
import { DocumentExplorer } from "./components/explorer/DocumentExplorer"
import { ChunkInspector } from "./components/chunks/ChunkInspector"
import { HybridSearchPanel } from "./components/hybrid/HybridSearchPanel"
import { RAGEvaluationDashboard } from "./components/evaluation/RAGEvaluationDashboard"
import { RAGAnalyticsPanel } from "./components/analytics/RAGAnalyticsPanel"
import { KnowledgeGraphViewer } from "./components/graph/KnowledgeGraphViewer"
import { useRAGStudioStore } from "./store/useRAGStudioStore"

export default function RAGPage() {
  const activeTab = useRAGStudioStore((s) => s.activeTab)
  const setActiveTab = useRAGStudioStore((s) => s.setActiveTab)

  return (
    <WorkspaceShell
      title="RAG Studio"
      subtitle="Commercial Retrieval-Augmented Generation & Vector Engineering Workspace"
    >
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-full items-start">
        {/* Left Column: Dataset Library */}
        <div className="lg:col-span-4 xl:col-span-3">
          <DatasetLibrary />
        </div>

        {/* Center Stage Column: Tabs & Main Views */}
        <div className="lg:col-span-8 xl:col-span-9 space-y-4">
          {/* Stage Tab Navigation */}
          <div className="flex items-center gap-1.5 p-1 bg-secondary/20 border border-border/40 rounded-xl overflow-x-auto">
            <button
              onClick={() => setActiveTab("datasets")}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg cursor-pointer transition-all ${
                activeTab === "datasets"
                  ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 shadow-xs"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/40"
              }`}
            >
              <Database className="h-3.5 w-3.5" />
              Datasets & Docs
            </button>

            <button
              onClick={() => setActiveTab("chunks")}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg cursor-pointer transition-all ${
                activeTab === "chunks"
                  ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 shadow-xs"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/40"
              }`}
            >
              <Scissors className="h-3.5 w-3.5" />
              Chunking Inspector
            </button>

            <button
              onClick={() => setActiveTab("hybrid")}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg cursor-pointer transition-all ${
                activeTab === "hybrid"
                  ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 shadow-xs"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/40"
              }`}
            >
              <Sliders className="h-3.5 w-3.5" />
              Hybrid Search & Reranker
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
              Evaluation Suite
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
              onClick={() => setActiveTab("graph")}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg cursor-pointer transition-all ${
                activeTab === "graph"
                  ? "bg-violet-500/20 text-violet-300 border border-violet-500/40 shadow-xs"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/40"
              }`}
            >
              <Share2 className="h-3.5 w-3.5 text-violet-400" />
              Knowledge Graph
            </button>
          </div>

          {/* Active Tab Component Render */}
          {activeTab === "datasets" && <DocumentExplorer />}
          {activeTab === "chunks" && <ChunkInspector />}
          {activeTab === "hybrid" && <HybridSearchPanel />}
          {activeTab === "eval" && <RAGEvaluationDashboard />}
          {activeTab === "analytics" && <RAGAnalyticsPanel />}
          {activeTab === "graph" && <KnowledgeGraphViewer />}
        </div>
      </div>
    </WorkspaceShell>
  )
}
