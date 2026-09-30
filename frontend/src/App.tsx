import { Suspense, lazy, useEffect } from "react"
import { BrowserRouter, Routes, Route, Navigate, Outlet, useLocation } from "react-router"
import { RootProvider } from "@/providers"
import AppShell from "@/components/layout/AppShell"
import { LoadingIndicator } from "@/components/common/LoadingIndicator"
import { useAuthStore, restoreUserSession } from "@/services/store/authStore"

// Lazy load page features to optimize performance
const HomePage = lazy(() => import("@/features/Home/HomePage"))
const WorkspacePage = lazy(() => import("@/features/Workspace/WorkspacePage"))
const AgentsPage = lazy(() => import("@/features/Agents/AgentsPage"))
const MemoryPage = lazy(() => import("@/features/Memory/MemoryPage"))
const FilesPage = lazy(() => import("@/features/Files/FilesPage"))
const ToolsPage = lazy(() => import("@/features/Tools/ToolsPage"))
const PromptsPage = lazy(() => import("@/features/Prompts/PromptsPage"))
const RAGPage = lazy(() => import("@/features/RAG/RAGPage"))
const ModelsPage = lazy(() => import("@/features/Models/ModelsPage"))
const WorkflowPage = lazy(() => import("@/features/Workflows/WorkflowPage"))
const DeploymentPage = lazy(() => import("@/features/Deployments/DeploymentPage"))
const SettingsPage = lazy(() => import("@/features/Settings/SettingsPage"))
const EmailPage = lazy(() => import("@/features/Email/EmailPage"))
const AuthPage = lazy(() => import("@/features/Auth/AuthPage"))
const DeveloperPortalPage = lazy(() => import("@/features/Developer/DeveloperPortalPage"))
const MCPPage = lazy(() => import("@/features/Developer/MCPPage"))
const ConnectionsPage = lazy(() => import("@/features/Developer/ConnectionsPage"))
const ObservabilityPage = lazy(() => import("@/features/Developer/ObservabilityPage"))
const TravelPage = lazy(() => import("@/features/Travel/TravelPage"))
const JobsPage = lazy(() => import("@/features/Jobs/JobsPage"))

/**
 * Route protection wrapper requiring active user authentication.
 * Records the attempted destination in the auth store so the login flow
 * can redirect back to it after a successful authentication.
 */
function ProtectedRoute() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const isRestored = useAuthStore((state) => state.isRestored)
  const setRedirectTo = useAuthStore((state) => state.setRedirectTo)
  const location = useLocation()

  if (!isRestored) {
    return <LoadingIndicator fullScreen message="Checking session token..." />
  }

  if (!isAuthenticated) {
    // Remember where the user was trying to go before saving to /auth
    setRedirectTo(location.pathname)
    return <Navigate to="/auth" replace />
  }

  return <Outlet />
}

/**
 * Public route wrapper for login/registration forms.
 * Authenticated users are sent directly to Home (/).
 */
function AnonymousRoute() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const isRestored = useAuthStore((state) => state.isRestored)

  if (!isRestored) {
    return <LoadingIndicator fullScreen message="Checking token status..." />
  }

  return !isAuthenticated ? <Outlet /> : <Navigate to="/" replace />
}

