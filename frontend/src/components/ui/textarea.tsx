import * as React from "react"

import { cn } from "@/lib/utils"

function Textarea({ className, ...props }: React.ComponentProps<"textarea">) {
  return (
    <textarea
      data-slot="textarea"
      className={cn(
        "flex field-sizing-content min-h-16 w-full rounded-lg border border-border/70 bg-secondary/30 px-3 py-2 text-sm transition-all duration-200 outline-none placeholder:text-muted-foreground/70 hover:border-border/90 focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:bg-secondary/60 disabled:cursor-not-allowed disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-2 aria-invalid:ring-destructive/30 md:text-sm",
        className
      )}
      {...props}
    />
  )
}

export { Textarea }
