import { useState } from "react"
import { Search, Pin, Trash2, MessageSquare, Plus } from "lucide-react"
import { Badge } from "@/components/ui/badge"

interface Conversation {
  id: string
  title: string
  preview: string
  time: string
  pinned: boolean
  model: string
  unread: boolean
  group: "Today" | "Yesterday" | "Last Week" | "Older"
}

interface SidebarProps {
  conversations: Conversation[]
  selectedId: string | null
  onSelect: (id: string) => void
  onNewChat: () => void
  onTogglePin: (id: string, e: React.MouseEvent) => void
  onDelete: (id: string, e: React.MouseEvent) => void
}

export const Sidebar: React.FC<SidebarProps> = ({
  conversations,
  selectedId,
  onSelect,
  onNewChat,
  onTogglePin,
  onDelete
}) => {
  const [search, setSearch] = useState("")

  const filtered = conversations.filter(
    (c) =>
      c.title.toLowerCase().includes(search.toLowerCase()) ||
      c.preview.toLowerCase().includes(search.toLowerCase())
  )

  // Grouping structure
  const groups: { [key: string]: Conversation[] } = {
    Today: [],
    Yesterday: [],
    "Last Week": [],
    Older: []
  }

  filtered.forEach((c) => {
    const grp = c.group && groups[c.group] ? c.group : "Today"
    groups[grp].push(c)
  })

  return (
    <div className="w-full h-full border-r border-border/80 bg-sidebar flex flex-col overflow-hidden select-none">
      {/* Header action */}
      <div className="p-3 border-b border-border/80 flex items-center justify-between gap-3 shrink-0">
        <span className="font-bold text-xs uppercase tracking-wider text-muted-foreground font-mono">
          Conversations
        </span>
        <button
          onClick={onNewChat}
          className="p-1.5 rounded-lg border border-primary/25 bg-primary/10 hover:bg-primary text-foreground hover:text-primary-foreground transition-all cursor-pointer focus:outline-none focus:ring-1 focus:ring-primary shrink-0"
          title="New session"
        >
          <Plus className="h-4 w-4" />
        </button>
      </div>

      {/* Filter search box */}
      <div className="px-3 py-2 border-b border-border/60 shrink-0">
        <div className="relative">
          <Search className="absolute left-2.5 top-2 h-3.5 w-3.5 text-muted-foreground/60" />
          <input
            type="text"
            placeholder="Search conversations..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-8 pr-3 py-1.5 w-full bg-secondary/25 border border-border/60 hover:border-primary/20 rounded-lg text-xs text-foreground outline-none focus:ring-1 focus:ring-primary placeholder:text-muted-foreground/50 transition-colors"
          />
        </div>
      </div>

      {/* Lists feed grouped */}
      <div className="flex-1 overflow-y-auto p-2 space-y-4">
        {Object.entries(groups).map(([groupName, items]) => {
          if (items.length === 0) return null

          return (
            <div key={groupName} className="space-y-1">
              <h3 className="px-2 py-1 text-[9px] font-mono font-semibold tracking-wider text-muted-foreground uppercase">
                {groupName}
              </h3>
              <div className="space-y-0.5">
                {items.map((chat) => {
                  const isSelected = selectedId === chat.id
                  return (
                    <div
                      key={chat.id}
                      onClick={() => onSelect(chat.id)}
                      className={`w-full text-left p-2.5 rounded-lg flex items-start gap-2.5 transition-all cursor-pointer group relative ${isSelected ? "bg-primary text-primary-foreground shadow-sm" : "hover:bg-secondary/40 text-muted-foreground hover:text-foreground"}`}
                    >
                      {/* Unread dot */}
                      {chat.unread && !isSelected && (
                        <span className="absolute left-1.5 top-3.75 h-1.5 w-1.5 rounded-full bg-primary" />
                      )}

                      <div className="pt-0.5 shrink-0">
                        <MessageSquare className={`h-4 w-4 ${isSelected ? "text-primary-foreground" : "text-primary/70 group-hover:text-primary"}`} />
                      </div>

                      <div className="flex-1 min-w-0 pr-8 space-y-1">
                        <div className="flex items-center justify-between gap-1.5">
                          <span className={`font-bold text-xs truncate leading-tight ${isSelected ? "text-primary-foreground" : "text-foreground"}`}>
                            {chat.title}
                          </span>
                        </div>
                        <p className={`text-[10px] truncate leading-normal ${isSelected ? "text-primary-foreground/80" : "text-muted-foreground"}`}>
                          {chat.preview}
                        </p>
                        
                        <div className="flex items-center gap-1.5 flex-wrap pt-0.5 select-none">
                          <span className={`text-[9px] font-mono ${isSelected ? "text-primary-foreground/75" : "text-muted-foreground/80"}`}>
                            {chat.time}
                          </span>
                          <Badge variant="outline" className={`text-[8px] font-mono px-1 py-0 border-0 ${isSelected ? "bg-primary-foreground/20 text-primary-foreground" : "bg-secondary/60 text-muted-foreground/85"}`}>
                            {chat.model.split(" ")[0]}
                          </Badge>
                        </div>
                      </div>

                      {/* Hover action overlay */}
                      <div className="absolute right-2 top-3.25 opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1">
                        <button
                          onClick={(e) => onTogglePin(chat.id, e)}
                          className={`p-1 rounded hover:bg-secondary/20 cursor-pointer focus:outline-none transition-colors ${chat.pinned ? "text-primary-foreground" : "text-muted-foreground/60 hover:text-foreground"}`}
                          title={chat.pinned ? "Unpin thread" : "Pin thread"}
                        >
                          <Pin className={`h-3 w-3 ${chat.pinned ? "fill-current rotate-45" : ""}`} />
                        </button>
                        <button
                          onClick={(e) => onDelete(chat.id, e)}
                          className="p-1 rounded hover:bg-secondary/20 text-muted-foreground/60 hover:text-destructive cursor-pointer focus:outline-none transition-colors"
                          title="Delete thread"
                        >
                          <Trash2 className="h-3 w-3" />
                        </button>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )
        })}

        {filtered.length === 0 && (
          <div className="py-8 text-center text-xs text-muted-foreground">
            No conversations found.
          </div>
        )}
      </div>
    </div>
  )
}
