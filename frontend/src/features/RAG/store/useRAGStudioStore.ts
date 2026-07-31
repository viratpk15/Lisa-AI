import { create } from "zustand"
import type { RetrievedChunk } from "../types/rag.types"

export type RAGStudioTab = "datasets" | "documents" | "chunks" | "playground" | "hybrid" | "eval" | "analytics" | "graph"

interface RAGStudioStore {
  activeTab: RAGStudioTab
  setActiveTab: (tab: RAGStudioTab) => void

  selectedKbId: string | null
  setSelectedKbId: (id: string | null) => void

  selectedDatasetId: string | null
  setSelectedDatasetId: (id: string | null) => void

  selectedDocId: string | null
  setSelectedDocId: (id: string | null) => void

  // Chunking params
  chunkSize: number
  chunkOverlap: number
  chunkStrategy: "fixed" | "semantic" | "recursive"
  setChunkParams: (size: number, overlap: number, strategy: "fixed" | "semantic" | "recursive") => void

  // Hybrid Search params
  queryText: string
  setQueryText: (q: string) => void
  topK: number
  setTopK: (k: number) => void
  hybridAlpha: number // 0.0 (BM25) to 1.0 (Dense Vector)
  setHybridAlpha: (alpha: number) => void
  useReranker: boolean
  setUseReranker: (v: boolean) => void

  // Search Results
  searchResults: RetrievedChunk[]
  setSearchResults: (results: RetrievedChunk[]) => void
  isSearching: boolean
  setIsSearching: (v: boolean) => void
}

export const useRAGStudioStore = create<RAGStudioStore>((set) => ({
  activeTab: "datasets",
  setActiveTab: (tab) => set({ activeTab: tab }),

  selectedKbId: "kb_enterprise_01",
  setSelectedKbId: (id) => set({ selectedKbId: id }),

  selectedDatasetId: "ds_core_docs",
  setSelectedDatasetId: (id) => set({ selectedDatasetId: id }),

  selectedDocId: "doc_arch_01",
  setSelectedDocId: (id) => set({ selectedDocId: id }),

  chunkSize: 512,
  chunkOverlap: 50,
  chunkStrategy: "recursive",
  setChunkParams: (chunkSize, chunkOverlap, chunkStrategy) => set({ chunkSize, chunkOverlap, chunkStrategy }),

  queryText: "How does Jarvis implement RAG vector retrieval?",
  setQueryText: (queryText) => set({ queryText }),
  topK: 5,
  setTopK: (topK) => set({ topK }),
  hybridAlpha: 0.50,
  setHybridAlpha: (hybridAlpha) => set({ hybridAlpha }),
  useReranker: true,
  setUseReranker: (useReranker) => set({ useReranker }),

  searchResults: [],
  setSearchResults: (searchResults) => set({ searchResults }),
  isSearching: false,
  setIsSearching: (isSearching) => set({ isSearching }),
}))
