import { useRef, useEffect } from "react"
import { Search, X } from "lucide-react"

interface SearchBarProps {
  value: string
  onChange: (val: string) => void
  placeholder?: string
  shortcut?: string
}

export function SearchBar({ value, onChange, placeholder = "Search tools... (/)", shortcut = "/" }: SearchBarProps) {
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === shortcut && document.activeElement !== inputRef.current) {
        e.preventDefault()
        inputRef.current?.focus()
      }
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [shortcut])

  return (
    <div className="relative flex items-center w-full">
      <Search className="absolute left-3 h-4 w-4 text-muted-foreground pointer-events-none" />
      <input
        ref={inputRef}
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full pl-9 pr-8 py-2 text-sm bg-secondary/30 border border-border/50 rounded-lg text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 transition-all"
      />
      {value ? (
        <button
          onClick={() => onChange("")}
          className="absolute right-2.5 p-1 text-muted-foreground hover:text-foreground cursor-pointer rounded"
        >
          <X className="h-3.5 w-3.5" />
        </button>
      ) : (
        <kbd className="absolute right-2.5 px-1.5 py-0.5 text-[10px] font-mono text-muted-foreground bg-secondary/60 border border-border/60 rounded pointer-events-none">
          {shortcut}
        </kbd>
      )}
    </div>
  )
}
