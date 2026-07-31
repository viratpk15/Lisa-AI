import { useState } from "react"
import { FileText, Upload, HardDrive, CheckCircle2 } from "lucide-react"
import { useRAGStudioStore } from "../../store/useRAGStudioStore"
import { useDocumentsQuery, useIngestDocumentMutation } from "../../services/ragApi"

export function DocumentExplorer() {
  const selectedDatasetId = useRAGStudioStore((s) => s.selectedDatasetId)
  const { data: docs = [], refetch } = useDocumentsQuery(selectedDatasetId)
  const ingestDocument = useIngestDocumentMutation()

  const [filename, setFilename] = useState("")
  const [text, setText] = useState("")
  const [statusMsg, setStatusMsg] = useState<string | null>(null)

  const isUploading = ingestDocument.isPending

  const handleIngest = () => {
    if (!filename || !text || !selectedDatasetId) return
    ingestDocument.mutate(
      {
        dataset_id: selectedDatasetId,
        filename,
        file_type: filename.split(".").pop() || "txt",
        text,
      },
      {
        onSuccess: () => {
          setStatusMsg("Document ingested and vector indexed!")
          setFilename("")
          setText("")
          refetch()
          setTimeout(() => setStatusMsg(null), 2500)
        },
        onError: (err: Error) => {
          setStatusMsg(`Upload failed: ${err.message}`)
        },
      }
    )
  }

  return (
    <div className="space-y-4 bg-secondary/15 border border-border/40 rounded-xl p-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border/40 pb-3">
        <div className="flex items-center gap-2">
          <FileText className="h-4 w-4 text-cyan-400" />
          <h3 className="text-xs font-bold text-foreground">Multi-Format Document Explorer & Ingestion Pipeline</h3>
        </div>
        {statusMsg && <span className="text-xs font-mono text-emerald-400 font-semibold">{statusMsg}</span>}
      </div>

      {/* Upload Dropzone Form */}
      <div className="space-y-3 bg-secondary/20 p-3 rounded-lg border border-border/40 font-mono text-xs">
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={filename}
            onChange={(e) => setFilename(e.target.value)}
            placeholder="Filename (e.g. System_Design.md)"
            className="flex-1 px-3 py-1.5 text-xs bg-[#0D1117] border border-border/50 rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
          />
          <button
            onClick={handleIngest}
            disabled={isUploading || !filename || !text}
            className="inline-flex items-center gap-1.5 px-4 py-1.5 text-xs font-bold bg-cyan-500 hover:bg-cyan-400 text-black rounded-lg cursor-pointer transition-all disabled:opacity-50"
          >
            <Upload className="h-3.5 w-3.5" />
            {isUploading ? "Ingesting..." : "Ingest Document"}
          </button>
        </div>

        <textarea
          rows={3}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste raw markdown, text, or architecture code here to parse & chunk..."
          className="w-full p-2.5 text-xs font-mono bg-[#0D1117] border border-border/50 rounded-lg text-[#C9D1D9] focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
        />
      </div>

      {/* Ingested Document List */}
      <div className="space-y-2 font-mono text-xs">
        <span className="text-xs font-bold text-foreground flex items-center gap-1.5">
          <HardDrive className="h-3.5 w-3.5 text-cyan-400" /> Ingested Dataset Files ({docs.length})
        </span>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {docs.map((doc) => (
            <div key={doc.id} className="p-3 bg-[#0D1117] border border-border/40 rounded-xl space-y-2">
              <div className="flex items-center justify-between border-b border-border/40 pb-2">
                <span className="font-bold text-cyan-400 truncate">{doc.filename}</span>
                <span className="text-[10px] text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 className="h-3 w-3" /> Ingested
                </span>
              </div>

              <div className="flex items-center justify-between text-[10px] text-muted-foreground">
                <span>Type: {doc.file_type.toUpperCase()}</span>
                <span>Size: {(doc.file_size_bytes / 1024).toFixed(1)} KB</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
