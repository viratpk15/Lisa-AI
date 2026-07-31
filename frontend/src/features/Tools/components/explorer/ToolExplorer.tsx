import { useToolConsoleStore } from "../../store/useToolConsoleStore"
import { useToolsQuery, useCategoriesQuery } from "../../services/toolApi"
import { SearchBar } from "../common/SearchBar"
import { FilterBar } from "../common/FilterBar"
import { ToolCard } from "./ToolCard"
import { LoadingSkeleton } from "../common/LoadingSkeleton"
import { EmptyState } from "../common/EmptyState"
import { ErrorState } from "../common/ErrorState"

export function ToolExplorer() {
  const selectedToolName = useToolConsoleStore((s) => s.selectedToolName)
  const setSelectedToolName = useToolConsoleStore((s) => s.setSelectedToolName)
  const searchQuery = useToolConsoleStore((s) => s.searchQuery)
  const setSearchQuery = useToolConsoleStore((s) => s.setSearchQuery)
  const selectedCategory = useToolConsoleStore((s) => s.selectedCategory)
  const setSelectedCategory = useToolConsoleStore((s) => s.setSelectedCategory)
  const resetFilters = useToolConsoleStore((s) => s.resetFilters)

  const { data: tools, isLoading, isError, refetch } = useToolsQuery(selectedCategory, null, searchQuery)
  const { data: categories = [] } = useCategoriesQuery()

  return (
    <div className="space-y-4">
      {/* Search & Filter Header */}
      <div className="space-y-2.5">
        <SearchBar value={searchQuery} onChange={setSearchQuery} />
        <FilterBar
          categories={categories}
          selectedCategory={selectedCategory}
          onSelectCategory={setSelectedCategory}
        />
      </div>

      {/* Tool List Content */}
      {isLoading ? (
        <LoadingSkeleton count={4} />
      ) : isError ? (
        <ErrorState onRetry={refetch} />
      ) : !tools || tools.length === 0 ? (
        <EmptyState onReset={resetFilters} />
      ) : (
        <div className="grid gap-3 grid-cols-1 md:grid-cols-2">
          {tools.map((tool) => (
            <ToolCard
              key={tool.name}
              tool={tool}
              isSelected={selectedToolName === tool.name}
              onSelect={setSelectedToolName}
            />
          ))}
        </div>
      )}
    </div>
  )
}
