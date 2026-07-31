import React from "react"
import { Spinner } from "./Spinner"
import { cn } from "@/lib/utils"

interface LoadingIndicatorProps extends React.HTMLAttributes<HTMLDivElement> {
  fullScreen?: boolean
  message?: string
  size?: "sm" | "md" | "lg" | "xl"
}

export const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({
  className,
  fullScreen = false,
  message = "Loading...",
  size = "lg",
  ...props
}) => {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-3 p-6 text-muted-foreground",
        fullScreen && "fixed inset-0 z-50 bg-background/80 backdrop-blur-md",
        className
      )}
      {...props}
    >
      <Spinner size={size} />
      {message && <p className="text-sm font-medium tracking-wide animate-pulse">{message}</p>}
    </div>
  )
}
