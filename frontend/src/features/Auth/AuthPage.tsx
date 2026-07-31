import React, { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Shield, Sparkles, AlertCircle, Eye, EyeOff, Loader2 } from "lucide-react"
import { useLoginMutation, useRegisterMutation } from "@/services/queries/auth"
import type { NormalizedError } from "@/services/api/errors"

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [localError, setLocalError] = useState<string | null>(null)

  const loginMutation = useLoginMutation()
  const registerMutation = useRegisterMutation()

  const handleToggleMode = () => {
    setIsLogin(!isLogin)
    setLocalError(null)
    setPassword("")
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLocalError(null)

    // Client-side validations
    if (!email.trim() || !password.trim()) {
      setLocalError("Email and password fields are required.")
      return
    }

    if (password.length < 8) {
      setLocalError("Password must be at least 8 characters long.")
      return
    }

    try {
      if (isLogin) {
        // Execute login
        await loginMutation.mutateAsync({ email: email.trim(), password })
      } else {
        // Execute registration
        await registerMutation.mutateAsync({ email: email.trim(), password })
        // Autologin after registration success
        await loginMutation.mutateAsync({ email: email.trim(), password })
      }
    } catch (err: unknown) {
      // The queries layer throws normalized APIError structures
      const normErr = err as NormalizedError
      if (normErr.details) {
        const detailsStr = Object.entries(normErr.details)
          .map(([key, val]) => `${key}: ${val}`)
          .join(", ")
        setLocalError(`${normErr.message} (${detailsStr})`)
      } else {
        setLocalError(normErr.message || "An authentication error occurred.")
      }
    }
  }

  const isLoading = loginMutation.isPending || registerMutation.isPending

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4 relative overflow-hidden select-none">
      {/* Background ambient mesh gradients */}
      <div className="absolute top-1/4 left-1/4 h-87.5 w-87.5 bg-primary/10 rounded-full blur-3xl pointer-events-none animate-pulse" />
      <div className="absolute bottom-1/4 right-1/4 h-100 w-100 bg-violet-600/5 rounded-full blur-3xl pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-md p-7 border border-border/80 bg-card/35 backdrop-blur-md rounded-2xl shadow-xl flex flex-col relative z-10"
      >
        {/* Brand header */}
        <div className="flex flex-col items-center mb-7">
          <div className="relative mb-3 flex items-center justify-center p-3.5 bg-primary/10 border border-primary/20 rounded-xl">
            <Shield className="h-6 w-6 text-primary" />
            <div className="absolute -top-0.5 -right-0.5 h-2 w-2 rounded-full bg-primary" />
          </div>
          <h1 className="text-lg font-extrabold tracking-tight text-foreground flex items-center gap-1.5 leading-none">
            Jarvis AIOS
            <span className="text-[10px] font-mono font-medium border border-primary/20 text-primary bg-primary/5 px-2 py-0.5 rounded-full uppercase tracking-wider scale-90">
              V1.1
            </span>
          </h1>
          <p className="text-xs text-muted-foreground mt-2 leading-relaxed text-center">
            {isLogin ? "Synchronize workspace session parameters" : "Create standard authentication credentials"}
          </p>
        </div>

        {/* Local/Server Errors Alert banner */}
        <AnimatePresence mode="wait">
          {localError && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-4 overflow-hidden"
            >
              <div className="flex gap-2 p-3 border border-red-500/20 bg-red-500/5 rounded-xl text-xs text-red-400 font-semibold leading-relaxed">
                <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                <span>{localError}</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Auth form fields */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider font-mono">
              Email Address
            </label>
            <input
              type="email"
              disabled={isLoading}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@company.com"
              className="w-full px-3 py-2 bg-secondary/25 border border-border/80 hover:border-primary/25 rounded-lg text-xs text-foreground outline-none focus:ring-1 focus:ring-primary focus:border-primary placeholder:text-muted-foreground/45 transition-colors font-mono"
            />
          </div>

          <div className="space-y-1.5 relative">
            <div className="flex items-center justify-between">
              <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider font-mono">
                Password
              </label>
            </div>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                disabled={isLoading}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-3 pr-9 py-2 bg-secondary/25 border border-border/80 hover:border-primary/25 rounded-lg text-xs text-foreground outline-none focus:ring-1 focus:ring-primary focus:border-primary placeholder:text-muted-foreground/45 transition-colors font-mono"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-2.5 top-1.75 text-muted-foreground hover:text-foreground cursor-pointer focus:outline-none"
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>

          {/* Submit button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full mt-2 py-2 border border-primary/25 bg-primary/10 hover:bg-primary text-foreground hover:text-primary-foreground font-semibold text-xs rounded-xl cursor-pointer transition-all flex items-center justify-center gap-2 shadow-md shadow-primary/5 focus:outline-none focus:ring-1 focus:ring-primary disabled:opacity-40 disabled:hover:bg-primary/10 disabled:hover:text-foreground disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin text-primary" />
                <span>Synchronizing...</span>
              </>
            ) : (
              <>
                <Sparkles className="h-3.5 w-3.5" />
                <span>{isLogin ? "Access System Kernel" : "Register Credentials"}</span>
              </>
            )}
          </button>
        </form>

        {/* Footer toggling triggers */}
        <div className="mt-6 border-t border-border/60 pt-4 text-center">
          <button
            onClick={handleToggleMode}
            disabled={isLoading}
            className="text-[10px] font-mono font-semibold text-primary hover:underline cursor-pointer disabled:opacity-40"
          >
            {isLogin ? "Initialize New Security Profile" : "Existing User? Sync Session Token"}
          </button>
        </div>
      </motion.div>
    </div>
  )
}
