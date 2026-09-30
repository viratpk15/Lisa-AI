// frontend/src/features/Email/SenderAuthBadge.tsx
import React from "react"
import { ShieldCheck, ShieldAlert } from "lucide-react"

interface SenderAuthBadgeProps {
  isVerified: boolean
  spfStatus?: string
  dkimStatus?: string
  dmarcStatus?: string
  className?: string
}

export const SenderAuthBadge: React.FC<SenderAuthBadgeProps> = ({
  isVerified,
  spfStatus = "unknown",
  dkimStatus = "unknown",
  dmarcStatus = "unknown",
  className = "",
}) => {
  if (isVerified) {
    return (
      <span
        title={`SPF: ${spfStatus} | DKIM: ${dkimStatus} | DMARC: ${dmarcStatus}`}
        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 ${className}`}
      >
        <ShieldCheck className="w-3 h-3 text-emerald-400" />
        <span>✓ Verified</span>
      </span>
    )
  }

  return (
    <span
      title={`SPF: ${spfStatus} | DKIM: ${dkimStatus} | DMARC: ${dmarcStatus}`}
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-amber-500/15 text-amber-400 border border-amber-500/30 ${className}`}
    >
      <ShieldAlert className="w-3 h-3 text-amber-400" />
      <span>⚠ Unverified</span>
    </span>
  )
}