function App() {
  // Sync and restore token session on application boot
  useEffect(() => {
    restoreUserSession()
  }, [])

  return (
    <RootProvider>
      <BrowserRouter>
        <Suspense fallback={<LoadingIndicator fullScreen message="Loading system components..." />}>
          <Routes>
            {/* Public/Anonymous auth entry */}
            <Route element={<AnonymousRoute />}>
              <Route path="auth" element={<AuthPage />} />
            </Route>

            {/* Protected system environment routing */}
            <Route element={<ProtectedRoute />}>
              <Route path="/" element={<AppShell />}>
                {/* 1. Primary Product Routes */}
                <Route index element={<HomePage />} />
                <Route path="assistant" element={<WorkspacePage />} />
                <Route path="email" element={<EmailPage />} />
                <Route path="files" element={<FilesPage />} />
                <Route path="travel" element={<TravelPage />} />
                <Route path="jobs" element={<JobsPage />} />
                
                {/* 2. Settings Subroutes */}
                <Route path="settings" element={<SettingsPage />} />
                <Route path="settings/account" element={<SettingsPage />} />
                <Route path="settings/appearance" element={<SettingsPage />} />
                <Route path="settings/memory" element={<SettingsPage />} />

                {/* 3. Developer / AIOS Portal Routes */}
                <Route path="settings/developer" element={<DeveloperPortalPage />} />
                <Route path="settings/developer/overview" element={<DeveloperPortalPage />} />
                
                {/* Developer Core */}
                <Route path="settings/developer/core/agents" element={<AgentsPage />} />
                <Route path="settings/developer/core/tools" element={<ToolsPage />} />
                <Route path="settings/developer/core/workflows" element={<WorkflowPage />} />

                {/* Developer Knowledge */}
                <Route path="settings/developer/knowledge/memory" element={<MemoryPage />} />
                <Route path="settings/developer/knowledge/rag" element={<RAGPage />} />

                {/* Developer AI */}
                <Route path="settings/developer/ai/models" element={<ModelsPage />} />
                <Route path="settings/developer/ai/prompts" element={<PromptsPage />} />

                {/* Developer Integrations */}
                <Route path="settings/developer/integrations/mcp" element={<MCPPage />} />
                <Route path="settings/developer/integrations/connections" element={<ConnectionsPage />} />

                {/* Developer Infrastructure */}
                <Route path="settings/developer/infrastructure/deployment" element={<DeploymentPage />} />
                <Route path="settings/developer/infrastructure/observability" element={<ObservabilityPage />} />

                {/* Shorthand Developer Redirects */}
                <Route path="settings/developer/agents" element={<Navigate to="/settings/developer/core/agents" replace />} />
                <Route path="settings/developer/tools" element={<Navigate to="/settings/developer/core/tools" replace />} />
                <Route path="settings/developer/workflows" element={<Navigate to="/settings/developer/core/workflows" replace />} />
                <Route path="settings/developer/memory" element={<Navigate to="/settings/developer/knowledge/memory" replace />} />
                <Route path="settings/developer/rag" element={<Navigate to="/settings/developer/knowledge/rag" replace />} />
                <Route path="settings/developer/models" element={<Navigate to="/settings/developer/ai/models" replace />} />
                <Route path="settings/developer/prompts" element={<Navigate to="/settings/developer/ai/prompts" replace />} />
                <Route path="settings/developer/deployment" element={<Navigate to="/settings/developer/infrastructure/deployment" replace />} />

                {/* 4. Legacy Route Redirects (10 canonical redirects) */}
                <Route path="dashboard" element={<Navigate to="/" replace />} />
                <Route path="workspace" element={<Navigate to="/assistant" replace />} />
                <Route path="agents" element={<Navigate to="/settings/developer/core/agents" replace />} />
                <Route path="memory" element={<Navigate to="/settings/developer/knowledge/memory" replace />} />
                <Route path="tools" element={<Navigate to="/settings/developer/core/tools" replace />} />
                <Route path="rag" element={<Navigate to="/settings/developer/knowledge/rag" replace />} />
                <Route path="models" element={<Navigate to="/settings/developer/ai/models" replace />} />
                <Route path="workflows" element={<Navigate to="/settings/developer/core/workflows" replace />} />
                <Route path="deployments" element={<Navigate to="/settings/developer/infrastructure/deployment" replace />} />
                <Route path="prompts" element={<Navigate to="/settings/developer/ai/prompts" replace />} />
              </Route>
            </Route>

            {/* Fallback: unknown routes go to root guard */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </RootProvider>
  )
}

export default App
