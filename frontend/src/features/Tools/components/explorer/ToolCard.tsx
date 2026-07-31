import { Wrench, Terminal, FolderTree, Code, Globe, Search as SearchIcon, Calculator, Clock, ChevronRight } from "lucide-react"
import type { ToolMetadata } from "../../types/tools.types"
import { StatusChip } from "../common/StatusChip"

interface ToolCardProps {
  tool: ToolMetadata
  isSelected: boolean
  onSelect: (name: string) => void
}

export function ToolCard({ tool, isSelected, onSelect }: ToolCardProps) {
  const getToolIcon = (name: string) => {
    switch (name) {
      case "filesystem":
        return <FolderTree className="h-4 w-4 text-cyan-400" />
      case "terminal":
        return <Terminal className="h-4 w-4 text-emerald-400" />
      case "git":
        return <Code className="h-4 w-4 text-violet-400" />
      case "python":
        return <Code className="h-4 w-4 text-amber-400" />
      case "web_search":
        return <SearchIcon className="h-4 w-4 text-blue-400" />
      case "browser":
        return <Globe className="h-4 w-4 text-pink-400" />
      case "calculator":
        return <Calculator className="h-4 w-4 text-cyan-400" />
      case "datetime":
        return <Clock className="h-4 w-4 text-emerald-400" />
      default:
        return <Wrench className="h-4 w-4 text-cyan-400" />
    }
  }

  return (
    <div
      onClick={() => onSelect(tool.name)}
      className={`p-3.5 rounded-xl border transition-all cursor-pointer group flex flex-col justify-between ${
        isSelected
          ? "bg-cyan-500/10 border-cyan-500/50 shadow-md ring-1 ring-cyan-500/30"
          : "bg-secondary/20 border-border/40 hover:border-cyan-500/30 hover:bg-secondary/40"
      }`}
    >
      <div>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <div className="p-1.5 bg-secondary/50 rounded-lg border border-border/50">
              {getToolIcon(tool.name)}
            </div>
            <div>
              <h4 className="text-xs font-bold text-foreground group-hover:text-cyan-400 transition-colors">
                {tool.display_name || tool.name}
              </h4>
              <span className="text-[10px] font-mono text-muted-foreground capitalize">{tool.category}</span>
            </div>
          </div>
          <ChevronRight className={`h-4 w-4 text-muted-foreground transition-transform ${isSelected ? "translate-x-0.5 text-cyan-400" : "group-hover:translate-x-0.5"}`} />
        </div>

        <p className="text-[11px] text-muted-foreground leading-relaxed line-clamp-2 mb-3">
          {tool.description}
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-1.5 pt-2 border-t border-border/30">
        <StatusChip type="permission" value={tool.permission_level} />
        {tool.requires_approval && <StatusChip type="approval" value={true} />}
        {tool.supports_streaming && <StatusChip type="streaming" value={true} />}
        {tool.supports_async && <StatusChip type="async" value={true} />}
      </div>
    </div>
  )
}
