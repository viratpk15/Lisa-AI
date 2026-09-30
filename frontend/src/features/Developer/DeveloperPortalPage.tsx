import { useNavigate } from "react-router"
import {
  Bot,
  ToyBrick,
  GitBranch,
  Brain,
  Database,
  Sparkles,
  FileCode,
  Server,
  Key,
  Rocket,
  Activity,
  ArrowRight,
  ArrowLeft
} from "lucide-react"
import { Button } from "@/components/ui/button"

interface DeveloperLink {
  name: string
  desc: string
  path: string
  icon: typeof Bot
}

interface DeveloperGroup {
  group: string
  links: DeveloperLink[]
}

const groups: DeveloperGroup[] = [
  {
    group: "Core",
    links: [
      { name: "Agents", desc: "Agent definitions, multi-agent teams, and playground", path: "/settings/developer/core/agents", icon: Bot },
      { name: "Tools", desc: "Tool engine registry and unified schema definitions", path: "/settings/developer/core/tools", icon: ToyBrick },
      { name: "Workflows", desc: "LangGraph orchestration state machines and workflows", path: "/settings/developer/core/workflows", icon: GitBranch },
    ]
  },
  {
    group: "Knowledge",
    links: [
      { name: "Memory", desc: "Working memory buffer, graph relations, and recall", path: "/settings/developer/knowledge/memory", icon: Brain },
      { name: "RAG", desc: "Document ingestion, embeddings, chunking, and retrieval", path: "/settings/developer/knowledge/rag", icon: Database },
    ]
  },
  {
    group: "AI",
    links: [
      { name: "Models", desc: "Provider registry, fallback chains, and latency benchmarks", path: "/settings/developer/ai/models", icon: Sparkles },
      { name: "Prompts", desc: "System prompt engineering studio and prompt library", path: "/settings/developer/ai/prompts", icon: FileCode },
    ]
  },
  {
    group: "Integrations",
    links: [
      { name: "MCP", desc: "Model Context Protocol external tool servers", path: "/settings/developer/integrations/mcp", icon: Server },
      { name: "Connections", desc: "External service accounts, OAuth tokens, and status", path: "/settings/developer/integrations/connections", icon: Key },
    ]
  },
  {
    group: "Infrastructure",
    links: [
      { name: "Deployment", desc: "Runtime hosting environments and deployment targets", path: "/settings/developer/infrastructure/deployment", icon: Rocket },
      { name: "Observability", desc: "Execution traces, telemetry logs, and runtime analytics", path: "/settings/developer/infrastructure/observability", icon: Activity },
    ]
  }
]

export default function DeveloperPortalPage() {
  const navigate = useNavigate()

  return (
    <div className="max-w-4xl mx-auto space-y-8 py-2">
      {/* Header */}
      <div className="space-y-3">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate("/settings")}
          className="text-xs text-muted-foreground hover:text-foreground -ml-2 cursor-pointer gap-1.5"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          <span>Back to Settings</span>
        </Button>

        <div className="space-y-1.5">
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Developer / AIOS</h1>
          <p className="text-sm text-muted-foreground leading-relaxed max-w-2xl">
            Advanced tools and configuration for power users and engineers. You don't need to use these for daily tasks.
          </p>
        </div>
      </div>

      {/* Capability Groups */}
      <div className="space-y-8">
        {groups.map((g) => (
          <div key={g.group} className="space-y-3">
            <h2 className="text-xs font-mono font-semibold uppercase tracking-wider text-muted-foreground">
              {g.group}
            </h2>
            <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-3">
              {g.links.map((link) => {
                const Icon = link.icon
                return (
                  <button
                    key={link.path}
                    onClick={() => navigate(link.path)}
                    className="flex flex-col items-start p-4 rounded-xl border border-border/60 bg-card/50 hover:bg-secondary/40 hover:border-border transition-all text-left group cursor-pointer outline-none shadow-xs"
                  >
                    <div className="flex items-center justify-between w-full mb-2">
                      <div className="p-2 rounded-lg bg-primary/10 text-primary group-hover:scale-105 transition-transform">
                        <Icon className="h-4 w-4" />
                      </div>
                      <ArrowRight className="h-3.5 w-3.5 text-muted-foreground/40 group-hover:text-foreground group-hover:translate-x-0.5 transition-all" />
                    </div>
                    <span className="text-sm font-semibold text-foreground">{link.name}</span>
                    <span className="text-xs text-muted-foreground mt-1 line-clamp-2 leading-relaxed">
                      {link.desc}
                    </span>
                  </button>
                )
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
