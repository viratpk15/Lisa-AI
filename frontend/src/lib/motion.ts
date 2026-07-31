import type { Variants } from "framer-motion"

export const springTransition = {
  type: "spring" as const,
  stiffness: 350,
  damping: 30,
  mass: 0.8
}

export const easeTransition = {
  type: "tween" as const,
  ease: [0.16, 1, 0.3, 1] as const, // easeOutExpo
  duration: 0.3
}

export const pageVariants: Variants = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0, transition: easeTransition },
  exit: { opacity: 0, y: -6, transition: { duration: 0.15 } }
}

export const sidebarVariants: Variants = {
  expanded: { width: 260, transition: springTransition },
  collapsed: { width: 68, transition: springTransition }
}

export const sidebarItemVariants: Variants = {
  initial: { opacity: 0, x: -10 },
  animate: { opacity: 1, x: 0, transition: { duration: 0.2 } },
  exit: { opacity: 0, x: -10, transition: { duration: 0.1 } }
}

export const panelVariants: Variants = {
  open: { 
    width: 320, 
    opacity: 1,
    x: 0,
    display: "flex",
    transition: springTransition 
  },
  closed: { 
    width: 0, 
    opacity: 0,
    x: 20,
    transitionEnd: { display: "none" },
    transition: springTransition 
  }
}

export const dialogVariants: Variants = {
  initial: { opacity: 0, scale: 0.96, y: -12 },
  animate: { opacity: 1, scale: 1, y: 0, transition: easeTransition },
  exit: { opacity: 0, scale: 0.96, y: -8, transition: { duration: 0.12 } }
}

export const dropdownScaleFade: Variants = {
  initial: { opacity: 0, scale: 0.95, y: -6 },
  animate: { opacity: 1, scale: 1, y: 0, transition: { duration: 0.18, ease: [0.16, 1, 0.3, 1] } },
  exit: { opacity: 0, scale: 0.95, y: -4, transition: { duration: 0.12 } }
}

export const fadeVariants: Variants = {
  initial: { opacity: 0 },
  animate: { opacity: 1, transition: { duration: 0.2 } },
  exit: { opacity: 0, transition: { duration: 0.15 } }
}

export const commandPaletteItemVariants: Variants = {
  hover: { backgroundColor: "var(--color-secondary)", scale: 1.008, transition: { duration: 0.15 } },
  tap: { scale: 0.985 }
}

export const dashboardGridVariants: Variants = {
  initial: { opacity: 0 },
  animate: {
    opacity: 1,
    transition: {
      staggerChildren: 0.03
    }
  }
}

export const dashboardCardVariants: Variants = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0, transition: easeTransition },
  hover: {
    y: -2.5,
    transition: { duration: 0.2, ease: "easeOut" }
  },
  tap: { scale: 0.985 }
}

export const dashboardItemVariants: Variants = {
  initial: { opacity: 0, x: -8 },
  animate: { opacity: 1, x: 0, transition: easeTransition }
}

export const messageVariants: Variants = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0, transition: easeTransition }
}

export const attachmentVariants: Variants = {
  initial: { opacity: 0, scale: 0.85 },
  animate: { opacity: 1, scale: 1, transition: springTransition },
  exit: { opacity: 0, scale: 0.85, transition: { duration: 0.15 } }
}

export const cursorVariants: Variants = {
  blink: {
    opacity: [1, 0, 1],
    transition: { duration: 0.8, repeat: Infinity, ease: "linear" }
  }
}

export const buttonMicroVariants: Variants = {
  hover: { y: -1, transition: { duration: 0.15 } },
  tap: { scale: 0.97, y: 0 }
}

export const tableRowVariants: Variants = {
  initial: { opacity: 0, y: 4 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.15 } },
  hover: { backgroundColor: "color-mix(in srgb, hsl(var(--secondary)) 60%, transparent)" }
}



