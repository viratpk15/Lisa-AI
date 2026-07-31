import { useState } from "react"
import { Share2, Server, Database, Cpu } from "lucide-react"
import { useKnowledgeGraphQuery } from "../../services/ragApi"

export function KnowledgeGraphViewer() {
  const { data: graph } = useKnowledgeGraphQuery()
  const [selectedNode, setSelectedNode] = useState<string | null>("Jarvis_AIOS")

  const nodes = graph?.nodes || [
    { id: "Jarvis_AIOS", label: "Jarvis AIOS", category: "System" },
    { id: "LangGraph", label: "LangGraph Engine", category: "Orchestrator" },
    { id: "RAG_Subsystem", label: "RAG Subsystem", category: "Module" },
    { id: "ChromaDB", label: "ChromaDB Vector Store", category: "Storage" },
    { id: "ToolEngine", label: "Tool Engine", category: "Executor" },
  ]

  const edges = graph?.edges || [
    { source: "Jarvis_AIOS", target: "LangGraph", relation: "uses" },
    { source: "Jarvis_AIOS", target: "RAG_Subsystem", relation: "includes" },
    { source: "RAG_Subsystem", target: "ChromaDB", relation: "indexes into" },
    { source: "LangGraph", target: "ToolEngine", relation: "invokes" },
  ]

  return (
    <div className="space-y-4 bg-secondary/15 border border-border/40 rounded-xl p-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border/40 pb-3">
        <div className="flex items-center gap-2">
          <Share2 className="h-4 w-4 text-cyan-400" />
          <h3 className="text-xs font-bold text-foreground">Entity-Relation Knowledge Graph Visualizer</h3>
        </div>
        <span className="text-[10px] font-mono text-muted-foreground">{nodes.length} Nodes • {edges.length} Edges</span>
      </div>

      {/* Interactive Node Graph Map Representation */}
      <div className="p-6 bg-[#0D1117] border border-border/40 rounded-xl space-y-6">
        <div className="flex flex-wrap items-center justify-center gap-4">
          {nodes.map((node) => {
            const isSelected = selectedNode === node.id
            return (
              <button
                key={node.id}
                onClick={() => setSelectedNode(node.id)}
                className={`p-3 rounded-xl border flex items-center gap-2 cursor-pointer transition-all ${
                  isSelected
                    ? "bg-cyan-500/20 text-cyan-300 border-cyan-500 shadow-md font-bold scale-105"
                    : "bg-secondary/20 text-foreground border-border/40 hover:bg-secondary/40"
                }`}
              >
                {node.category === "System" && <Cpu className="h-4 w-4 text-cyan-400" />}
                {node.category === "Storage" && <Database className="h-4 w-4 text-emerald-400" />}
                {node.category !== "System" && node.category !== "Storage" && <Server className="h-4 w-4 text-violet-400" />}
                <span className="text-xs font-mono">{node.label}</span>
              </button>
            )
          })}
        </div>

        {/* Relationship Edges Inspector */}
        <div className="pt-4 border-t border-border/30 space-y-2 font-mono text-xs">
          <span className="text-muted-foreground uppercase text-[10px]">Entity Relationships</span>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {edges.map((edge, idx) => (
              <div key={idx} className="p-2 bg-secondary/20 rounded border border-border/30 text-[11px] flex items-center justify-between">
                <span className="text-cyan-400 font-bold">{edge.source}</span>
                <span className="text-muted-foreground italic text-[10px]">-- ({edge.relation}) --&gt;</span>
                <span className="text-emerald-400 font-bold">{edge.target}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
