# Theme System Specifications: Jarvis AIOS

## 1. Design Token Registry

All themes expose standard HSL tokens used across the application:

| Semantic Token | Purpose | Dark Theme | Light Theme | Aurora Theme |
| :--- | :--- | :--- | :--- | :--- |
| `--background` | Root canvas | `240 10% 2%` (`#030712`) | `210 40% 98%` (`#f8fafc`) | `235 45% 6%` (`#070a14`) |
| `--foreground` | Primary text | `0 0% 98%` (`#fafafa`) | `222 47% 11%` (`#0f172a`) | `210 40% 98%` (`#f8fafc`) |
| `--card` | Surface containers | `240 10% 4.5%` (`#0b0e14`) | `0 0% 100%` (`#ffffff`) | `240 35% 10%` (`#101326`) |
| `--popover` | Elevated dialogs/menus | `240 10% 6.5%` (`#10141e`) | `0 0% 100%` (`#ffffff`) | `240 35% 12%` (`#151833`) |
| `--primary` | Active branding accent | `250 84% 67%` (`#818cf8`) | `221 83% 53%` (`#2563eb`) | `265 89% 66%` (`#a855f7`) |
| `--secondary` | Secondary interactive | `240 5% 12%` (`#1c1d22`) | `210 40% 96%` (`#f1f5f9`) | `240 30% 16%` (`#202444`) |
| `--muted-foreground` | Subdued labels/hints | `240 5% 65%` (`#9ca3af`) | `215 16% 47%` (`#64748b`) | `230 20% 70%` (`#a5b4fc`) |
| `--border` | Dividers & outlines | `240 5% 14%` | `214 32% 91%` | `250 40% 22%` |

---

## 2. Theme Descriptions

### Theme 1: Premium Dark (Default)
- **Concept**: True AMOLED Black desktop space with frosted glass & Digital Violet accents.
- **Aesthetic**: Sleek, high-end professional AI OS feeling. Minimalist, deep contrast, low eye fatigue.

### Theme 2: Premium Light
- **Concept**: Soft White Workspace (`#f8fafc`) with pure white card containers (`#ffffff`) and charcoal typography (`#0f172a`).
- **Aesthetic**: Clean Apple / Vercel desktop application look. High legibility in bright environment.

### Theme 3: Aurora
- **Concept**: Cybernetic Space Obsidian (`#070a14`) with electric neon purple (`#a855f7`) and cyan glow.
- **Aesthetic**: Futuristic AI branding identity with glowing gradients and ambient depth.
