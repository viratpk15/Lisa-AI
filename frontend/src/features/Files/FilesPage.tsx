import React, { useState, useRef, useEffect } from "react"
import { useNavigate } from "react-router"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import {
  FileText,
  Upload,
  Search,
  Bot,
  FolderOpen,
  ArrowRight,
  Clock,
  CheckCircle2,
  AlertCircle,
  X,
  FileCode,
  FileSpreadsheet,
  FileImage,
  RefreshCw,
  Sparkles
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { uploadDocument } from "@/services/api/files"
import { fetchDocuments, runHybridSearchApi } from "@/features/RAG/services/ragApi"
import { queryKeys } from "@/services/queries/queryKeys"
import type { Document, RetrievedChunk } from "@/features/RAG/types/rag.types"

function formatFileSize(bytes?: number): string {
  if (!bytes || bytes <= 0) return "—"
  const kb = bytes / 1024
  if (kb < 1024) return `${kb.toFixed(1)} KB`
  const mb = kb / 1024
  return `${mb.toFixed(1)} MB`
}

function getFileIcon(filename: string, fileType?: string) {
  const ext = filename.split(".").pop()?.toLowerCase() || fileType?.toLowerCase() || ""
  if (["pdf"].includes(ext)) return FileText
  if (["csv", "xlsx", "xls"].includes(ext)) return FileSpreadsheet
  if (["png", "jpg", "jpeg", "webp", "svg"].includes(ext)) return FileImage
  if (["ts", "tsx", "js", "jsx", "py", "json", "html", "css"].includes(ext)) return FileCode
  return FileText
}

export default function FilesPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [searchQuery, setSearchQuery] = useState("")
  const [debouncedQuery, setDebouncedQuery] = useState("")
  const [uploadStatus, setUploadStatus] = useState<"idle" | "uploading" | "success" | "error">("idle")
  const [uploadMessage, setUploadMessage] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<Document | null>(null)

  // Debounce search query
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(searchQuery.trim())
    }, 300)
    return () => clearTimeout(timer)
  }, [searchQuery])

  // Real Documents Query
  const {
    data: documents = [],
    isLoading: isDocsLoading,
    isError: isDocsError,
    refetch: refetchDocs
  } = useQuery({
    queryKey: queryKeys.rag.documents(null),
    queryFn: () => fetchDocuments(null),
  })

  // Real Hybrid Search Query when search input is non-empty
  const {
    data: searchResults,
    isLoading: isSearchLoading,
  } = useQuery({
    queryKey: ["files", "search", debouncedQuery],
    queryFn: async () => {
      if (!debouncedQuery) return null
      return runHybridSearchApi({
        query: debouncedQuery,
        top_k: 5,
        alpha: 0.5,
        use_reranker: true,
      })
    },
    enabled: debouncedQuery.length > 1,
  })

  // File Upload Mutation
  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      setUploadStatus("uploading")
      setUploadMessage(`Uploading ${file.name}...`)
      return uploadDocument(file)
    },
    onSuccess: (res) => {
      setUploadStatus("success")
      setUploadMessage(`"${res.name}" indexed and ready for Lisa.`)
      queryClient.invalidateQueries({ queryKey: queryKeys.rag.documents(null) })
      setTimeout(() => {
        setUploadStatus("idle")
        setUploadMessage(null)
      }, 5000)
    },
    onError: (err: Error) => {
      setUploadStatus("error")
      setUploadMessage(`Upload failed: ${err.message || "Could not process document."}`)
    },
  })

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      uploadMutation.mutate(files[0])
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const handleAskLisaAboutFile = (doc: Document) => {
    navigate("/assistant", {
      state: {
        initialPrompt: `Can you summarize and explain the key points in "${doc.filename}"?`,
        activeDocumentId: doc.id,
        activeFilename: doc.filename,
      },
    })
  }

  const handleAskLisaAboutSearch = (result: RetrievedChunk) => {
    navigate("/assistant", {
      state: {
        initialPrompt: `Regarding "${result.raw_text.slice(0, 120)}...", can you provide more details?`,
      },
    })
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6 py-2">
      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        onChange={handleFileChange}
        className="hidden"
        accept=".pdf,.txt,.md,.markdown,.docx,.doc,.csv,.json,.py,.ts,.tsx,.js"
      />

      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Files</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Search, upload, and organize documents for Lisa to reference in your conversations.
          </p>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <Button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploadMutation.isPending}
            className="cursor-pointer gap-2 font-medium"
          >
            <Upload className="h-4 w-4" />
            <span>{uploadMutation.isPending ? "Uploading..." : "Upload File"}</span>
          </Button>
        </div>
      </div>

      {/* Upload Status Alert Notification */}
      {uploadMessage && (
        <div
          className={`p-3.5 rounded-xl border flex items-center justify-between gap-3 text-xs ${
            uploadStatus === "uploading"
              ? "bg-primary/10 border-primary/30 text-primary"
              : uploadStatus === "success"
              ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
              : "bg-rose-500/10 border-rose-500/30 text-rose-400"
          }`}
        >
          <div className="flex items-center gap-2 min-w-0">
            {uploadStatus === "uploading" && <RefreshCw className="h-4 w-4 animate-spin shrink-0" />}
            {uploadStatus === "success" && <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-400" />}
            {uploadStatus === "error" && <AlertCircle className="h-4 w-4 shrink-0 text-rose-400" />}
            <span className="truncate">{uploadMessage}</span>
          </div>
          <button
            onClick={() => setUploadMessage(null)}
            className="text-muted-foreground hover:text-foreground cursor-pointer"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* Search Input Bar */}
      <div className="relative">
        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search your files and indexed passages..."
          className="w-full pl-10 pr-10 py-2.5 bg-card/60 border border-border/70 rounded-xl text-sm text-foreground placeholder:text-muted-foreground outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all shadow-xs"
        />
        {searchQuery && (
          <button
            onClick={() => setSearchQuery("")}
            className="absolute right-3.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground cursor-pointer"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Live Search Results View (rendered when searching) */}
      {debouncedQuery.length > 1 && (
        <Card className="border-border/70 bg-card/50 shadow-xs">
          <CardHeader className="pb-3 flex flex-row items-center justify-between">
            <div className="space-y-0.5">
              <CardTitle className="text-base font-semibold">Search Results</CardTitle>
              <CardDescription>Matching passages for "{debouncedQuery}"</CardDescription>
            </div>
            {isSearchLoading && (
              <div className="flex items-center gap-1.5 text-xs text-muted-foreground font-mono">
                <RefreshCw className="h-3.5 w-3.5 animate-spin text-primary" />
                <span>Searching...</span>
              </div>
            )}
          </CardHeader>
          <CardContent>
            {isSearchLoading ? (
              <div className="py-8 space-y-3">
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-3 w-full" />
                <Skeleton className="h-3 w-5/6" />
              </div>
            ) : searchResults?.results && searchResults.results.length > 0 ? (
              <div className="divide-y divide-border/40">
                {searchResults.results.map((item, idx) => (
                  <div key={idx} className="py-3.5 space-y-2 first:pt-0 last:pb-0">
                    <p className="text-xs text-foreground/90 leading-relaxed bg-secondary/20 p-3 rounded-lg border border-border/40">
                      "{item.raw_text}"
                    </p>
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-[10px] font-mono text-muted-foreground">
                        Document reference ID: {item.document_id}
                      </span>
                      <Button
                        size="xs"
                        variant="ghost"
                        onClick={() => handleAskLisaAboutSearch(item)}
                        className="text-xs text-primary hover:text-primary gap-1 cursor-pointer"
                      >
                        <Bot className="h-3.5 w-3.5" />
                        <span>Ask Lisa</span>
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-8 text-center text-xs text-muted-foreground">
                No matching passages found for "{debouncedQuery}".
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Main Files Table Card */}
      <Card className="border-border/70 bg-card/50 shadow-xs">
        <CardHeader className="flex flex-row items-center justify-between pb-3">
          <div>
            <CardTitle className="text-base font-semibold">Your files</CardTitle>
            <CardDescription>Knowledge documents currently indexed for conversation retrieval.</CardDescription>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => refetchDocs()}
            className="text-xs text-muted-foreground hover:text-foreground cursor-pointer gap-1.5"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            <span>Refresh</span>
          </Button>
        </CardHeader>
        <CardContent className="p-0">
          {isDocsLoading ? (
            <div className="p-6 space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex items-center justify-between py-2 border-b border-border/30">
                  <div className="flex items-center gap-3 w-1/2">
                    <Skeleton className="h-8 w-8 rounded-lg" />
                    <div className="space-y-1 w-full">
                      <Skeleton className="h-3.5 w-3/4" />
                      <Skeleton className="h-3 w-1/4" />
                    </div>
                  </div>
                  <Skeleton className="h-6 w-20" />
                </div>
              ))}
            </div>
          ) : isDocsError ? (
            <div className="p-8 text-center space-y-3">
              <AlertCircle className="h-6 w-6 text-destructive mx-auto" />
              <p className="text-sm font-medium text-foreground">Could not load files</p>
              <p className="text-xs text-muted-foreground max-w-sm mx-auto">
                Unable to reach the document registry. Please check backend connection and retry.
              </p>
              <Button size="sm" variant="outline" onClick={() => refetchDocs()} className="cursor-pointer">
                Retry
              </Button>
            </div>
          ) : documents.length === 0 ? (
            <div className="py-16 text-center space-y-3">
              <div className="p-3 rounded-full bg-secondary/50 border border-border/40 w-fit mx-auto text-muted-foreground">
                <FolderOpen className="h-6 w-6" />
              </div>
              <div className="space-y-1">
                <p className="text-sm font-semibold text-foreground">No files yet</p>
                <p className="text-xs text-muted-foreground max-w-sm mx-auto">
                  Upload a file and Lisa can help you search, summarize, and understand it.
                </p>
              </div>
              <Button
                size="sm"
                onClick={() => fileInputRef.current?.click()}
                className="cursor-pointer gap-1.5 text-xs font-medium"
              >
                <Upload className="h-3.5 w-3.5" />
                Upload a file
              </Button>
            </div>
          ) : (
            <div className="divide-y divide-border/40 font-mono text-xs">
              {documents.map((doc) => {
                const Icon = getFileIcon(doc.filename, doc.file_type)
                const isSelected = selectedFile?.id === doc.id

                return (
                  <div
                    key={doc.id}
                    onClick={() => setSelectedFile(isSelected ? null : doc)}
                    className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-secondary/20 transition-colors cursor-pointer"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="p-2 rounded-lg bg-primary/10 text-primary shrink-0">
                        <Icon className="h-4 w-4" />
                      </div>
                      <div className="min-w-0">
                        <p className="text-xs font-semibold text-foreground truncate font-sans">
                          {doc.filename}
                        </p>
                        <div className="flex items-center gap-3 text-[11px] text-muted-foreground mt-0.5">
                          <span className="uppercase">{doc.file_type}</span>
                          <span>•</span>
                          <span>{formatFileSize(doc.file_size_bytes)}</span>
                          <span>•</span>
                          <span className="flex items-center gap-1 font-sans">
                            <Clock className="h-3 w-3" />
                            {new Date(doc.ingested_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 self-end sm:self-center shrink-0">
                      <span className="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20 flex items-center gap-1">
                        <CheckCircle2 className="h-3 w-3" /> Ready
                      </span>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleAskLisaAboutFile(doc)
                        }}
                        className="h-7 text-xs font-medium gap-1.5 cursor-pointer text-primary hover:text-primary"
                      >
                        <Bot className="h-3.5 w-3.5" />
                        <span>Ask Lisa</span>
                      </Button>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Selected File Detail Card (Modal/Drawer expansion) */}
      {selectedFile && (
        <Card className="border-border/70 bg-card/60 shadow-xs">
          <CardHeader className="flex flex-row items-center justify-between pb-3">
            <div className="space-y-0.5">
              <CardTitle className="text-sm font-semibold flex items-center gap-2">
                <FileText className="h-4 w-4 text-primary" />
                <span>{selectedFile.filename}</span>
              </CardTitle>
              <CardDescription>File details and cognitive knowledge context</CardDescription>
            </div>
            <button
              onClick={() => setSelectedFile(null)}
              className="text-muted-foreground hover:text-foreground cursor-pointer"
            >
              <X className="h-4 w-4" />
            </button>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
              <div className="p-3 rounded-lg bg-secondary/30 border border-border/40">
                <span className="text-[10px] text-muted-foreground uppercase">Format</span>
                <p className="font-semibold text-foreground mt-0.5 uppercase">{selectedFile.file_type}</p>
              </div>
              <div className="p-3 rounded-lg bg-secondary/30 border border-border/40">
                <span className="text-[10px] text-muted-foreground uppercase">Size</span>
                <p className="font-semibold text-foreground mt-0.5">{formatFileSize(selectedFile.file_size_bytes)}</p>
              </div>
              <div className="p-3 rounded-lg bg-secondary/30 border border-border/40">
                <span className="text-[10px] text-muted-foreground uppercase">Status</span>
                <p className="font-semibold text-emerald-400 mt-0.5">Indexed</p>
              </div>
              <div className="p-3 rounded-lg bg-secondary/30 border border-border/40">
                <span className="text-[10px] text-muted-foreground uppercase">Added</span>
                <p className="font-semibold text-foreground mt-0.5">{new Date(selectedFile.ingested_at).toLocaleDateString()}</p>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-border/40">
              <Button
                size="sm"
                onClick={() => handleAskLisaAboutFile(selectedFile)}
                className="gap-1.5 cursor-pointer text-xs font-medium"
              >
                <Bot className="h-3.5 w-3.5" />
                <span>Ask Lisa about this file</span>
                <ArrowRight className="h-3 w-3" />
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Bottom CTA Card */}
      <Card className="border-border/60 bg-secondary/20 shadow-xs">
        <CardContent className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-0.5">
            <p className="text-xs font-semibold text-foreground flex items-center gap-1.5">
              <Sparkles className="h-3.5 w-3.5 text-primary" />
              <span>Ask Lisa about your files</span>
            </p>
            <p className="text-xs text-muted-foreground">
              Lisa can synthesize information across your documents, extract insights, and answer questions.
            </p>
          </div>
          <Button
            size="sm"
            variant="outline"
            onClick={() => navigate("/assistant")}
            className="text-xs font-medium gap-1.5 shrink-0 cursor-pointer self-start sm:self-auto"
          >
            <span>Open Assistant</span>
            <ArrowRight className="h-3 w-3" />
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
