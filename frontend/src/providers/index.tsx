import React from "react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { ThemeProvider } from "./ThemeProvider"
import { TooltipProvider } from "@/components/ui/tooltip"

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Retain resolved server data in stale status for 5 minutes.
      // Helps avoid redundant background sync operations.
      staleTime: 5 * 60 * 1000,
      
      // Retain unused cached data in memory for 10 minutes before garbage collection.
      gcTime: 10 * 60 * 1000,
      
      // Avoid firing LLM load requests automatically when users focus on browser windows
      refetchOnWindowFocus: false,
      
      // Auto reconnect recover when network offline finishes
      refetchOnReconnect: true,
      
      // Retry strategy: Retry only on safe read operations (GET/queries) up to 3 times
      // with exponential backoff delay to prevent overloading backend.
      retry: (failureCount, error) => {
        // Do not retry unauthorized, forbidden or client validations exceptions
        if (error instanceof Error && (error.message.includes("401") || error.message.includes("403") || error.message.includes("422"))) {
          return false
        }
        return failureCount < 3
      },
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000)
    },
    mutations: {
      // Do not retry mutate state operations to avoid double POST submissions
      retry: 0
    }
  }
})

export const RootProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <TooltipProvider delayDuration={200}>
          {children}
        </TooltipProvider>
      </QueryClientProvider>
    </ThemeProvider>
  )
}
