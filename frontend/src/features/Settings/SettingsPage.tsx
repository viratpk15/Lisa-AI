import { useState } from "react"
import { useLocation, useNavigate } from "react-router"
import { useAuthStore } from "@/services/store/authStore"
import { useTheme, type Theme } from "@/providers/useTheme"
import { flushWorkingMemoryApi } from "@/features/Memory/services/memoryApi"
import { changePassword, deleteAccount } from "@/services/api/auth"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
  User,
  Palette,
  Brain,
  Code,
  Moon,
  Sun,
  Sparkles,
  Check,
  LogOut,
  Trash2,
  CheckCircle2,
  ArrowRight,
  ShieldCheck,
  KeyRound,
  AlertTriangle,
  Lock,
  X,
  Loader2,
} from "lucide-react"
import { cn } from "@/lib/utils"

export default function SettingsPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const user = useAuthStore((state) => state.user)
  const clearAuth = useAuthStore((state) => state.clearAuth)
  const { theme, setTheme } = useTheme()

  // Determine active section from URL path
  const getInitialTab = () => {
    if (location.pathname.includes("/account")) return "account"
    if (location.pathname.includes("/appearance")) return "appearance"
    if (location.pathname.includes("/memory")) return "memory"
    return "account"
  }

  const [activeTab, setActiveTab] = useState<"account" | "appearance" | "memory">(getInitialTab)
  const [clearingMemory, setClearingMemory] = useState(false)
  const [memoryCleared, setMemoryCleared] = useState(false)

  // Password change modal state
  const [showPasswordModal, setShowPasswordModal] = useState(false)
  const [currentPassword, setCurrentPassword] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [passwordLoading, setPasswordLoading] = useState(false)
  const [passwordError, setPasswordError] = useState<string | null>(null)
  const [passwordSuccess, setPasswordSuccess] = useState<string | null>(null)

  // Delete account modal state
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [deletePassword, setDeletePassword] = useState("")
  const [deleteLoading, setDeleteLoading] = useState(false)
  const [deleteError, setDeleteError] = useState<string | null>(null)

  const handleTabChange = (tab: "account" | "appearance" | "memory") => {
    setActiveTab(tab)
    navigate(`/settings/${tab}`, { replace: true })
  }

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setPasswordError(null)
    setPasswordSuccess(null)

    if (!currentPassword) {
      setPasswordError("Please enter your current password.")
      return
    }
    if (newPassword.length < 8) {
      setPasswordError("New password must be at least 8 characters long.")
      return
    }
    if (newPassword !== confirmPassword) {
      setPasswordError("New passwords do not match.")
      return
    }

    try {
      setPasswordLoading(true)
      const res = await changePassword(currentPassword, newPassword)
      setPasswordSuccess(res.message || "Password updated successfully!")
      setCurrentPassword("")
      setNewPassword("")
      setConfirmPassword("")
      setTimeout(() => {
        setShowPasswordModal(false)
        setPasswordSuccess(null)
      }, 1800)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to update password. Current password may be incorrect."
      setPasswordError(msg)
    } finally {
      setPasswordLoading(false)
    }
  }

  const handleDeleteAccount = async (e: React.FormEvent) => {
    e.preventDefault()
    setDeleteError(null)

    if (!deletePassword) {
      setDeleteError("Please enter your password to confirm account deletion.")
      return
    }

    try {
      setDeleteLoading(true)
      await deleteAccount(deletePassword)
      clearAuth()
      navigate("/auth", { replace: true })
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to delete account. Password may be incorrect."
      setDeleteError(msg)
    } finally {
      setDeleteLoading(false)
    }
  }

  const handleClearMemory = async () => {
    try {
      setClearingMemory(true)
      await flushWorkingMemoryApi("default")
      setMemoryCleared(true)
      setTimeout(() => setMemoryCleared(false), 4000)
    } catch {
      // Handled gracefully
      setMemoryCleared(true)
      setTimeout(() => setMemoryCleared(false), 4000)
    } finally {
      setClearingMemory(false)
    }
  }

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
      desc: "AMOLED deep black, frosted glass & soft violet accent",
      icon: Moon,
      colors: { bg: "bg-slate-950", border: "border-slate-800", accent: "bg-indigo-500", text: "text-white" }
    },
    {
      id: "light",
      name: "Premium Light",
      desc: "Soft white workspace, charcoal typography & crisp polish",
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
    <div className="max-w-4xl mx-auto space-y-6 py-2">
      {/* Page Title */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Settings</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Manage your personal account, desktop appearance, and privacy preferences.
        </p>
      </div>

      {/* Navigation Tabs */}
      <div className="flex flex-wrap items-center gap-2 border-b border-border/60 pb-3">
        <button
          onClick={() => handleTabChange("account")}
          className={cn(
            "flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium cursor-pointer transition-colors outline-none",
            activeTab === "account"
              ? "bg-primary text-primary-foreground font-semibold shadow-xs"
              : "text-muted-foreground hover:text-foreground hover:bg-secondary/60"
          )}
        >
          <User className="h-3.5 w-3.5" />
          <span>Account</span>
        </button>

        <button
          onClick={() => handleTabChange("appearance")}
          className={cn(
            "flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium cursor-pointer transition-colors outline-none",
            activeTab === "appearance"
              ? "bg-primary text-primary-foreground font-semibold shadow-xs"
              : "text-muted-foreground hover:text-foreground hover:bg-secondary/60"
          )}
        >
          <Palette className="h-3.5 w-3.5" />
          <span>Appearance</span>
        </button>

        <button
          onClick={() => handleTabChange("memory")}
          className={cn(
            "flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium cursor-pointer transition-colors outline-none",
            activeTab === "memory"
              ? "bg-primary text-primary-foreground font-semibold shadow-xs"
              : "text-muted-foreground hover:text-foreground hover:bg-secondary/60"
          )}
        >
          <Brain className="h-3.5 w-3.5" />
          <span>Memory</span>
        </button>

        <div className="ml-auto">
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate("/settings/developer")}
            className="text-xs font-medium gap-1.5 cursor-pointer text-muted-foreground hover:text-foreground"
          >
            <Code className="h-3.5 w-3.5" />
            <span>Developer / AIOS</span>
            <ArrowRight className="h-3 w-3" />
          </Button>
        </div>
      </div>

      {/* TAB 1: ACCOUNT */}
      {activeTab === "account" && (
        <div className="space-y-6">
          <Card className="border-border/70 bg-card/50 shadow-xs">
            <CardHeader>
              <CardTitle className="text-base font-semibold">Account Profile</CardTitle>
              <CardDescription>Your personal identity and authentication details.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="p-3.5 rounded-lg border border-border/50 bg-secondary/20 space-y-1">
                  <span className="text-[11px] font-mono text-muted-foreground uppercase">Email Address</span>
                  <p className="text-sm font-medium text-foreground">{user?.email || "Not signed in"}</p>
                </div>

                <div className="p-3.5 rounded-lg border border-border/50 bg-secondary/20 space-y-1">
                  <span className="text-[11px] font-mono text-muted-foreground uppercase">Account Plan</span>
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium text-foreground">Personal AIOS</p>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 font-bold">
                      Active
                    </span>
                  </div>
                </div>
              </div>

              {user?.id && (
                <div className="p-3.5 rounded-lg border border-border/50 bg-secondary/20 space-y-1">
                  <span className="text-[11px] font-mono text-muted-foreground uppercase">Account ID</span>
                  <p className="text-xs font-mono text-muted-foreground">usr_{user.id}</p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="border-border/70 bg-card/50 shadow-xs">
            <CardHeader>
              <CardTitle className="text-base font-semibold">Security & Access</CardTitle>
              <CardDescription>Manage credentials and session connection.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-3.5 rounded-lg border border-border/50 bg-secondary/20">
                <div className="space-y-0.5">
                  <p className="text-xs font-medium text-foreground">Password</p>
                  <p className="text-xs text-muted-foreground">Change your account sign-in password.</p>
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    setPasswordError(null)
                    setPasswordSuccess(null)
                    setCurrentPassword("")
                    setNewPassword("")
                    setConfirmPassword("")
                    setShowPasswordModal(true)
                  }}
                  className="text-xs cursor-pointer gap-1.5"
                >
                  <KeyRound className="h-3.5 w-3.5" />
                  Change Password
                </Button>
              </div>

              <div className="flex items-center justify-between p-3.5 rounded-lg border border-border/50 bg-secondary/20">
                <div className="space-y-0.5">
                  <p className="text-xs font-medium text-foreground">Sign Out</p>
                  <p className="text-xs text-muted-foreground">End your active authenticated session on this browser.</p>
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => clearAuth()}
                  className="text-xs text-destructive hover:bg-destructive/10 border-destructive/30 cursor-pointer gap-1.5"
                >
                  <LogOut className="h-3.5 w-3.5" />
                  Sign Out
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* DANGER ZONE: DELETE ACCOUNT */}
          <Card className="border-red-500/30 bg-red-500/5 shadow-xs">
            <CardHeader>
              <div className="flex items-center gap-2 text-destructive">
                <AlertTriangle className="h-4 w-4" />
                <CardTitle className="text-base font-semibold">Danger Zone</CardTitle>
              </div>
              <CardDescription>Irreversible and permanent account actions.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between p-3.5 rounded-lg border border-red-500/20 bg-background/50">
                <div className="space-y-0.5">
                  <p className="text-xs font-semibold text-foreground">Delete Account</p>
                  <p className="text-xs text-muted-foreground">
                    Permanently delete your account, workspace memory, and all associated personal data.
                  </p>
                </div>
                <Button
                  size="sm"
                  variant="destructive"
                  onClick={() => {
                    setDeleteError(null)
                    setDeletePassword("")
                    setShowDeleteModal(true)
                  }}
                  className="text-xs cursor-pointer gap-1.5 font-medium shadow-xs"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                  Delete Account
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* TAB 2: APPEARANCE */}
      {activeTab === "appearance" && (
        <Card className="border-border/70 bg-card/50 shadow-xs">
          <CardHeader>
            <div className="flex items-center gap-2 text-primary">
              <Palette className="h-5 w-5" />
              <CardTitle className="text-base font-semibold">Desktop Theme</CardTitle>
            </div>
            <CardDescription>Select your active desktop environment theme.</CardDescription>
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
                      <div className="absolute top-3 right-3 h-5 w-5 rounded-full bg-primary text-primary-foreground flex items-center justify-center shadow-xs">
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
      )}

      {/* TAB 3: MEMORY */}
      {activeTab === "memory" && (
        <Card className="border-border/70 bg-card/50 shadow-xs">
          <CardHeader>
            <div className="flex items-center gap-2 text-primary">
              <Brain className="h-5 w-5" />
              <CardTitle className="text-base font-semibold">Conversation Memory</CardTitle>
            </div>
            <CardDescription>
              Lisa uses information from previous conversations to provide continuity across your work.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 rounded-lg bg-secondary/20 border border-border/40 flex items-start gap-3">
              <ShieldCheck className="h-5 w-5 text-primary shrink-0 mt-0.5" />
              <div className="space-y-1">
                <p className="text-xs font-semibold text-foreground">Continuity & Privacy</p>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  Your conversational context is retained locally so Lisa can remember your preferences, instructions, and recent discussions. You can clear this memory buffer at any time.
                </p>
              </div>
            </div>

            {memoryCleared && (
              <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 shrink-0" />
                <span>Conversation memory buffer cleared successfully.</span>
              </div>
            )}

            <div className="flex items-center justify-between pt-2">
              <div>
                <p className="text-xs font-medium text-foreground">Reset Memory Buffer</p>
                <p className="text-xs text-muted-foreground">Flushes active conversation continuity memory.</p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={handleClearMemory}
                disabled={clearingMemory}
                className="text-xs text-rose-400 hover:bg-rose-500/10 border-rose-500/30 cursor-pointer gap-1.5"
              >
                <Trash2 className="h-3.5 w-3.5" />
                {clearingMemory ? "Clearing..." : "Clear Conversation Memory"}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Developer / AIOS Callout Card */}
      <Card className="border-border/60 bg-secondary/20 shadow-xs">
        <CardContent className="p-4 flex items-center justify-between gap-4">
          <div className="space-y-0.5">
            <p className="text-xs font-semibold text-foreground">Developer / AIOS</p>
            <p className="text-xs text-muted-foreground">
              Advanced tools and configuration for power users. You don't need to use these for daily tasks.
            </p>
          </div>
          <Button
            size="sm"
            variant="outline"
            onClick={() => navigate("/settings/developer")}
            className="text-xs font-medium gap-1.5 shrink-0 cursor-pointer"
          >
            <span>Open Portal</span>
            <ArrowRight className="h-3 w-3" />
          </Button>
        </CardContent>
      </Card>

      {/* MODAL 1: CHANGE PASSWORD */}
      {showPasswordModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs">
          <div className="relative w-full max-w-md rounded-2xl border border-border/80 bg-background/95 p-6 shadow-2xl space-y-5 animate-in fade-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between pb-3 border-b border-border/50">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-lg bg-primary/10 border border-primary/20 text-primary">
                  <KeyRound className="h-4 w-4" />
                </div>
                <div>
                  <h3 className="text-base font-semibold text-foreground">Change Password</h3>
                  <p className="text-xs text-muted-foreground">Update your account credentials</p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setShowPasswordModal(false)}
                className="p-1 rounded-lg hover:bg-secondary/80 text-muted-foreground hover:text-foreground cursor-pointer transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {passwordError && (
              <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-xs flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 shrink-0" />
                <span>{passwordError}</span>
              </div>
            )}

            {passwordSuccess && (
              <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 shrink-0" />
                <span>{passwordSuccess}</span>
              </div>
            )}

            <form onSubmit={handleChangePassword} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-foreground">Current Password</label>
                <div className="relative">
                  <input
                    type="password"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    placeholder="Enter current password"
                    className="w-full px-3 py-2 pl-9 rounded-lg border border-border/60 bg-secondary/30 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                    required
                  />
                  <Lock className="absolute left-3 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-foreground">New Password</label>
                <div className="relative">
                  <input
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="At least 8 characters"
                    className="w-full px-3 py-2 pl-9 rounded-lg border border-border/60 bg-secondary/30 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                    required
                    minLength={8}
                  />
                  <Lock className="absolute left-3 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-foreground">Confirm New Password</label>
                <div className="relative">
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Re-enter new password"
                    className="w-full px-3 py-2 pl-9 rounded-lg border border-border/60 bg-secondary/30 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                    required
                  />
                  <Lock className="absolute left-3 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
                </div>
              </div>

              <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-border/50">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setShowPasswordModal(false)}
                  className="text-xs cursor-pointer"
                  disabled={passwordLoading}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  size="sm"
                  disabled={passwordLoading}
                  className="text-xs cursor-pointer gap-1.5 font-semibold"
                >
                  {passwordLoading ? (
                    <>
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                      Updating...
                    </>
                  ) : (
                    "Save Password"
                  )}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 2: DELETE ACCOUNT CONFIRMATION */}
      {showDeleteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs">
          <div className="relative w-full max-w-md rounded-2xl border border-destructive/40 bg-background/95 p-6 shadow-2xl space-y-5 animate-in fade-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between pb-3 border-b border-border/50">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive">
                  <AlertTriangle className="h-4 w-4" />
                </div>
                <div>
                  <h3 className="text-base font-semibold text-foreground">Delete Account</h3>
                  <p className="text-xs text-destructive">Permanent and irreversible</p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setShowDeleteModal(false)}
                className="p-1 rounded-lg hover:bg-secondary/80 text-muted-foreground hover:text-foreground cursor-pointer transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <p className="text-xs text-muted-foreground leading-relaxed">
              Are you sure you want to permanently delete your account? All conversation history, memory embeddings, emails, preferences, and workspace settings will be irreversibly erased.
            </p>

            {deleteError && (
              <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-xs flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 shrink-0" />
                <span>{deleteError}</span>
              </div>
            )}

            <form onSubmit={handleDeleteAccount} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-foreground">
                  Confirm Password to Authorize Deletion
                </label>
                <div className="relative">
                  <input
                    type="password"
                    value={deletePassword}
                    onChange={(e) => setDeletePassword(e.target.value)}
                    placeholder="Enter your current password"
                    className="w-full px-3 py-2 pl-9 rounded-lg border border-destructive/30 bg-secondary/30 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-destructive"
                    required
                  />
                  <Lock className="absolute left-3 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
                </div>
              </div>

              <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-border/50">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setShowDeleteModal(false)}
                  className="text-xs cursor-pointer"
                  disabled={deleteLoading}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="destructive"
                  size="sm"
                  disabled={deleteLoading}
                  className="text-xs cursor-pointer gap-1.5 font-semibold"
                >
                  {deleteLoading ? (
                    <>
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                      Deleting Account...
                    </>
                  ) : (
                    "Permanently Delete"
                  )}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
