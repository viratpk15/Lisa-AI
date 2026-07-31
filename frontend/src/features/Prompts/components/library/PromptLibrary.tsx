import { Star, Search, Plus, Sparkles, FileText, ChevronRight } from "lucide-react"
import { usePromptStudioStore } from "../../store/usePromptStudioStore"
import { usePromptsQuery } from "../../services/promptsApi"

export function PromptLibrary() {
  const selectedPromptId = usePromptStudioStore((s) => s.selectedPromptId)
  const setSelectedPromptId = usePromptStudioStore((s) => s.setSelectedPromptId)
  const searchQuery = usePromptStudioStore((s) => s.searchQuery)
  const setSearchQuery = usePromptStudioStore((s) => s.setSearchQuery)
  const selectedFolderId = usePromptStudioStore((s) => s.selectedFolderId)
  const setSelectedFolderId = usePromptStudioStore((s) => s.setSelectedFolderId)
  const setActiveTab = usePromptStudioStore((s) => s.setActiveTab)

  const { data: prompts = [], isLoading } = usePromptsQuery(selectedFolderId, null, searchQuery)

  return (
    <div className="space-y-4">
      {/* Search & Actions Header */}
      <div className="space-y-2">
        <div className="relative flex items-center w-full">
          <Search className="absolute left-3 h-4 w-4 text-muted-foreground pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search prompts by title or tag..."
            className="w-full pl-9 pr-3 py-2 text-xs bg-secondary/30 border border-border/50 rounded-lg text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 transition-all"
          />
        </div>

        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none text-xs">
            <button
              onClick={() => setSelectedFolderId(null)}
              className={`px-2.5 py-1 text-[11px] font-medium rounded-full cursor-pointer transition-all ${
                selectedFolderId === null
                  ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/40"
                  : "bg-secondary/40 text-muted-foreground border border-border/40 hover:text-foreground"
              }`}
            >
              All Prompts
            </button>
            <button
              onClick={() => setActiveTab("templates")}
              className="px-2.5 py-1 text-[11px] font-semibold rounded-full bg-violet-500/20 text-violet-300 border border-violet-500/40 hover:bg-violet-500/30 cursor-pointer transition-all flex items-center gap-1"
            >
              <Sparkles className="h-3 w-3" />
              Templates
            </button>
          </div>

          <button
            onClick={() => {
              setSelectedPromptId(null)
              setActiveTab("editor")
            }}
            className="p-1.5 bg-cyan-500 hover:bg-cyan-400 text-black rounded-lg cursor-pointer transition-all"
            title="New Prompt"
          >
            <Plus className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Prompt Card List */}
      {isLoading ? (
        <div className="p-4 text-center text-xs text-muted-foreground animate-pulse">Loading prompt library...</div>
      ) : prompts.length === 0 ? (
        <div className="p-6 text-center text-xs text-muted-foreground bg-secondary/10 border border-dashed border-border/40 rounded-xl">
          No prompts matched search.
        </div>
      ) : (
        <div className="space-y-2 max-h-125 overflow-y-auto scrollbar-thin">
          {prompts.map((p) => {
            const isSelected = selectedPromptId === p.id
            return (
              <div
                key={p.id}
                onClick={() => {
                  setSelectedPromptId(p.id)
                  setActiveTab("editor")
                }}
                className={`p-3 rounded-xl border transition-all cursor-pointer group flex items-start justify-between ${
                  isSelected
                    ? "bg-cyan-500/10 border-cyan-500/50 shadow-md ring-1 ring-cyan-500/30"
                    : "bg-secondary/20 border-border/40 hover:border-cyan-500/30 hover:bg-secondary/40"
                }`}
              >
                <div className="space-y-1 pr-2">
                  <div className="flex items-center gap-1.5">
                    {p.is_favorite && <Star className="h-3 w-3 text-amber-400 fill-current shrink-0" />}
                    <FileText className="h-3.5 w-3.5 text-cyan-400 shrink-0" />
                    <h4 className="text-xs font-bold text-foreground group-hover:text-cyan-400 transition-colors line-clamp-1">
                      {p.title}
                    </h4>
                  </div>
                  <p className="text-[11px] text-muted-foreground leading-relaxed line-clamp-1">
                    {p.description || "No description provided."}
                  </p>

                  {p.tags && p.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 pt-1">
                      {p.tags.map((t) => (
                        <span key={t} className="px-1.5 py-0.2 text-[9px] font-mono bg-secondary/50 border border-border/40 rounded text-muted-foreground">
                          #{t}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <ChevronRight className={`h-4 w-4 text-muted-foreground shrink-0 transition-transform ${isSelected ? "text-cyan-400 translate-x-0.5" : "group-hover:translate-x-0.5"}`} />
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
