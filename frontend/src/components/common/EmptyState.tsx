import type { HTMLAttributes, FC } from "react"
import type { LucideIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface EmptyStateProps extends HTMLAttributes<HTMLDivElement> {
  title: string
  description: string
  icon?: LucideIcon
  actionText?: string
  onAction?: () => void
}

export const EmptyState: FC<EmptyStateProps> = ({
  className,
  title,
  description,
  icon: Icon,
  actionText,
  onAction,
  ...props
}) => {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center text-center p-8 border border-dashed border-border/60 rounded-xl bg-card/20 max-w-md mx-auto my-6",
        className
      )}
      {...props}
    >
      {Icon && (
        <div className="flex items-center justify-center w-12 h-12 rounded-lg bg-secondary/50 text-muted-foreground mb-4 border border-border/40">
          <Icon className="w-6 h-6 text-muted-foreground/85" />
        </div>
      )}
      <h3 className="text-lg font-semibold text-foreground tracking-tight mb-1">{title}</h3>
      <p className="text-sm text-muted-foreground mb-5 leading-relaxed">{description}</p>
      {actionText && onAction && (
        <Button onClick={onAction} size="sm" className="font-medium cursor-pointer">
          {actionText}
        </Button>
      )}
    </div>
  )
}
