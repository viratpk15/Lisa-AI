import React, { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Search, X, MessageSquare, ArrowRight } from "lucide-react"
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
      <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4 bg-black/60 backdrop-blur-sm">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: -10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: -10 }}
          className="w-full max-w-xl bg-background border border-border/80 rounded-xl shadow-2xl overflow-hidden flex flex-col"
        >
          {/* Search Header */}
          <div className="flex items-center px-4 py-3 border-b border-border/60 gap-3">
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
              >
                <X className="h-3.5 w-3.5" />
              </button>
            )}
            <kbd className="text-[10px] font-mono bg-secondary/40 px-1.5 py-0.5 rounded text-muted-foreground border border-border/40">ESC</kbd>
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
