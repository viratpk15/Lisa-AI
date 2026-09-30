import { useState } from "react"
import { useNavigate } from "react-router"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/services/api/apiClient"
import { ArrowLeft, Mail, CheckCircle2, XCircle, RefreshCw, Unplug, ShieldCheck } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

interface GoogleStatusResponse {
  connected: boolean
  email_address?: string
  expires_at?: string
  scopes?: string[]
}

export default function ConnectionsPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [connecting, setConnecting] = useState(false)

  // Query Google OAuth status
  const { data: status, isLoading, refetch } = useQuery<GoogleStatusResponse>({
    queryKey: ["auth", "google", "status"],
    queryFn: async () => {
      try {
        return await apiClient.get<GoogleStatusResponse>("/api/v1/auth/google/status")
      } catch {
        return { connected: false }
      }
    },
    staleTime: 30_000,
  })

  // Disconnect mutation
  const disconnectMutation = useMutation({
    mutationFn: async () => {
      return apiClient.post("/api/v1/auth/google/disconnect")
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["auth", "google", "status"] })
      queryClient.invalidateQueries({ queryKey: ["email"] })
    }
  })

  const handleConnect = async () => {
    try {
      setConnecting(true)
      const res = await apiClient.get<{ url?: string; authorization_url?: string }>("/api/v1/auth/google/url")
      const targetUrl = res?.url || res?.authorization_url
      if (targetUrl) {
        window.location.href = targetUrl
      } else {
        setConnecting(false)
      }
    } catch (err) {
      console.error("Failed to initiate Google OAuth:", err)
      setConnecting(false)
    }
  }

  const isConnected = status?.connected === true

  return (
    <div className="max-w-4xl mx-auto space-y-6 py-2">
      <Button
        variant="ghost"
        size="sm"
        onClick={() => navigate("/settings/developer")}
        className="text-xs text-muted-foreground hover:text-foreground -ml-2 cursor-pointer gap-1.5"
      >
        <ArrowLeft className="h-3.5 w-3.5" />
        <span>Back to Developer Portal</span>
      </Button>

      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Service Connections</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Manage authorized third-party OAuth service connections and token states.
        </p>
      </div>

      <div className="p-4 rounded-xl border border-border/50 bg-secondary/20 flex items-start gap-3">
        <ShieldCheck className="h-5 w-5 text-primary shrink-0 mt-0.5" />
        <div className="space-y-1">
          <p className="text-xs font-semibold text-foreground">Token Security & Isolation</p>
          <p className="text-xs text-muted-foreground leading-relaxed">
            OAuth refresh tokens are encrypted at rest with local ciphers and never exposed to the client or outside processes.
          </p>
        </div>
      </div>

      <Card className="border-border/70 bg-card/50 shadow-xs">
        <CardHeader className="flex flex-row items-center justify-between pb-3">
          <div>
            <CardTitle className="text-base font-semibold">Configured Service Integrations</CardTitle>
            <CardDescription>Accounts authorized for Jarvis AIOS personal tools.</CardDescription>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => refetch()}
            className="text-xs text-muted-foreground hover:text-foreground cursor-pointer gap-1.5"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            <span>Refresh</span>
          </Button>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="py-8 text-center text-xs text-muted-foreground">
              Checking integration statuses...
            </div>
          ) : (
            <div className="p-4 rounded-xl border border-border/50 bg-secondary/20 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-lg bg-red-500/10 text-red-400 border border-red-500/20 shrink-0">
                  <Mail className="h-5 w-5" />
                </div>
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-foreground">Google / Gmail</span>
                    {isConnected ? (
                      <span className="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20 flex items-center gap-1">
                        <CheckCircle2 className="h-3 w-3" /> Connected
                      </span>
                    ) : (
                      <span className="text-[10px] font-mono font-bold text-muted-foreground bg-secondary px-2 py-0.5 rounded-full border border-border/50 flex items-center gap-1">
                        <XCircle className="h-3 w-3" /> Disconnected
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {isConnected && status?.email_address
                      ? `Authorized as ${status.email_address} (Read-only access)`
                      : "Used by Email Agent for intelligence classification and digests."}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2 shrink-0">
                {isConnected ? (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => disconnectMutation.mutate()}
                    disabled={disconnectMutation.isPending}
                    className="text-xs text-destructive hover:bg-destructive/10 border-destructive/30 cursor-pointer gap-1.5"
                  >
                    <Unplug className="h-3.5 w-3.5" />
                    <span>{disconnectMutation.isPending ? "Disconnecting..." : "Disconnect"}</span>
                  </Button>
                ) : (
                  <Button
                    size="sm"
                    onClick={handleConnect}
                    disabled={connecting}
                    className="text-xs font-medium cursor-pointer gap-1.5"
                  >
                    <Mail className="h-3.5 w-3.5" />
                    <span>{connecting ? "Connecting..." : "Connect Google"}</span>
                  </Button>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
