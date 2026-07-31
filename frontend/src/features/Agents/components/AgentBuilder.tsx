// frontend/src/features/Agents/components/AgentBuilder.tsx
import { useState } from "react"
import { Save, Bot, Cpu, Wrench, Sparkles, CheckCircle, AlertTriangle, Loader2 } from "lucide-react"
import { useCreateAgentMutation } from "../services/agentsApi"

// NOTE on backend contract: backend/app/Agents/schemas.py's AgentCreate only
// accepts `name` and `description` — there is no persisted field yet for
// orchestration pattern, model, system prompt, or tool bindings. Rather than
// silently discarding what the user configures here (or inventing backend
// fields that don't exist), we serialize the full configuration into
// `description` so nothing is lost. When the backend adds first-class
// columns for these, switch this payload to use them directly.
function buildDescription(pattern: string, model: string, systemPrompt: string, tools: string[]): string {
  return JSON.stringify({ pattern, model, system_prompt: systemPrompt, tools })
}

export default function AgentBuilder() {
  const [name, setName] = useState("Custom ReAct Assistant")
  const [pattern, setPattern] = useState("react")
  const [model, setModel] = useState("gemini-2.5-flash")
  const [systemPrompt, setSystemPrompt] = useState("You are an autonomous AI agent capable of breaking down complex problems and selecting tools to execute step-by-step.")
  const [selectedTools, setSelectedTools] = useState<string[]>(["python_interpreter", "web_search"])

  const createAgent = useCreateAgentMutation()

  const availableTools = [
    { id: "python_interpreter", name: "Python REPL Execution" },
    { id: "web_search", name: "Web Search Provider" },
    { id: "rag_retrieval", name: "RAG Vector Store Search" },
    { id: "file_system", name: "Filesystem Workspace Access" },
  ]

  const toggleTool = (toolId: string) => {
    setSelectedTools((prev) =>
      prev.includes(toolId) ? prev.filter((id) => id !== toolId) : [...prev, toolId]
    )
  }

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim()) return
    createAgent.mutate({
      name: name.trim(),
      description: buildDescription(pattern, model, systemPrompt, selectedTools),
    })
  }

  return (
    <div className="space-y-4 font-mono text-xs max-w-4xl">
      <div className="flex items-center justify-between border-b border-border/40 pb-3">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-cyan-400" />
          <h3 className="text-xs font-bold text-foreground">Agent Configuration & Graph Node Builder</h3>
        </div>
        <button
          onClick={handleSave}
          disabled={createAgent.isPending || !name.trim()}
          className="flex items-center gap-1.5 px-3 py-1.5 font-bold rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 hover:bg-cyan-500/30 cursor-pointer transition-all disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {createAgent.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Save className="h-3.5 w-3.5" />}
          Save Agent Version
        </button>
      </div>

      {createAgent.isSuccess && (
        <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-300 flex items-center gap-2">
          <CheckCircle className="h-4 w-4 text-emerald-400 shrink-0" />
          <span>Agent '{createAgent.data?.name}' saved to registry (id {createAgent.data?.id}).</span>
        </div>
      )}

      {createAgent.isError && (
        <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-xl text-red-300 flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-red-400 shrink-0" />
          <span>Failed to save agent: {(createAgent.error as Error)?.message ?? "Unknown error"}</span>
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-4">
        {/* Agent Metadata */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="space-y-1">
            <label className="text-[10px] text-muted-foreground uppercase font-bold flex items-center gap-1">
              <Bot className="h-3 w-3 text-cyan-400" /> Agent Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full p-2 bg-secondary/30 border border-border/40 rounded text-foreground text-xs font-mono"
            />
          </div>

          <div className="space-y-1">
            <label className="text-[10px] text-muted-foreground uppercase font-bold">Orchestration Pattern</label>
            <select
              value={pattern}
              onChange={(e) => setPattern(e.target.value)}
              className="w-full p-2 bg-secondary/30 border border-border/40 rounded text-foreground text-xs font-mono"
            >
              <option value="react">ReAct Reasoning Loop</option>
              <option value="plan_exec">Plan-Execute Two-Stage</option>
              <option value="reflection">Reflection & Self-Correction</option>
            </select>
          </div>

          <div className="space-y-1">
            <label className="text-[10px] text-muted-foreground uppercase font-bold flex items-center gap-1">
              <Cpu className="h-3 w-3 text-amber-400" /> Primary LLM Model
            </label>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="w-full p-2 bg-secondary/30 border border-border/40 rounded text-foreground text-xs font-mono"
            >
              <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
              <option value="gpt-4o">OpenAI GPT-4o</option>
              <option value="claude-3-5-sonnet">Claude 3.5 Sonnet</option>
            </select>
          </div>
        </div>

        {/* System Prompt Instruction */}
        <div className="space-y-1">
          <label className="text-[10px] text-muted-foreground uppercase font-bold">Agent System Instruction Prompt</label>
          <textarea
            rows={4}
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            className="w-full p-2.5 bg-secondary/30 border border-border/40 rounded text-foreground text-xs font-mono"
          />
        </div>

        {/* Tool Bindings */}
        <div className="bg-secondary/15 border border-border/40 rounded-xl p-4 space-y-3">
          <div className="flex items-center gap-2 border-b border-border/40 pb-2">
            <Wrench className="h-4 w-4 text-cyan-400" />
            <h4 className="text-xs font-bold text-foreground">Bound Subsystem Tools</h4>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {availableTools.map((t) => {
              const isBound = selectedTools.includes(t.id)
              return (
                <div
                  key={t.id}
                  onClick={() => toggleTool(t.id)}
                  className={`p-3 rounded-lg border cursor-pointer flex items-center justify-between transition-all ${
                    isBound
                      ? "bg-cyan-500/20 border-cyan-500 text-cyan-300 font-bold"
                      : "bg-secondary/20 border-border/30 text-muted-foreground hover:border-cyan-500/40"
                  }`}
                >
                  <span>{t.name}</span>
                  {isBound && <CheckCircle className="h-4 w-4 text-cyan-400" />}
                </div>
              )
            })}
          </div>
        </div>
      </form>
    </div>
  )
}