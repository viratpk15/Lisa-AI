import React, { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Search, X, MessageSquare, ArrowRight, ArrowLeft } from "lucide-react"
import { searchConversationsApi } from "@/services/api/chat"
import type { Conversation } from "@/types/api"

interface SearchModalProps {
  isOpen: boolean
  onClose: () => void
  onSelectConversation: (sessionId: string) => void
}

export const SearchModal: React.FC<SearchModalProps> = ({
  isOpen,
  onClose,
  onSelectConversation,
}) => {
  const [query, setQuery] = useState("")
  const [results, setResults] = useState<Conversation[]>([])
  const [isLoading, setIsLoading] = useState(false)

  // Escape key handler to return to chat
  useEffect(() => {
    if (!isOpen) return
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault()
        onClose()
      }
    }
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [isOpen, onClose])

  // Real-time search execution with debouncing
  useEffect(() => {
    if (!query.trim()) {
      setResults([])
      setIsLoading(false)
      return
    }

    const timer = setTimeout(async () => {
      setIsLoading(true)
      try {
        const data = await searchConversationsApi(query.trim())
        setResults(data)
      } catch (err) {
        console.error("Search failed:", err)
      } finally {
        setIsLoading(false)
      }
    }, 200)

    return () => clearTimeout(timer)
  }, [query])

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <div
        onClick={onClose}
        className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4 bg-black/60 backdrop-blur-sm cursor-pointer"
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: -10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: -10 }}
          onClick={(e) => e.stopPropagation()}
          className="w-full max-w-xl bg-background border border-border/80 rounded-xl shadow-2xl overflow-hidden flex flex-col cursor-default"
        >
          {/* Search Header */}
          <div className="flex items-center px-4 py-3 border-b border-border/60 gap-3">
            <button
              onClick={onClose}
              className="p-1 rounded-md hover:bg-secondary text-muted-foreground hover:text-foreground cursor-pointer flex items-center gap-1 text-xs font-medium transition-colors"
              title="Back to Assistant Chat"
            >
              <ArrowLeft className="h-4 w-4" />
              <span className="hidden sm:inline">Back</span>
            </button>
            <div className="h-4 w-px bg-border/60" />
            <Search className="h-4 w-4 text-muted-foreground shrink-0" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search conversation titles or message contents..."
              className="flex-1 bg-transparent text-sm text-foreground outline-none placeholder:text-muted-foreground/60 font-medium"
              autoFocus
            />
            {query && (
              <button
                onClick={() => setQuery("")}
                className="p-1 text-muted-foreground hover:text-foreground cursor-pointer"
                title="Clear query"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            )}
            <button
              onClick={onClose}
              className="text-[10px] font-mono bg-secondary/50 hover:bg-secondary px-2 py-1 rounded text-muted-foreground hover:text-foreground border border-border/40 cursor-pointer flex items-center gap-1"
              title="Close search (ESC)"
            >
              <span>ESC</span>
              <X className="h-3 w-3" />
            </button>
          </div>

          {/* Results List */}
          <div className="max-h-96 overflow-y-auto p-2 divide-y divide-border/20">
            {isLoading ? (
              <div className="p-8 text-center text-xs font-mono text-muted-foreground flex items-center justify-center gap-2">
                <span className="animate-spin text-primary">⚡</span> Searching conversations...
              </div>
            ) : results.length > 0 ? (
              results.map((conv) => (
                <button
                  key={conv.id}
                  onClick={() => {
                    onSelectConversation(conv.id)
                    onClose()
                  }}
                  className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-secondary/40 text-left transition-colors group cursor-pointer"
                >
                  <div className="flex items-start gap-3 min-w-0">
                    <MessageSquare className="h-4 w-4 text-primary shrink-0 mt-0.5" />
                    <div className="min-w-0">
                      <h4 className="text-xs font-bold text-foreground group-hover:text-primary transition-colors truncate">
                        {conv.title}
                      </h4>
                      {conv.preview && (
                        <p className="text-[11px] text-muted-foreground truncate mt-0.5">
                          {conv.preview}
                        </p>
                      )}
                    </div>
                  </div>
                  <ArrowRight className="h-3.5 w-3.5 text-muted-foreground/40 group-hover:text-primary opacity-0 group-hover:opacity-100 transition-all shrink-0 ml-2" />
                </button>
              ))
            ) : query.trim() ? (
              <div className="p-8 text-center text-xs font-mono text-muted-foreground">
                No matching conversations found for "{query}"
              </div>
            ) : (
              <div className="p-8 text-center text-xs font-mono text-muted-foreground/60">
                Type to search conversation titles or contents across your history...
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}
