import { useRef, useEffect } from "react"
import { Terminal, Pause, Play, Trash2, Copy, Download, ArrowDown } from "lucide-react"
import { useToolConsoleStore } from "../../store/useToolConsoleStore"
import type { ConsoleLogEntry } from "../../types/tools.types"

export function ExecutionConsole() {
  const consoleLogs = useToolConsoleStore((s) => s.consoleLogs)
  const clearConsoleLogs = useToolConsoleStore((s) => s.clearConsoleLogs)
  const isStreaming = useToolConsoleStore((s) => s.isStreaming)
  const autoScroll = useToolConsoleStore((s) => s.autoScroll)
  const setAutoScroll = useToolConsoleStore((s) => s.setAutoScroll)
  const isPaused = useToolConsoleStore((s) => s.isPaused)
  const setIsPaused = useToolConsoleStore((s) => s.setIsPaused)

  const logEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (autoScroll && !isPaused) {
      logEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }
  }, [consoleLogs, autoScroll, isPaused])

  const handleCopy = () => {
    const text = consoleLogs.map((l) => `[${l.timestamp}] [${l.type.toUpperCase()}] ${l.message}`).join("\n")
    navigator.clipboard.writeText(text)
  }

  const handleDownload = () => {
    const text = consoleLogs.map((l) => `[${l.timestamp}] [${l.type.toUpperCase()}] ${l.message}`).join("\n")
    const blob = new Blob([text], { type: "text/plain" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `jarvis_tool_console_${Date.now()}.log`
    a.click()
    URL.revokeObjectURL(url)
  }

  const getLogColor = (type: ConsoleLogEntry["type"]) => {
    switch (type) {
      case "stdout":
        return "text-cyan-400"
      case "stderr":
        return "text-rose-400 font-semibold"
      case "info":
        return "text-blue-400"
      case "warning":
        return "text-amber-400"
      case "success":
        return "text-emerald-400 font-semibold"
      default:
        return "text-gray-300"
    }
  }

  return (
    <div className="bg-[#090D16] border border-border/40 rounded-xl overflow-hidden font-mono flex flex-col h-100">
      {/* Console Header Toolbar */}
      <div className="h-10 px-3 bg-[#121826]/90 border-b border-border/40 flex items-center justify-between text-xs text-muted-foreground select-none">
        <div className="flex items-center gap-2">
          <Terminal className="h-3.5 w-3.5 text-cyan-400" />
          <span className="font-bold text-foreground">Execution Terminal Console</span>
          {isStreaming && (
            <span className="flex items-center gap-1 text-[10px] text-violet-400 bg-violet-500/10 border border-violet-500/30 px-2 py-0.5 rounded-full font-semibold">
              <span className="h-1.5 w-1.5 rounded-full bg-violet-400 animate-ping" />
              Streaming SSE
            </span>
          )}
        </div>

        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setAutoScroll(!autoScroll)}
            className={`p-1.5 rounded cursor-pointer transition-colors ${
              autoScroll ? "text-cyan-400 bg-cyan-500/10" : "text-muted-foreground hover:text-foreground"
            }`}
            title="Toggle Auto-Scroll"
          >
            <ArrowDown className="h-3.5 w-3.5" />
          </button>

          <button
            onClick={() => setIsPaused(!isPaused)}
            className={`p-1.5 rounded cursor-pointer transition-colors ${
              isPaused ? "text-amber-400 bg-amber-500/10" : "text-muted-foreground hover:text-foreground"
            }`}
            title={isPaused ? "Resume Console" : "Pause Console"}
          >
            {isPaused ? <Play className="h-3.5 w-3.5" /> : <Pause className="h-3.5 w-3.5" />}
          </button>

          <button
            onClick={handleCopy}
            disabled={consoleLogs.length === 0}
            className="p-1.5 text-muted-foreground hover:text-foreground cursor-pointer rounded disabled:opacity-30"
            title="Copy Logs"
          >
            <Copy className="h-3.5 w-3.5" />
          </button>

          <button
            onClick={handleDownload}
            disabled={consoleLogs.length === 0}
            className="p-1.5 text-muted-foreground hover:text-foreground cursor-pointer rounded disabled:opacity-30"
            title="Download Log File"
          >
            <Download className="h-3.5 w-3.5" />
          </button>

          <button
            onClick={clearConsoleLogs}
            disabled={consoleLogs.length === 0}
            className="p-1.5 text-muted-foreground hover:text-rose-400 cursor-pointer rounded disabled:opacity-30"
            title="Clear Console"
          >
            <Trash2 className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      {/* Terminal Log Output Window */}
      <div className="flex-1 p-3 overflow-y-auto space-y-1 text-xs leading-relaxed scrollbar-thin">
        {consoleLogs.length === 0 ? (
          <div className="h-full flex items-center justify-center text-muted-foreground/50 text-[11px] italic">
            Console log output stream is empty. Execute a tool to stream terminal logs.
          </div>
        ) : (
          consoleLogs.map((entry) => (
            <div key={entry.id} className="flex items-start gap-2 hover:bg-secondary/20 px-1 py-0.5 rounded">
              <span className="text-[10px] text-muted-foreground/60 shrink-0 font-mono select-none">
                [{entry.timestamp}]
              </span>
              <span className={`text-[10px] uppercase font-bold shrink-0 w-14 ${getLogColor(entry.type)}`}>
                [{entry.type}]
              </span>
              <span className="text-xs break-all text-[#C9D1D9] whitespace-pre-wrap">{entry.message}</span>
            </div>
          ))
        )}
        <div ref={logEndRef} />
      </div>
    </div>
  )
}
