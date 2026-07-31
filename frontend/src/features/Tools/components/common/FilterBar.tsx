import { Layers } from "lucide-react"

interface FilterBarProps {
  categories: string[]
  selectedCategory: string | null
  onSelectCategory: (cat: string | null) => void
}

export function FilterBar({ categories, selectedCategory, onSelectCategory }: FilterBarProps) {
  return (
    <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
      <button
        onClick={() => onSelectCategory(null)}
        className={`px-3 py-1 text-xs font-medium rounded-full cursor-pointer transition-all whitespace-nowrap ${
          selectedCategory === null
            ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 shadow-xs"
            : "bg-secondary/40 text-muted-foreground border border-border/40 hover:text-foreground hover:bg-secondary/70"
        }`}
      >
        <Layers className="inline-block h-3 w-3 mr-1 -mt-0.5" />
        All Categories
      </button>

      {categories.map((cat) => {
        const isSelected = selectedCategory === cat
        return (
          <button
            key={cat}
            onClick={() => onSelectCategory(isSelected ? null : cat)}
            className={`px-3 py-1 text-xs font-medium rounded-full cursor-pointer transition-all capitalize whitespace-nowrap ${
              isSelected
                ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 shadow-xs"
                : "bg-secondary/40 text-muted-foreground border border-border/40 hover:text-foreground hover:bg-secondary/70"
            }`}
          >
            {cat}
          </button>
        )
      })}
    </div>
  )
}
