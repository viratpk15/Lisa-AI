export function LoadingSkeleton({ count = 4 }: { count?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, idx) => (
        <div
          key={idx}
          className="p-4 bg-secondary/20 border border-border/30 rounded-xl animate-pulse space-y-2.5"
        >
          <div className="flex items-center justify-between">
            <div className="h-4 w-36 bg-secondary/60 rounded" />
            <div className="h-3 w-16 bg-secondary/50 rounded-full" />
          </div>
          <div className="h-3 w-3/4 bg-secondary/40 rounded" />
          <div className="flex items-center gap-2 pt-1">
            <div className="h-3.5 w-12 bg-secondary/50 rounded" />
            <div className="h-3.5 w-16 bg-secondary/50 rounded" />
          </div>
        </div>
      ))}
    </div>
  )
}
