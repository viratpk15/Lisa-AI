/**
 * Lisa AIOS — Job Search Filters Panel
 * Controls role, location, remote, type, experience, and sorting.
 */

import { useState, useEffect } from "react"
import { Search, SlidersHorizontal, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import type { JobSearchFilters } from "../types"
import { cn } from "@/lib/utils"

interface JobSearchFiltersProps {
  onSearch: (filters: JobSearchFilters) => void
  isLoading: boolean
  activeFilters?: JobSearchFilters | null
}

const employmentTypes = [
  { value: "any", label: "All Types" },
  { value: "internship", label: "Internship" },
  { value: "full_time", label: "Full-time" },
  { value: "entry_level", label: "Entry-level" },
  { value: "graduate", label: "Graduate" },
  { value: "contract", label: "Contract" },
]

const experienceLevels = [
  { value: "", label: "Any Level" },
  { value: "internship", label: "Student / Intern" },
  { value: "entry_level", label: "Entry-level (0–2yr)" },
  { value: "junior", label: "Junior (1–3yr)" },
  { value: "mid", label: "Mid-level (3–6yr)" },
]

const sortOptions = [
  { value: "relevance", label: "Relevance" },
  { value: "newest", label: "Newest" },
  { value: "salary", label: "Salary" },
]

export function JobSearchFiltersPanel({ onSearch, isLoading, activeFilters }: JobSearchFiltersProps) {
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [query, setQuery] = useState("")
  const [role, setRole] = useState("")
  const [location, setLocation] = useState("")
  const [company, setCompany] = useState("")
  const [remoteOnly, setRemoteOnly] = useState(false)
  const [employmentType, setEmploymentType] = useState<string>("any")
  const [experienceLevel, setExperienceLevel] = useState("")
  const [sortBy, setSortBy] = useState<"relevance" | "newest" | "salary">("relevance")

  useEffect(() => {
    if (activeFilters) {
      if (activeFilters.role !== undefined) {
        setRole(activeFilters.role)
        setQuery(activeFilters.role)
      }
      if (activeFilters.location !== undefined) setLocation(activeFilters.location)
      if (activeFilters.company !== undefined) setCompany(activeFilters.company)
      if (activeFilters.is_remote !== undefined) setRemoteOnly(Boolean(activeFilters.is_remote))
      if (activeFilters.employment_type !== undefined) setEmploymentType(activeFilters.employment_type || "any")
      if (activeFilters.experience_level !== undefined) setExperienceLevel(activeFilters.experience_level || "")
      if (activeFilters.sort_by !== undefined) setSortBy(activeFilters.sort_by as "relevance" | "newest" | "salary")
      if (activeFilters.location || activeFilters.experience_level || activeFilters.company) {
        setShowAdvanced(true)
      }
    }
  }, [activeFilters])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Map frontend state to real backend JobSearchFilters schema
    const filters: JobSearchFilters = {
      role: role || query || undefined,      // backend: role
      location: location || undefined,
      company: company || undefined,
      is_remote: remoteOnly || undefined,   // backend: is_remote
      employment_type: (employmentType !== "any" ? employmentType : undefined) as JobSearchFilters["employment_type"],
      experience_level: experienceLevel || undefined,
      sort_by: sortBy,
      limit: 25,
    }
    onSearch(filters)
  }

  const handleReset = () => {
    setQuery("")
    setRole("")
    setLocation("")
    setCompany("")
    setRemoteOnly(false)
    setEmploymentType("any")
    setExperienceLevel("")
    setSortBy("relevance")
  }

  return (
    <form onSubmit={handleSubmit} className="rounded-xl border border-border/70 bg-card/60 p-5 space-y-4">
      {/* Primary Search Bar */}
      <div className="flex gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search jobs, companies, or keywords..."
            className="pl-9 h-10"
          />
        </div>
        <Button type="submit" disabled={isLoading} className="h-10 px-5">
          {isLoading ? "Searching..." : "Find Opportunities"}
        </Button>
        <Button
          type="button"
          variant="outline"
          size="icon"
          onClick={() => setShowAdvanced((prev) => !prev)}
          className={cn("h-10 w-10", showAdvanced && "border-primary bg-primary/10 text-primary")}
          title="Advanced filters"
        >
          <SlidersHorizontal className="h-4 w-4" />
        </Button>
      </div>

      {/* Quick Type Chips */}
      <div className="flex flex-wrap gap-2">
        {employmentTypes.map((type) => (
          <button
            key={type.value}
            type="button"
            onClick={() => setEmploymentType(type.value)}
            className={cn(
              "text-xs px-3 py-1 rounded-full border transition-colors font-medium",
              employmentType === type.value
                ? "bg-primary border-primary text-primary-foreground"
                : "border-border/70 text-muted-foreground hover:border-primary/50 hover:text-foreground"
            )}
          >
            {type.label}
          </button>
        ))}

        <button
          type="button"
          onClick={() => setRemoteOnly((prev) => !prev)}
          className={cn(
            "text-xs px-3 py-1 rounded-full border transition-colors font-medium",
            remoteOnly
              ? "bg-emerald-500 border-emerald-500 text-white"
              : "border-border/70 text-muted-foreground hover:border-emerald-500/50 hover:text-emerald-600"
          )}
        >
          🌐 Remote Only
        </button>
      </div>

      {/* Advanced Filters */}
      {showAdvanced && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-2 border-t border-border/50">
          <div className="space-y-1">
            <label className="text-xs font-semibold text-muted-foreground">Role / Title</label>
            <Input
              value={role}
              onChange={(e) => setRole(e.target.value)}
              placeholder="e.g. ML Engineer"
              className="h-9 text-sm"
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-semibold text-muted-foreground">Location</label>
            <Input
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g. Bangalore, Mumbai"
              className="h-9 text-sm"
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-semibold text-muted-foreground">Experience Level</label>
            <select
              value={experienceLevel}
              onChange={(e) => setExperienceLevel(e.target.value)}
              className="w-full h-9 text-sm rounded-md border border-input bg-background px-3 text-foreground"
            >
              {experienceLevels.map((lvl) => (
                <option key={lvl.value} value={lvl.value}>
                  {lvl.label}
                </option>
              ))}
            </select>
          </div>
          <div className="space-y-1">
            <label className="text-xs font-semibold text-muted-foreground">Sort By</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as "relevance" | "newest" | "salary")}
              className="w-full h-9 text-sm rounded-md border border-input bg-background px-3 text-foreground"
            >
              {sortOptions.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>
          </div>
          <div className="space-y-1 sm:col-span-2">
            <label className="text-xs font-semibold text-muted-foreground">Target Company</label>
            <div className="flex gap-2">
              <Input
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                placeholder="e.g. Google, Microsoft, Startup"
                className="h-9 text-sm flex-1"
              />
              <button
                type="button"
                onClick={handleReset}
                className="text-xs flex items-center gap-1 text-muted-foreground hover:text-destructive transition-colors px-3 py-1.5 rounded-md border border-border"
              >
                <X className="h-3 w-3" />
                Reset
              </button>
            </div>
          </div>
        </div>
      )}
    </form>
  )
}
