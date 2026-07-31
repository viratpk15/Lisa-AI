import { Database, Folder, FileText, Plus, Server } from "lucide-react"
import { useRAGStudioStore } from "../../store/useRAGStudioStore"
import { useKnowledgeBasesQuery, useDatasetsQuery, useDocumentsQuery } from "../../services/ragApi"

export function DatasetLibrary() {
  const selectedKbId = useRAGStudioStore((s) => s.selectedKbId)
  const setSelectedKbId = useRAGStudioStore((s) => s.setSelectedKbId)
  const selectedDatasetId = useRAGStudioStore((s) => s.selectedDatasetId)
  const setSelectedDatasetId = useRAGStudioStore((s) => s.setSelectedDatasetId)
  const setSelectedDocId = useRAGStudioStore((s) => s.setSelectedDocId)

  const { data: kbs = [] } = useKnowledgeBasesQuery()
  const { data: datasets = [] } = useDatasetsQuery(selectedKbId)
  const { data: docs = [] } = useDocumentsQuery(selectedDatasetId)

  return (
    <div className="space-y-4 bg-secondary/15 border border-border/40 rounded-xl p-4 h-full flex flex-col justify-between">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border/40 pb-3">
          <div className="flex items-center gap-2">
            <Database className="h-4 w-4 text-cyan-400" />
            <h3 className="text-xs font-bold text-foreground">Knowledge Base Datasets</h3>
          </div>
          <button className="p-1 text-cyan-400 hover:bg-cyan-500/10 rounded cursor-pointer transition-all">
            <Plus className="h-4 w-4" />
          </button>
        </div>

        {/* KB Selection Selector */}
        <div className="space-y-1.5">
          <label className="text-[10px] font-mono text-muted-foreground uppercase flex items-center gap-1">
            <Server className="h-3 w-3 text-cyan-400" /> Target Knowledge Base
          </label>
          <select
            value={selectedKbId || ""}
            onChange={(e) => setSelectedKbId(e.target.value)}
            className="w-full px-2.5 py-1.5 text-xs font-mono bg-[#0D1117] border border-border/50 rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
          >
            {kbs.map((kb) => (
              <option key={kb.id} value={kb.id}>
                {kb.name}
              </option>
            ))}
          </select>
        </div>

        {/* Datasets Hierarchy List */}
        <div className="space-y-2">
          <span className="text-[10px] font-mono text-muted-foreground uppercase">Datasets ({datasets.length})</span>
          <div className="space-y-1">
            {datasets.map((ds) => {
              const isSelected = ds.id === selectedDatasetId
              return (
                <div
                  key={ds.id}
                  onClick={() => setSelectedDatasetId(ds.id)}
                  className={`p-2.5 rounded-lg border transition-all cursor-pointer space-y-1 ${
                    isSelected
                      ? "bg-cyan-500/10 border-cyan-500/50 shadow-xs"
                      : "bg-secondary/20 border-border/40 hover:bg-secondary/40"
                  }`}
                >
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="font-bold text-foreground flex items-center gap-1.5">
                      <Folder className="h-3.5 w-3.5 text-cyan-400" />
                      {ds.name}
                    </span>
                    <span className="px-1.5 py-0.2 text-[9px] font-bold bg-secondary/60 text-cyan-300 rounded border border-border/40">
                      {ds.document_count} docs
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Documents in Selected Dataset */}
        {selectedDatasetId && (
          <div className="space-y-2 pt-2 border-t border-border/40">
            <span className="text-[10px] font-mono text-muted-foreground uppercase">Documents ({docs.length})</span>
            <div className="space-y-1">
              {docs.map((doc) => (
                <div
                  key={doc.id}
                  onClick={() => setSelectedDocId(doc.id)}
                  className="p-2 bg-[#0D1117] border border-border/40 hover:border-cyan-500/40 rounded-lg text-xs font-mono text-foreground flex items-center justify-between cursor-pointer transition-all"
                >
                  <span className="flex items-center gap-1.5 font-medium truncate">
                    <FileText className="h-3.5 w-3.5 text-violet-400" />
                    {doc.filename}
                  </span>
                  <span className="text-[10px] text-muted-foreground uppercase">{doc.file_type}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="pt-3 border-t border-border/40 text-[10px] font-mono text-muted-foreground flex items-center justify-between">
        <span>Vector Store: ChromaDB HNSW</span>
        <span className="text-emerald-400 font-bold">Online</span>
      </div>
    </div>
  )
}
