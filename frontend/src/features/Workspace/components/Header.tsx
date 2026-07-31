import React, { useState } from "react"
import { Pin, Share2, Download, Trash2, Edit2, Check, Sparkles, Folder, Search } from "lucide-react"
import { Badge } from "@/components/ui/badge"

interface HeaderProps {
  title: string
  model: string
  scope: string
  pinned: boolean
  onTogglePin: () => void
  onRename: (newTitle: string) => void
  onDelete: () => void
  onExport: (format: "markdown" | "json") => void
  onOpenSearch?: () => void
}

export const Header: React.FC<HeaderProps> = ({
  title,
  model,
  scope,
  pinned,
  onTogglePin,
  onRename,
  onDelete,
  onExport,
  onOpenSearch
}) => {
  const [isEditing, setIsEditing] = useState(false)
  const [editedTitle, setEditedTitle] = useState(title)
  const [copiedLink, setCopiedLink] = useState(false)

  const handleSaveRename = () => {
    if (editedTitle.trim()) {
      onRename(editedTitle.trim())
    }
    setIsEditing(false)
  }

  const handleShare = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href)
      setCopiedLink(true)
      setTimeout(() => setCopiedLink(false), 2000)
    } catch (err) {
      console.error("Failed to copy URL:", err)
    }
  }

  return (
    <div className="h-14 border-b border-border/80 bg-background/50 backdrop-blur-md px-4 flex items-center justify-between shrink-0 select-none gap-4">
      {/* Title & Scope */}
      <div className="flex items-center gap-3 min-w-0 flex-1">
        <button
          onClick={onTogglePin}
          className={`p-1.5 rounded hover:bg-secondary cursor-pointer focus:outline-none transition-colors shrink-0 ${pinned ? "text-primary hover:text-primary-foreground" : "text-muted-foreground/40 hover:text-foreground"}`}
          title={pinned ? "Unpin thread" : "Pin thread"}
        >
          <Pin className={`h-4 w-4 ${pinned ? "fill-primary/20 rotate-45" : ""}`} />
        </button>

        <div className="flex-1 min-w-0 flex items-center gap-2">
          {isEditing ? (
            <div className="flex items-center gap-1.5 max-w-md w-full">
              <input
                type="text"
                value={editedTitle}
                onChange={(e) => setEditedTitle(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleSaveRename()
                  if (e.key === "Escape") {
                    setEditedTitle(title)
                    setIsEditing(false)
                  }
                }}
                className="bg-secondary/40 border border-border px-2 py-1 text-xs rounded-lg text-foreground outline-none focus:ring-1 focus:ring-primary w-full"
                autoFocus
              />
              <button
                onClick={handleSaveRename}
                className="p-1.5 text-emerald-400 hover:bg-secondary rounded cursor-pointer focus:outline-none"
              >
                <Check className="h-3.5 w-3.5" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2 min-w-0 group/title">
              <h1 className="font-bold text-xs sm:text-sm text-foreground truncate max-w-60 sm:max-w-md leading-none">
                {title}
              </h1>
              <button
                onClick={() => {
                  setEditedTitle(title)
                  setIsEditing(true)
                }}
                className="p-1 rounded opacity-0 group-hover/title:opacity-100 focus:opacity-100 hover:bg-secondary text-muted-foreground/60 hover:text-foreground cursor-pointer focus:outline-none transition-opacity"
                title="Rename conversation"
              >
                <Edit2 className="h-3 w-3" />
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Model & Metadata & Actions */}
      <div className="flex items-center gap-2 sm:gap-3 shrink-0">
        {/* Scope context info */}
        <div className="hidden md:flex items-center gap-1 text-[10px] font-mono text-muted-foreground">
          <Folder className="h-3 w-3 text-primary/70" />
          <span>Scope: <span className="text-foreground">{scope}</span></span>
        </div>

        {/* Selected Model badge */}
        <Badge variant="outline" className="text-[9px] font-mono bg-secondary/30 border-border/60 gap-1 text-muted-foreground px-2 py-0.5 shrink-0 select-none">
          <Sparkles className="h-2.5 w-2.5 text-primary" />
          {model}
        </Badge>

        <div className="h-4 w-px bg-border/60 hidden sm:block" />

        {/* Action icons */}
        <div className="flex items-center gap-0.5">
          {/* Search Trigger with Cmd+K badge */}
          {onOpenSearch && (
            <button
              onClick={onOpenSearch}
              className="p-1.5 rounded hover:bg-secondary text-muted-foreground hover:text-foreground cursor-pointer focus:outline-none transition-colors flex items-center gap-1 text-[10px] font-mono mr-1"
              title="Search conversations (Cmd + K)"
              aria-label="Search conversations"
            >
              <Search className="h-3.5 w-3.5" />
              <kbd className="hidden lg:inline-block text-[9px] bg-secondary/60 border border-border/80 px-1 py-0.2 rounded text-muted-foreground">⌘K</kbd>
            </button>
          )}

          {/* Share */}
          <button
            onClick={handleShare}
            className={`p-1.5 rounded hover:bg-secondary cursor-pointer focus:outline-none transition-colors text-[10px] font-mono ${copiedLink ? "text-emerald-400" : "text-muted-foreground hover:text-foreground"}`}
            title="Copy conversation URL link"
          >
            {copiedLink ? <Check className="h-3.5 w-3.5" /> : <Share2 className="h-3.5 w-3.5" />}
          </button>

          {/* Export JSON */}
          <button
            onClick={() => onExport("json")}
            className="p-1.5 rounded hover:bg-secondary text-muted-foreground hover:text-foreground cursor-pointer focus:outline-none transition-colors"
            title="Export Thread (JSON)"
          >
            <Download className="h-3.5 w-3.5" />
          </button>

          {/* Delete */}
          <button
            onClick={onDelete}
            className="p-1.5 rounded hover:bg-secondary text-muted-foreground hover:text-destructive cursor-pointer focus:outline-none transition-colors"
            title="Delete Conversation"
          >
            <Trash2 className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>
    </div>
  )
}
