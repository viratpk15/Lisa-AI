// frontend/src/features/Agents/AgentsPage.tsx
/**
 * Entry page for Agent Studio.
 * Uses existing WorkspaceShell layout and provides navigation tabs for sub‑features.
 */
import { Suspense, lazy, useState } from "react"
import { WorkspaceShell } from "../Tools/components/shell/WorkspaceShell"
import { LoadingIndicator } from "@/components/common/LoadingIndicator"

// Lazy load heavy sub‑components to keep bundle size low
const AgentLibrary = lazy(() => import("./components/AgentLibrary"));
const AgentBuilder = lazy(() => import("./components/AgentBuilder"));
const AgentPlayground = lazy(() => import("./components/AgentPlayground"));
const TeamBuilder = lazy(() => import("./components/TeamBuilder"));
const AnalyticsDashboard = lazy(() => import("./components/AnalyticsDashboard"));

export default function AgentsPage() {
  const [activeTab, setActiveTab] = useState<string>("library");

  const renderTab = () => {
    switch (activeTab) {
      case "library":
        return <AgentLibrary />;
      case "builder":
        return <AgentBuilder />;
      case "playground":
        return <AgentPlayground />;
      case "team":
        return <TeamBuilder />;
      case "analytics":
        return <AnalyticsDashboard />;
      default:
        return <AgentLibrary />;
    }
  };

  return (
    <WorkspaceShell
      title="Agent Studio"
      subtitle="Build, version, and orchestrate AI agents and multi-agent teams"
    >
      <div className="flex flex-col h-full">
        <nav className="flex border-b border-divider mb-4">
          {[
            { id: "library", label: "Library" },
            { id: "builder", label: "Builder" },
            { id: "playground", label: "Playground" },
            { id: "team", label: "Team Builder" },
            { id: "analytics", label: "Analytics" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 text-sm font-medium focus:outline-none ${
                activeTab === tab.id ? "border-b-2 border-primary text-primary" : "text-muted"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
        <Suspense fallback={<LoadingIndicator message="Loading..." />}>{renderTab()}</Suspense>
      </div>
    </WorkspaceShell>
  );
}
