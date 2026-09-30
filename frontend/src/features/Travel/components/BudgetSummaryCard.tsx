/**
 * Lisa AIOS — Trip Budget & Financial Breakdown
 * Transparently isolates verified prices vs estimated expenses with progress meter & health status.
 */

import {
  DollarSign,
  ShieldCheck,
  Calculator,
  AlertCircle,
  CheckCircle2,
} from "lucide-react"
import type { TripBudget, BudgetCategory } from "../types"
import { formatCurrency } from "../types"

interface BudgetSummaryCardProps {
  budget: TripBudget
  currency: string
}

export function BudgetSummaryCard({
  budget,
  currency,
}: BudgetSummaryCardProps) {
  const isExceeded = budget.status === "exceeded"
  const isWithin = budget.status === "within_budget"
  const hasUserBudget = budget.user_budget > 0

  const formatAmount = (amt: number) => {
    return formatCurrency(amt, currency)
  }

  // Calculate percentage for progress bars
  const totalSpend = budget.total_projected || 1
  const verifiedPercent = Math.min(100, Math.round((budget.total_verified / totalSpend) * 100))
  const estimatedPercent = 100 - verifiedPercent

  return (
    <div className="rounded-2xl border border-border/70 bg-card/60 backdrop-blur-md p-5 sm:p-6 shadow-xs space-y-5">
      {/* Header & Status Indicator */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <DollarSign className="h-4 w-4" />
            </span>
            <h3 className="text-base font-semibold text-foreground">Trip Financial Breakdown</h3>
          </div>
          <p className="text-xs text-muted-foreground mt-0.5">
            Strict isolation between verified provider fares and estimated on-the-ground spending.
          </p>
        </div>

        {/* Health status badge */}
        <div className="flex items-center gap-2 self-start sm:self-auto">
          {hasUserBudget && (
            <div
              className={`px-3 py-1 rounded-xl text-xs font-semibold border flex items-center gap-1.5 ${
                isExceeded
                  ? "bg-rose-500/10 text-rose-400 border-rose-500/30"
                  : isWithin
                  ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                  : "bg-secondary text-muted-foreground border-border"
              }`}
            >
              {isExceeded ? (
                <>
                  <AlertCircle className="h-3.5 w-3.5" />
                  <span>Exceeds Target by {formatAmount(Math.abs(budget.remaining_balance))}</span>
                </>
              ) : (
                <>
                  <CheckCircle2 className="h-3.5 w-3.5" />
                  <span>Under Budget ({formatAmount(budget.remaining_balance)} left)</span>
                </>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Summary Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
        {/* User Target Budget */}
        {hasUserBudget && (
          <div className="p-3.5 rounded-xl bg-secondary/30 border border-border/50 space-y-1">
            <span className="text-[11px] font-medium text-muted-foreground">Target Budget</span>
            <div className="text-xl font-bold font-mono text-foreground">
              {formatAmount(budget.user_budget)}
            </div>
          </div>
        )}

        {/* Total Projected */}
        <div className="p-3.5 rounded-xl bg-secondary/30 border border-border/50 space-y-1">
          <span className="text-[11px] font-medium text-muted-foreground">Projected Total</span>
          <div className="text-xl font-bold font-mono text-foreground">
            {formatAmount(budget.total_projected)}
          </div>
        </div>

        {/* Verified Quote Total */}
        <div className="p-3.5 rounded-xl bg-emerald-500/5 border border-emerald-500/20 space-y-1">
          <span className="text-[11px] font-medium text-emerald-400 flex items-center gap-1">
            <ShieldCheck className="h-3.5 w-3.5" />
            Verified Fares
          </span>
          <div className="text-xl font-bold font-mono text-emerald-400">
            {formatAmount(budget.total_verified)}
          </div>
        </div>

        {/* Estimated Expenses */}
        <div className="p-3.5 rounded-xl bg-sky-500/5 border border-sky-500/20 space-y-1">
          <span className="text-[11px] font-medium text-sky-400 flex items-center gap-1">
            <Calculator className="h-3.5 w-3.5" />
            Estimated Costs
          </span>
          <div className="text-xl font-bold font-mono text-sky-400">
            {formatAmount(budget.total_estimated)}
          </div>
        </div>
      </div>

      {/* Spend Meter */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between text-xs text-muted-foreground font-mono">
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-emerald-400" />
            Verified Quotes ({verifiedPercent}%)
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-sky-400" />
            Estimated On-Ground ({estimatedPercent}%)
          </span>
        </div>
        <div className="h-2.5 w-full rounded-full bg-secondary/60 overflow-hidden flex">
          <div
            className="h-full bg-emerald-500 transition-all duration-500"
            style={{ width: `${verifiedPercent}%` }}
          />
          <div
            className="h-full bg-sky-500 transition-all duration-500"
            style={{ width: `${estimatedPercent}%` }}
          />
        </div>
      </div>

      {/* Itemized Categories Table */}
      <div className="space-y-2">
        <span className="text-xs font-semibold text-foreground uppercase tracking-wider text-[10px]">
          Itemized Category Breakdown
        </span>

        <div className="rounded-xl border border-border/60 overflow-hidden">
          <table className="w-full text-left text-xs">
            <thead className="bg-secondary/40 text-muted-foreground border-b border-border/60 font-mono text-[11px]">
              <tr>
                <th className="py-2 px-3.5 font-medium">Category</th>
                <th className="py-2 px-3.5 font-medium">Verified Amount</th>
                <th className="py-2 px-3.5 font-medium">Estimated Amount</th>
                <th className="py-2 px-3.5 font-medium hidden sm:table-cell">Basis / Notes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40 font-mono text-xs">
              {budget.categories.map((cat: BudgetCategory, idx: number) => (
                <tr key={idx} className="hover:bg-secondary/20 transition-colors">
                  <td className="py-2.5 px-3.5 font-sans font-medium text-foreground">
                    {cat.category}
                  </td>
                  <td className="py-2.5 px-3.5 text-emerald-400 font-semibold">
                    {cat.verified_amount > 0 ? formatAmount(cat.verified_amount) : "—"}
                  </td>
                  <td className="py-2.5 px-3.5 text-sky-400">
                    {cat.estimated_amount > 0 ? formatAmount(cat.estimated_amount) : "—"}
                  </td>
                  <td className="py-2.5 px-3.5 font-sans text-muted-foreground text-[11px] hidden sm:table-cell">
                    {cat.notes}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Mandatory Transparency Disclaimer */}
      <p className="text-[11px] text-muted-foreground/80 leading-relaxed italic border-t border-border/40 pt-3">
        ● {budget.disclaimer}
      </p>
    </div>
  )
}
