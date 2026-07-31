# Interaction Guidelines & Micro-Interaction Standards

## 1. Interaction Rules by Component

### Buttons
- **Hover**: Smooth lift (`transform: translateY(-1px)` or `hover:-translate-y-0.5`), glowing primary shadow.
- **Press / Active**: Compression scale (`active:scale-[0.97] translate-y-0`).
- **Focus**: Visible ring (`focus-visible:ring-2 focus-visible:ring-ring/50`).

### Cards
- **Hover**: Subtle vertical float (`hover:-translate-y-0.5`), border token transition (`hover:border-primary/30`), soft shadow elevation.
- **Transition**: `transition-all duration-200 cubic-bezier(0.16, 1, 0.3, 1)`.

### Navigation & Sidebar
- **Active State**: Shared layout background pill animated via Framer Motion `layoutId="sidebarActiveItem"` with spring physics (`stiffness: 350, damping: 30`).
- **Hover**: Subdued secondary background transition.

### Tabs & Inspector
- **Active Tab**: Sliding Framer Motion indicator `layoutId="inspectorActiveTab"`.

### Dialogs & Dropdowns
- **Open Animation**: Scale + fade entry (`dialogVariants`, `dropdownScaleFade`).
- **Surface**: Frosted glass (`backdrop-blur-xl bg-popover/90 border border-border/80 shadow-2xl`).

### Inputs
- **Focus**: Glowing ring (`focus-visible:ring-primary/30 focus-visible:border-primary`), background tint shift.

---

## 2. Motion Physics Standards

All motion transitions utilize GPU-accelerated properties (`transform`, `opacity`) to eliminate layout thrashing:
```typescript
export const springTransition = {
  type: "spring",
  stiffness: 350,
  damping: 30,
  mass: 0.8
}
```
Reduced-motion support is automatically enforced for users who enable system-level accessibility settings.
