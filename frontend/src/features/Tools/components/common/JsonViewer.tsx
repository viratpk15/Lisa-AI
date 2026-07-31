import { useState } from "react"
import { Copy, Check, ChevronDown, ChevronRight } from "lucide-react"

interface JsonViewerProps {
  data: Record<string, any> | Array<any> | null
  title?: string
  defaultExpanded?: boolean
}

export function JsonViewer({ data, title, defaultExpanded = true }: JsonViewerProps) {
  const [copied, setCopied] = useState(false)
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)

  if (!data) return <div className="text-xs text-muted-foreground italic">No data</div>

  const jsonString = JSON.stringify(data, null, 2)

  const handleCopy = () => {
    navigator.clipboard.writeText(jsonString)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="bg-[#0D1117] border border-border/40 rounded-lg overflow-hidden font-mono text-xs shadow-inner">
      {title && (
        <div className="flex items-center justify-between px-3 py-2 bg-secondary/40 border-b border-border/40 text-muted-foreground select-none">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center gap-1.5 font-semibold hover:text-foreground cursor-pointer transition-colors"
          >
            {isExpanded ? <ChevronDown className="h-3.5 w-3.5" /> : <ChevronRight className="h-3.5 w-3.5" />}
            <span>{title}</span>
          </button>
          <button
            onClick={handleCopy}
            className="flex items-center gap-1 px-2 py-0.5 text-[10px] bg-secondary/60 hover:bg-secondary text-muted-foreground hover:text-foreground border border-border/50 rounded cursor-pointer transition-all"
          >
            {copied ? (
              <>
                <Check className="h-3 w-3 text-emerald-400" />
                <span className="text-emerald-400 font-semibold">Copied</span>
              </>
            ) : (
              <>
                <Copy className="h-3 w-3" />
                <span>Copy JSON</span>
              </>
            )}
          </button>
        </div>
      )}

      {isExpanded && (
        <div className="p-3 overflow-x-auto text-[#C9D1D9] leading-relaxed max-h-87.5 scrollbar-thin">
          <pre className="whitespace-pre-wrap break-all">{jsonString}</pre>
        </div>
      )}
    </div>
  )
}
