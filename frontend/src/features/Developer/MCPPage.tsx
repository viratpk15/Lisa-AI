import { useNavigate } from "react-router"
import { Server, ArrowLeft, ShieldCheck } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function MCPPage() {
  const navigate = useNavigate()

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
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Model Context Protocol</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Configure external MCP servers that supply tools and resources to your local agents.
        </p>
      </div>

      <div className="p-4 rounded-xl border border-border/50 bg-secondary/20 flex items-start gap-3">
        <ShieldCheck className="h-5 w-5 text-primary shrink-0 mt-0.5" />
        <div className="space-y-1">
          <p className="text-xs font-semibold text-foreground">Secure Local Integration</p>
          <p className="text-xs text-muted-foreground leading-relaxed">
            MCP allows local tools (such as filesystem access, terminal, or GitHub repositories) to be invoked strictly under your permission and oversight.
          </p>
        </div>
      </div>

      <Card className="border-border/70 bg-card/50 shadow-xs">
        <CardHeader>
          <CardTitle className="text-base font-semibold">Active MCP Servers</CardTitle>
          <CardDescription>Servers currently registered with the Lisa AIOS runtime.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="py-12 text-center space-y-3">
            <div className="p-3 rounded-full bg-secondary/50 border border-border/40 w-fit mx-auto text-muted-foreground">
              <Server className="h-6 w-6" />
            </div>
            <div className="space-y-1">
              <p className="text-sm font-semibold text-foreground">No MCP connections configured</p>
              <p className="text-xs text-muted-foreground max-w-sm mx-auto">
                No external Model Context Protocol servers are currently active. When servers are connected, their available tools and resources will appear here.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
