import React, { useEffect, useState } from "react"
import { ThemeContext } from "./ThemeContext"

export type Theme = "dark" | "light" | "aurora"

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setThemeState] = useState<Theme>(() => {
    const saved = localStorage.getItem("theme") as Theme
    if (saved && ["dark", "light", "aurora"].includes(saved)) {
      return saved
    }
    return "dark"
  })

  useEffect(() => {
    const root = window.document.documentElement
    root.classList.remove("light", "dark", "aurora")
    root.classList.add(theme)
    localStorage.setItem("theme", theme)
  }, [theme])

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme)
  }

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

