/**
 * Lisa AIOS — Travel Planner Booking Safety Confirmation Modal
 * Enforces explicit user confirmation before opening external booking providers.
 */

import { useState } from "react"
import { ShieldCheck, ExternalLink, AlertTriangle, Loader2 } from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { usePrepareBookingMutation } from "../queries"

interface BookingItemDetails {
  itemType: "flight" | "hotel" | "activity" | "transport"
  itemId: string
  title: string
  providerName: string
  priceText?: string
  deepLink?: string
}

interface BookingConfirmationModalProps {
  isOpen: boolean
  onClose: () => void
  tripId: string
  item: BookingItemDetails | null
}

export function BookingConfirmationModal({
  isOpen,
  onClose,
  tripId,
  item,
}: BookingConfirmationModalProps) {
  const [confirmed, setConfirmed] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const prepareBooking = usePrepareBookingMutation()

  if (!item) return null

  const handleProceed = async () => {
    if (!confirmed) return
    setErrorMessage(null)

    try {
      const response = await prepareBooking.mutateAsync({
        trip_id: tripId,
        item_type: item.itemType,
        item_id: item.itemId,
        user_confirmed: true,
      })

      const targetUrl = response.action_url || item.deepLink
      if (targetUrl) {
        window.open(targetUrl, "_blank", "noopener,noreferrer")
        onClose()
      } else {
        setErrorMessage("Provider URL could not be resolved. Please try again.")
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to prepare booking action"
      setErrorMessage(msg)
    }
  }

  const handleOpenChange = (open: boolean) => {
    if (!open) {
      setConfirmed(false)
      setErrorMessage(null)
      onClose()
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogContent className="max-w-md bg-card/95 border-border/80 backdrop-blur-md shadow-2xl p-6 rounded-2xl">
        <DialogHeader className="space-y-2">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-primary/10 text-primary border border-primary/20">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <div>
              <DialogTitle className="text-lg font-bold text-foreground">
                External Booking Redirect
              </DialogTitle>
              <DialogDescription className="text-xs text-muted-foreground">
                Verified Provider Safety Gate
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-4 my-2">
          {/* Target Item Summary */}
          <div className="p-3.5 rounded-xl bg-secondary/50 border border-border/60 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold uppercase tracking-wider text-muted-foreground text-[10px]">
                {item.itemType}
              </span>
              <span className="font-medium text-primary bg-primary/10 px-2 py-0.5 rounded-md border border-primary/20">
                {item.providerName}
              </span>
            </div>
            <p className="text-sm font-semibold text-foreground">{item.title}</p>
            {item.priceText && (
              <p className="text-xs font-mono font-medium text-muted-foreground">
                Indicative Price: <span className="text-foreground font-semibold">{item.priceText}</span>
              </p>
            )}
          </div>

          {/* Safety Notice Banner */}
          <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/25 text-amber-500 flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 shrink-0 mt-0.5" />
            <div className="space-y-1 text-xs text-amber-500/90 leading-relaxed">
              <p className="font-semibold text-amber-400">Zero Autonomous Charges Policy</p>
              <p>
                Lisa AIOS never stores credit cards, commits payment funds, or books tickets autonomously.
                You are being safely redirected to the verified provider portal to verify live availability and complete booking directly.
              </p>
            </div>
          </div>

          {/* Checkbox gate */}
          <label className="flex items-start gap-2.5 cursor-pointer select-none text-xs text-muted-foreground p-1">
            <input
              type="checkbox"
              checked={confirmed}
              onChange={(e) => setConfirmed(e.target.checked)}
              className="mt-0.5 rounded border-border text-primary focus:ring-primary h-4 w-4 cursor-pointer"
            />
            <span>
              I understand that I am leaving Lisa AIOS to review live seat/room availability and finalize payment directly with{" "}
              <strong className="text-foreground">{item.providerName}</strong>.
            </span>
          </label>

          {errorMessage && (
            <p className="text-xs text-destructive font-medium bg-destructive/10 p-2.5 rounded-lg border border-destructive/20">
              {errorMessage}
            </p>
          )}
        </div>

        <DialogFooter className="gap-2 sm:gap-0 mt-2">
          <Button
            variant="ghost"
            onClick={() => handleOpenChange(false)}
            disabled={prepareBooking.isPending}
            className="text-xs cursor-pointer"
          >
            Cancel
          </Button>
          <Button
            onClick={handleProceed}
            disabled={!confirmed || prepareBooking.isPending}
            className="gap-2 text-xs font-medium cursor-pointer"
          >
            {prepareBooking.isPending ? (
              <>
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                <span>Preparing Portal...</span>
              </>
            ) : (
              <>
                <span>Proceed to {item.providerName}</span>
                <ExternalLink className="h-3.5 w-3.5" />
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
