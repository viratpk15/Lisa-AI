import React from "react"
import { cn } from "@/lib/utils"

interface SpinnerProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: "sm" | "md" | "lg" | "xl"
  variant?: "primary" | "muted" | "white"
}

export const Spinner = React.forwardRef<HTMLDivElement, SpinnerProps>(
  ({ className, size = "md", variant = "primary", ...props }, ref) => {
    const sizeClasses = {
      sm: "h-4 w-4 border-2",
      md: "h-6 w-6 border-2",
      lg: "h-8 w-8 border-[3px]",
      xl: "h-12 w-12 border-4",
    }

    const variantClasses = {
      primary: "border-primary/20 border-t-primary",
      muted: "border-muted-foreground/20 border-t-muted-foreground",
      white: "border-white/20 border-t-white",
    }

    return (
      <div
        ref={ref}
        className={cn(
          "animate-spin rounded-full border-solid",
          sizeClasses[size],
          variantClasses[variant],
          className
        )}
        role="status"
        aria-label="Loading"
        {...props}
      />
    )
  }
)
Spinner.displayName = "Spinner"
