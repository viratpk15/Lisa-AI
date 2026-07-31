// frontend/src/features/Memory/components/graph/EntityGraphCanvas.tsx

import { useState } from "react"
import { Share2, Plus, Server, Database, Cpu, Brain } from "lucide-react"
import { useKnowledgeGraphQuery, addRelationApi } from "../../services/memoryApi"
import { useQueryClient } from "@tanstack/react-query"
import { queryKeys } from "@/services/queries/queryKeys"
import type { EntityNode, RelationEdge } from "../../types/memory.types"

export function EntityGraphCanvas() {
  const queryClient = useQueryClient()
  const { data: graphData } = useKnowledgeGraphQuery()

  const nodes: EntityNode[] = graphData?.nodes || [
    { id: 1, name: "Jarvis_AIOS", category: "System", attributes: {}, created_at: "" },
    { id: 2, name: "Memory_Studio", category: "Subsystem", attributes: {}, created_at: "" },
    { id: 3, name: "LangGraph", category: "Orchestrator", attributes: {}, created_at: "" },
    { id: 4, name: "ChromaDB", category: "VectorStore", attributes: {}, created_at: "" },
  ]

  const edges: RelationEdge[] = graphData?.edges || [
    { id: 1, subject_id: 1, object_id: 2, relation: "INCLUDES", confidence: 1.0 },
    { id: 2, subject_id: 1, object_id: 3, relation: "USES", confidence: 1.0 },
    { id: 3, subject_id: 2, object_id: 4, relation: "INDEXES_INTO", confidence: 1.0 },
  ]

  const [selectedNodeId, setSelectedNodeId] = useState<number | null>(1)
  const [showAddModal, setShowAddModal] = useState(false)
  const [subjectName, setSubjectName] = useState("")
  const [predicate, setPredicate] = useState("")
  const [objectName, setObjectName] = useState("")
  const [formError, setFormError] = useState<string | null>(null)

  const selectedNode = nodes.find((n) => n.id === selectedNodeId) || nodes[0]

  const handleAddRelation = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!subjectName || !predicate || !objectName) return
    setFormError(null)
    try {
      await addRelationApi({
        subject_name: subjectName,
        predicate: predicate,
        object_name: objectName,
      })
      queryClient.invalidateQueries({ queryKey: queryKeys.memory.graph() })
      setSubjectName("")
      setPredicate("")
      setObjectName("")
      setShowAddModal(false)
    } catch (err: unknown) {
      setFormError(err instanceof Error ? err.message : "Failed to add triple")
    }
  }

  return (
    <div className="space-y-4 bg-secondary/15 border border-border/40 rounded-xl p-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border/40 pb-3">
        <div className="flex items-center gap-2">
          <Share2 className="h-4 w-4 text-cyan-400" />
          <h3 className="text-xs font-bold text-foreground">Semantic Memory Entity-Relation Knowledge Graph</h3>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-1.5 px-3 py-1 text-xs font-bold font-mono rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 hover:bg-cyan-500/30 cursor-pointer transition-all"
        >
          <Plus className="h-3.5 w-3.5" />
          Add Entity Relation
        </button>
      </div>

      {/* Graph Visualizer Map */}
      <div className="p-6 bg-[#0D1117] border border-border/40 rounded-xl space-y-6">
        <div className="flex flex-wrap items-center justify-center gap-4">
          {nodes.map((node) => {
            const isSelected = selectedNodeId === node.id
            return (
              <button
                key={node.id}
                onClick={() => setSelectedNodeId(node.id)}
                className={`p-3 rounded-xl border flex items-center gap-2 cursor-pointer transition-all ${
                  isSelected
                    ? "bg-cyan-500/20 text-cyan-300 border-cyan-500 shadow-md font-bold scale-105"
                    : "bg-secondary/20 text-foreground border-border/40 hover:bg-secondary/40"
                }`}
              >
                {node.category === "System" && <Cpu className="h-4 w-4 text-cyan-400" />}
                {node.category === "VectorStore" && <Database className="h-4 w-4 text-emerald-400" />}
                {node.category === "Orchestrator" && <Brain className="h-4 w-4 text-amber-400" />}
                {node.category !== "System" && node.category !== "VectorStore" && node.category !== "Orchestrator" && (
                  <Server className="h-4 w-4 text-violet-400" />
                )}
                <span className="text-xs font-mono">{node.name}</span>
              </button>
            )
          })}
        </div>

        {/* Triple Relation List */}
        <div className="pt-4 border-t border-border/30 space-y-2 font-mono text-xs">
          <span className="text-muted-foreground uppercase text-[10px] font-bold">Recorded Graph Triples</span>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {edges.map((edge) => {
              const sub = nodes.find((n) => n.id === edge.subject_id)?.name || `Entity_${edge.subject_id}`
              const obj = nodes.find((n) => n.id === edge.object_id)?.name || `Entity_${edge.object_id}`
              return (
                <div key={edge.id} className="p-2.5 bg-secondary/20 rounded-lg border border-border/30 text-[11px] flex items-center justify-between">
                  <span className="text-cyan-400 font-bold">{sub}</span>
                  <span className="text-muted-foreground italic text-[10px]">-- ({edge.relation}) --&gt;</span>
                  <span className="text-emerald-400 font-bold">{obj}</span>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Selected Node Properties */}
      {selectedNode && (
        <div className="p-4 bg-secondary/20 border border-border/40 rounded-xl space-y-2 font-mono text-xs">
          <span className="text-[10px] text-muted-foreground uppercase font-bold">Selected Entity Properties</span>
          <div className="grid grid-cols-3 gap-2">
            <div><span className="text-muted-foreground text-[10px]">Name:</span> <span className="text-cyan-300 font-bold">{selectedNode.name}</span></div>
            <div><span className="text-muted-foreground text-[10px]">Category:</span> <span className="text-emerald-300">{selectedNode.category}</span></div>
            <div><span className="text-muted-foreground text-[10px]">Entity ID:</span> <span className="text-foreground">#{selectedNode.id}</span></div>
          </div>
        </div>
      )}

      {/* Add Relation Triple Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0D1117] border border-border/50 rounded-xl p-5 max-w-md w-full space-y-4">
            <h3 className="text-xs font-bold font-mono text-foreground uppercase">Add Entity Relation Triple</h3>
            {formError && (
              <div className="p-2 bg-red-500/10 border border-red-500/30 rounded text-xs text-red-400 font-mono">
                {formError}
              </div>
            )}
            <form onSubmit={handleAddRelation} className="space-y-3 font-mono text-xs">
              <div>
                <label className="text-[10px] text-muted-foreground block mb-1">Subject Entity</label>
                <input
                  type="text"
                  value={subjectName}
                  onChange={(e) => setSubjectName(e.target.value)}
                  placeholder="e.g. Memory_Studio"
                  className="w-full p-2 rounded bg-secondary/30 border border-border/40 text-foreground"
                />
              </div>
              <div>
                <label className="text-[10px] text-muted-foreground block mb-1">Predicate / Relation</label>
                <input
                  type="text"
                  value={predicate}
                  onChange={(e) => setPredicate(e.target.value)}
                  placeholder="e.g. COMPRESSES"
                  className="w-full p-2 rounded bg-secondary/30 border border-border/40 text-foreground"
                />
              </div>
              <div>
                <label className="text-[10px] text-muted-foreground block mb-1">Object Entity</label>
                <input
                  type="text"
                  value={objectName}
                  onChange={(e) => setObjectName(e.target.value)}
                  placeholder="e.g. Conversation_History"
                  className="w-full p-2 rounded bg-secondary/30 border border-border/40 text-foreground"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-3 py-1.5 rounded bg-secondary/40 text-muted-foreground hover:text-foreground"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-3 py-1.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold"
                >
                  Save Triple
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
