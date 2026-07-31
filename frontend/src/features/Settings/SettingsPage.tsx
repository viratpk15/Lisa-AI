import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Save, Shield, Settings2, Palette, Check, Moon, Sun, Sparkles } from "lucide-react"
import { useTheme, type Theme } from "@/providers/useTheme"
import { cn } from "@/lib/utils"

export default function SettingsPage() {
  const { theme, setTheme } = useTheme()

  const themesList: Array<{
    id: Theme
    name: string
    desc: string
    icon: typeof Moon
    colors: { bg: string; border: string; accent: string; text: string }
  }> = [
    {
      id: "dark",
      name: "Premium Dark",
      desc: "AMOLED deep black, frosted glass & soft accent glow",
      icon: Moon,
      colors: { bg: "bg-slate-950", border: "border-slate-800", accent: "bg-indigo-500", text: "text-white" }
    },
    {
      id: "light",
      name: "Premium Light",
      desc: "Soft white workspace, charcoal typography & Apple-style polish",
      icon: Sun,
      colors: { bg: "bg-slate-50", border: "border-slate-300", accent: "bg-blue-600", text: "text-slate-900" }
    },
    {
      id: "aurora",
      name: "Aurora",
      desc: "Cybernetic space black with electric neon purple & cyan gradients",
      icon: Sparkles,
      colors: { bg: "bg-purple-950/60", border: "border-purple-500/40", accent: "bg-purple-500", text: "text-purple-100" }
    }
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight bg-linear-to-r from-foreground via-foreground/90 to-primary bg-clip-text text-transparent">Settings</h1>
        <p className="text-muted-foreground mt-1">Configure your local Jarvis AIOS runtime parameters, theme aesthetics, and agent preferences.</p>
      </div>

      {/* Theme System Selector */}
      <Card className="border-border/60 bg-card/40 backdrop-blur-md">
        <CardHeader>
          <div className="flex items-center gap-2 text-primary">
            <Palette className="h-5 w-5" />
            <CardTitle className="text-base font-semibold">Appearance & Desktop Theme System</CardTitle>
          </div>
          <CardDescription>Select your active desktop environment theme. Switch instantly without page reload.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            {themesList.map((t) => {
              const Icon = t.icon
              const isActive = theme === t.id

              return (
                <button
                  key={t.id}
                  type="button"
                  onClick={() => setTheme(t.id)}
                  className={cn(
                    "flex flex-col text-left p-4 rounded-xl border transition-all duration-200 cursor-pointer relative group outline-none focus-visible:ring-2 focus-visible:ring-primary",
                    isActive
                      ? "border-primary bg-primary/10 shadow-lg shadow-primary/10 ring-1 ring-primary"
                      : "border-border/60 bg-secondary/30 hover:border-primary/40 hover:bg-secondary/60"
                  )}
                >
                  {isActive && (
                    <div className="absolute top-3 right-3 h-5 w-5 rounded-full bg-primary text-primary-foreground flex items-center justify-center shadow-sm">
                      <Check className="h-3 w-3 stroke-3" />
                    </div>
                  )}

                  <div className="flex items-center gap-2.5 mb-3">
                    <div className={cn("p-2 rounded-lg border", t.colors.bg, t.colors.border, t.colors.text)}>
                      <Icon className="h-4 w-4" />
                    </div>
                    <span className="font-semibold text-sm text-foreground">{t.name}</span>
                  </div>

                  <p className="text-xs text-muted-foreground leading-relaxed flex-1 mb-4">{t.desc}</p>

                  {/* Visual Color Preview Chips */}
                  <div className="flex items-center gap-1.5 pt-2 border-t border-border/40">
                    <span className={cn("h-3.5 w-3.5 rounded-full border border-white/20", t.colors.bg)} />
                    <span className={cn("h-3.5 w-3.5 rounded-full border border-white/20", t.colors.accent)} />
                    <span className={cn("h-3.5 w-3.5 rounded-full border border-white/20", t.colors.border)} />
                  </div>
                </button>
              )
            })}
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="border-border/60 bg-card/30 backdrop-blur-sm">
          <CardHeader>
            <div className="flex items-center gap-2 text-primary">
              <Settings2 className="h-5 w-5" />
              <CardTitle className="text-base font-semibold">General AI Engine</CardTitle>
            </div>
            <CardDescription>Setup default API endpoint bindings and model choices.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider font-mono">Primary Model</label>
              <Input placeholder="gemini-2.5-flash" className="bg-secondary/40 border-border/50 text-sm focus-visible:ring-primary" />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider font-mono">Reasoning Temperature</label>
              <Input type="number" step="0.1" defaultValue="0.2" className="bg-secondary/40 border-border/50 text-sm focus-visible:ring-primary" />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider font-mono">Fallback API Key</label>
              <Input type="password" placeholder="••••••••••••••••••••" className="bg-secondary/40 border-border/50 text-sm focus-visible:ring-primary" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-border/60 bg-card/30 backdrop-blur-sm">
          <CardHeader>
            <div className="flex items-center gap-2 text-primary">
              <Shield className="h-5 w-5" />
              <CardTitle className="text-base font-semibold">Security Settings</CardTitle>
            </div>
            <CardDescription>Configure filesystem and tool authorization thresholds.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider font-mono">Workspace Directory Root</label>
              <Input placeholder="/Users/virat/MyPersonalCloud/Virat/AI-Engineering/Projects/Jarvis" className="bg-secondary/40 border-border/50 text-sm focus-visible:ring-primary" />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider font-mono">Tool Confirmation Scope</label>
              <Input placeholder="Commands, Write Actions, Web Requests" className="bg-secondary/40 border-border/50 text-sm focus-visible:ring-primary" />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider font-mono">System Prompt Override</label>
              <Textarea placeholder="You are Jarvis, a production-grade AI Operating System..." className="bg-secondary/40 border-border/50 text-sm min-h-20.5 focus-visible:ring-primary" />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="flex justify-end gap-3">
        <Button variant="outline" className="cursor-pointer border-border font-medium">Cancel</Button>
        <Button className="gap-2 cursor-pointer font-medium">
          <Save className="h-4 w-4" />
          Save Configurations
        </Button>
      </div>
    </div>
  )
}

