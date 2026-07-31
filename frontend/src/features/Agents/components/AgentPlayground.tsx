// frontend/src/features/Agents/components/AgentPlayground.tsx
import { useState } from "react"
import { Play, Bot, Terminal, Cpu, CheckCircle } from "lucide-react"

export default function AgentPlayground() {
  const [prompt, setPrompt] = useState("Analyze the recent performance telemetry and generate an optimization plan.")
  const [isRunning, setIsRunning] = useState(false)
  const [logs, setLogs] = useState<Array<{ step: string; output: string }>>([
    { step: "Thought", output: "User requested performance telemetry analysis. Selecting tool 'telemetry_probe'." },
    { step: "Action", output: "Invoking telemetry_probe({ env: 'prod' }) -> CPU: 24%, RAM: 480MB, Status: Healthy" },
    { step: "Observation", output: "System load is nominal. Generating structured optimization response." },
  ])

  const handleRun = (e: React.FormEvent) => {
    e.preventDefault()
    setIsRunning(true)
    setTimeout(() => {
      setLogs((prev) => [
        ...prev,
        { step: "Thought", output: `Processing prompt: '${prompt}'` },
        { step: "Final Response", output: "Telemetry analysis complete. Recommendations generated." },
      ])
      setIsRunning(false)
    }, 1200)
  }

  return (
    <div className="space-y-4 font-mono text-xs">
      <div className="bg-secondary/15 border border-border/40 p-4 rounded-xl space-y-3">
        <div className="flex items-center gap-2 border-b border-border/40 pb-2">
          <Bot className="h-4 w-4 text-cyan-400" />
          <h3 className="text-xs font-bold text-foreground">Agent Execution Playground & Trace Console</h3>
        </div>

        <form onSubmit={handleRun} className="space-y-2">
          <textarea
            rows={3}
            placeholder="Enter goal or instruction for agent execution..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="w-full p-2.5 bg-secondary/30 border border-border/40 rounded text-foreground text-xs font-mono"
          />
          <button
            type="submit"
            disabled={isRunning}
            className="px-4 py-2 font-bold rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 hover:bg-cyan-500/30 transition-all cursor-pointer flex items-center justify-center gap-1.5 disabled:opacity-50"
          >
            <Play className="h-3.5 w-3.5" />
            {isRunning ? "Executing LangGraph Reasoning Loop..." : "Run Agent Loop"}
          </button>
        </form>
      </div>

      {/* Reasoning Trace Terminal */}
      <div className="bg-[#0D1117] border border-border/40 rounded-xl p-4 space-y-2">
        <div className="flex items-center justify-between border-b border-border/30 pb-2 text-[10px] text-muted-foreground">
          <span className="flex items-center gap-1">
            <Terminal className="h-3.5 w-3.5 text-cyan-400" /> ReAct Reasoning Step Trace
          </span>
          <span className="text-emerald-400 font-bold flex items-center gap-1">
            <CheckCircle className="h-3 w-3" /> LangGraph Active
          </span>
        </div>

        <div className="h-56 overflow-y-auto space-y-2 text-[11px] p-1 font-mono">
          {logs.map((log, index) => (
            <div key={index} className="p-2 bg-secondary/10 border border-border/20 rounded-lg space-y-1">
              <div className="flex items-center gap-2">
                <Cpu className="h-3 w-3 text-cyan-400" />
                <span className="text-cyan-300 font-bold uppercase">{log.step}:</span>
              </div>
              <p className="text-foreground pl-5">{log.output}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}