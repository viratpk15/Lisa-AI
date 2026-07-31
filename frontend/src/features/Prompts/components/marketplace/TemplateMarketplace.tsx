import { Sparkles, Copy } from "lucide-react"
import { usePromptStudioStore } from "../../store/usePromptStudioStore"
import { usePromptTemplatesQuery, cloneTemplateApi } from "../../services/promptsApi"

export function TemplateMarketplace() {
  const setSelectedPromptId = usePromptStudioStore((s) => s.setSelectedPromptId)
  const setActiveTab = usePromptStudioStore((s) => s.setActiveTab)
  const setDraftContent = usePromptStudioStore((s) => s.setDraftContent)

  const { data: templates = [], isLoading } = usePromptTemplatesQuery()

  const handleClone = async (templateId: string) => {
    try {
      const res = await cloneTemplateApi(templateId)
      if (res?.prompt) {
        setSelectedPromptId(res.prompt.id)
        if (res.current_version) {
          setDraftContent(res.current_version.system_prompt, res.current_version.user_prompt)
        }
        setActiveTab("editor")
      }
    } catch (err: any) {
      console.error(err)
    }
  }

  return (
    <div className="space-y-4 bg-secondary/15 border border-border/40 rounded-xl p-4">
      <div className="flex items-center justify-between border-b border-border/40 pb-3">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-violet-400" />
          <h3 className="text-xs font-bold text-foreground">Industry Prompt Templates Marketplace</h3>
        </div>
        <span className="text-[10px] font-mono text-muted-foreground">One-Click Clone & Customize</span>
      </div>

      {isLoading ? (
        <div className="p-4 text-center text-xs text-muted-foreground animate-pulse">Loading templates gallery...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {templates.map((tmpl) => (
            <div
              key={tmpl.id}
              className="p-4 bg-[#0D1117] border border-border/40 hover:border-violet-500/40 rounded-xl space-y-3 transition-all flex flex-col justify-between group"
            >
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="px-2 py-0.5 text-[10px] font-mono font-bold bg-violet-500/20 text-violet-300 border border-violet-500/30 rounded">
                    {tmpl.category}
                  </span>
                  <Sparkles className="h-3.5 w-3.5 text-violet-400 group-hover:rotate-12 transition-transform" />
                </div>
                <h4 className="text-xs font-bold text-foreground group-hover:text-violet-300 transition-colors">
                  {tmpl.name}
                </h4>
                <p className="text-[11px] text-muted-foreground leading-relaxed">
                  {tmpl.description}
                </p>
              </div>

              <div className="pt-2 border-t border-border/30 flex items-center justify-between">
                <span className="text-[10px] font-mono text-muted-foreground">Includes system & user templates</span>
                <button
                  onClick={() => handleClone(tmpl.id)}
                  className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-bold bg-violet-500 hover:bg-violet-400 text-black rounded-lg cursor-pointer transition-all shadow-sm"
                >
                  <Copy className="h-3 w-3" />
                  Clone Template
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
