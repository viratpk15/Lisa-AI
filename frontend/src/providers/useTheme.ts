import { useContext } from "react"
import { ThemeContext } from "./ThemeContext"
import type { Theme } from "./ThemeProvider"

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error("useTheme must be used within a ThemeProvider")
  }
  return context
}

export type { Theme }