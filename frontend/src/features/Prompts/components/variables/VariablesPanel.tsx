import { Sliders, CheckCircle2, FileText } from "lucide-react"
import { usePromptStudioStore } from "../../store/usePromptStudioStore"

export function VariablesPanel() {
  const userPromptDraft = usePromptStudioStore((s) => s.userPromptDraft)
  const parsedVariables = usePromptStudioStore((s) => s.parsedVariables)
  const updateVariableValue = usePromptStudioStore((s) => s.updateVariableValue)

  const keys = Object.keys(parsedVariables)

  // Interpolated Preview Calculation
  let previewText = userPromptDraft
  keys.forEach((k) => {
    const val = parsedVariables[k] || `[${k}]`
    previewText = previewText.replace(new RegExp(`\\{\\{\\s*${k}\\s*\\}\\}`, "g"), val)
  })

  return (
    <div className="space-y-4 bg-secondary/15 border border-border/40 rounded-xl p-4">
      <div className="flex items-center justify-between border-b border-border/40 pb-3">
        <div className="flex items-center gap-2">
          <Sliders className="h-4 w-4 text-cyan-400" />
          <h3 className="text-xs font-bold text-foreground">Dynamic Template Variables ({keys.length})</h3>
        </div>
        <span className="text-[10px] font-mono text-muted-foreground">{"Auto-Parsed {{var}}"}</span>
      </div>

      {keys.length === 0 ? (
        <div className="p-4 text-center text-xs text-muted-foreground bg-secondary/10 border border-dashed border-border/40 rounded-lg">
          No variables detected. Insert <span className="text-cyan-400 font-mono">{"{{variable}}"}</span> into prompt editor.
        </div>
      ) : (
        <div className="space-y-3">
          {keys.map((key) => (
            <div key={key} className="p-2.5 bg-secondary/20 border border-border/40 rounded-lg space-y-1">
              <div className="flex items-center justify-between text-xs font-mono">
                <label className="font-bold text-cyan-400">{key}</label>
                <span className="text-[10px] text-muted-foreground capitalize">Type: String</span>
              </div>
              <input
                type="text"
                value={parsedVariables[key] || ""}
                onChange={(e) => updateVariableValue(key, e.target.value)}
                placeholder={`Enter value for ${key}...`}
                className="w-full px-3 py-1.5 text-xs bg-secondary/30 border border-border/50 rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
              />
            </div>
          ))}
        </div>
      )}

      {/* Live Interpolated Preview View */}
      <div className="space-y-1.5 pt-2 border-t border-border/40">
        <div className="flex items-center justify-between text-xs font-mono">
          <span className="font-bold text-foreground flex items-center gap-1">
            <FileText className="h-3.5 w-3.5 text-emerald-400" />
            Live Interpolated Preview
          </span>
          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
        </div>
        <div className="p-3 bg-[#0D1117] border border-border/40 rounded-lg text-xs font-mono text-[#C9D1D9] whitespace-pre-wrap leading-relaxed max-h-45 overflow-y-auto scrollbar-thin">
          {previewText || "Prompt preview will appear here..."}
        </div>
      </div>
    </div>
  )
}
