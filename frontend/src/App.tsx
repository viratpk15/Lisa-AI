import { Suspense, lazy, useEffect } from "react"
import { BrowserRouter, Routes, Route, Navigate, Outlet, useLocation } from "react-router"
import { RootProvider } from "@/providers"
import AppShell from "@/components/layout/AppShell"
import { LoadingIndicator } from "@/components/common/LoadingIndicator"
import { useAuthStore, restoreUserSession } from "@/services/store/authStore"

// Lazy load page features to optimize performance
const DashboardPage = lazy(() => import("@/features/Dashboard/DashboardPage"))
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
const AuthPage = lazy(() => import("@/features/Auth/AuthPage"))

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
 * Authenticated users are sent directly to /dashboard.
 */
function AnonymousRoute() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const isRestored = useAuthStore((state) => state.isRestored)

  if (!isRestored) {
    return <LoadingIndicator fullScreen message="Checking token status..." />
  }

  return !isAuthenticated ? <Outlet /> : <Navigate to="/dashboard" replace />
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
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<DashboardPage />} />
                <Route path="workspace" element={<WorkspacePage />} />
                <Route path="agents" element={<AgentsPage />} />
                <Route path="memory" element={<MemoryPage />} />
                <Route path="files" element={<FilesPage />} />
                <Route path="tools" element={<ToolsPage />} />
                <Route path="prompts" element={<PromptsPage />} />
                <Route path="rag" element={<RAGPage />} />
                <Route path="models" element={<ModelsPage />} />
                <Route path="workflows" element={<WorkflowPage />} />
                <Route path="deployments" element={<DeploymentPage />} />
                <Route path="settings" element={<SettingsPage />} />
              </Route>
            </Route>

            {/* Fallback: unknown routes go through the root auth guard */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </RootProvider>
  )
}

export default App
