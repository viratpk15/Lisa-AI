import React, { useState } from "react"
import { Copy, Check, ChevronDown, ChevronRight, WrapText, Download } from "lucide-react"

interface CodeBlockProps {
  code: string
  language: string
}

export const CodeBlock: React.FC<CodeBlockProps> = ({ code, language }) => {
  const [copied, setCopied] = useState(false)
  const [collapsed, setCollapsed] = useState(false)
  const [lineWrap, setLineWrap] = useState(true)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error("Failed to copy text:", err)
    }
  }

  const handleDownload = () => {
    const extMap: Record<string, string> = {
      python: "py",
      javascript: "js",
      typescript: "ts",
      jsx: "jsx",
      tsx: "tsx",
      html: "html",
      css: "css",
      json: "json",
      sql: "sql",
      sh: "sh",
      bash: "sh",
      markdown: "md",
    }
    const ext = extMap[language.toLowerCase()] || "txt"
    const blob = new Blob([code], { type: "text/plain;charset=utf-8" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `code-snippet.${ext}`
    a.click()
    URL.revokeObjectURL(url)
  }

  // Visual syntax highlighting simulation by formatting key symbols
  const highlightCode = (rawCode: string, _lang: string) => {
    const lines = rawCode.split("\n")
    return lines.map((line, idx) => {
      let highlightedLine = line
        .replace(/(\bconst\b|\blet\b|\bvar\b|\bfunction\b|\breturn\b|\bimport\b|\bexport\b|\bfrom\b|\bclass\b|\btype\b|\binterface\b|\bdef\b|\basync\b|\bawait\b)/g, '<span class="text-violet-400 font-semibold">$1</span>')
        .replace(/(\bif\b|\belse\b|\bfor\b|\bwhile\b|\bswitch\b|\bcase\b|\bbreak\b|\btry\b|\bexcept\b|\bcatch\b)/g, '<span class="text-pink-400 font-semibold">$1</span>')
        .replace(/(["'`])(.*?)\1/g, '<span class="text-emerald-300">"$2"</span>')
        .replace(/(\/\/.*|#.*)$/g, '<span class="text-zinc-500 italic">$1</span>')

      return (
        <div key={idx} className="table-row">
          <span className="table-cell select-none text-right pr-4 text-[10px] text-zinc-600 font-mono w-8">
            {idx + 1}
          </span>
          <span
            className="table-cell text-xs font-mono text-zinc-300 whitespace-pre"
            dangerouslySetInnerHTML={{ __html: highlightedLine || " " }}
          />
        </div>
      )
    })
  }

  return (
    <div className="border border-border/80 rounded-lg overflow-hidden bg-black/45 backdrop-blur-sm select-text">
      {/* Header bar */}
      <div className="flex items-center justify-between px-4 py-2 bg-secondary/30 border-b border-border/60 text-xs font-mono select-none">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-0.5 rounded hover:bg-secondary text-muted-foreground hover:text-foreground cursor-pointer focus:outline-none focus:ring-1 focus:ring-primary"
            aria-label={collapsed ? "Expand code block" : "Collapse code block"}
            title={collapsed ? "Expand code" : "Collapse code"}
          >
            {collapsed ? <ChevronRight className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
          </button>
          <span className="text-[10px] font-bold text-primary bg-primary/10 border border-primary/20 px-2 py-0.5 rounded-full uppercase tracking-wider">
            {language}
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* Download Button */}
          <button
            onClick={handleDownload}
            className="p-1 rounded hover:bg-secondary text-muted-foreground hover:text-foreground cursor-pointer focus:outline-none transition-colors"
            aria-label="Download code snippet"
            title="Download code snippet"
          >
            <Download className="h-3.5 w-3.5" />
          </button>

          {/* Line Wrap Toggle */}
          <button
            onClick={() => setLineWrap(!lineWrap)}
            className={`p-1 rounded hover:bg-secondary cursor-pointer focus:outline-none transition-colors ${lineWrap ? "text-primary bg-primary/5" : "text-muted-foreground hover:text-foreground"}`}
            aria-label="Toggle line wrap"
            title="Toggle Line Wrap"
          >
            <WrapText className="h-3.5 w-3.5" />
          </button>

          {/* Copy Button */}
          <button
            onClick={handleCopy}
            className="p-1 rounded hover:bg-secondary text-muted-foreground hover:text-foreground cursor-pointer focus:outline-none transition-colors flex items-center gap-1 text-[10px] font-semibold"
            aria-label="Copy code to clipboard"
            title="Copy Code"
          >
            {copied ? (
              <>
                <Check className="h-3.5 w-3.5 text-emerald-400" />
                <span className="text-emerald-400 font-mono">Copied</span>
              </>
            ) : (
              <>
                <Copy className="h-3.5 w-3.5" />
                <span className="font-mono">Copy</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Code Area */}
      {!collapsed && (
        <div className={`p-4 font-mono overflow-x-auto bg-transparent ${lineWrap ? "whitespace-pre-wrap break-all" : "whitespace-pre"}`}>
          <div className="table w-full">
            {highlightCode(code, language)}
          </div>
        </div>
      )}
    </div>
  )
}
