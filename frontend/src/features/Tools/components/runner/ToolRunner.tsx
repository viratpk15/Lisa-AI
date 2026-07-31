import { Play, FileText } from "lucide-react"
import { useToolConsoleStore } from "../../store/useToolConsoleStore"
import { useToolDetailsQuery, executeTool, streamTool } from "../../services/toolApi"
import { DynamicForm } from "./DynamicForm"
import { ResultPanel } from "../results/ResultPanel"
import { LoadingSkeleton } from "../common/LoadingSkeleton"
import { ErrorState } from "../common/ErrorState"

export function ToolRunner() {
  const selectedToolName = useToolConsoleStore((s) => s.selectedToolName)
  const formParameters = useToolConsoleStore((s) => s.formParameters)
  const setFormParameters = useToolConsoleStore((s) => s.setFormParameters)
  const latestResult = useToolConsoleStore((s) => s.latestResult)
  const setLatestResult = useToolConsoleStore((s) => s.setLatestResult)
  const addExecutionHistory = useToolConsoleStore((s) => s.addExecutionHistory)
  const addPendingApproval = useToolConsoleStore((s) => s.addPendingApproval)
  const addConsoleLog = useToolConsoleStore((s) => s.addConsoleLog)
  const isExecuting = useToolConsoleStore((s) => s.isExecuting)
  const setIsExecuting = useToolConsoleStore((s) => s.setIsExecuting)
  const isStreaming = useToolConsoleStore((s) => s.isStreaming)
  const setIsStreaming = useToolConsoleStore((s) => s.setIsStreaming)
  const setActiveTab = useToolConsoleStore((s) => s.setActiveTab)

  const { data: details, isLoading, isError, refetch } = useToolDetailsQuery(selectedToolName)

  if (!selectedToolName) {
    return (
      <div className="p-8 text-center text-xs text-muted-foreground italic bg-secondary/10 rounded-xl border border-dashed border-border/40">
        Select a tool from the explorer on the left to configure parameters and run executions.
      </div>
    )
  }

  if (isLoading) return <LoadingSkeleton count={3} />
  if (isError || !details) return <ErrorState message={`Failed to load parameter schema for '${selectedToolName}'.`} onRetry={refetch} />

  const { metadata, schema } = details

  const handleExecute = async (args: Record<string, any>) => {
    setIsExecuting(true)
    addConsoleLog("info", `Initiating execution for tool '${metadata.name}'...`)

    try {
      const result = await executeTool(metadata.name, args)
      setLatestResult(result)

      if (result.status === "SUCCESS") {
        addConsoleLog("success", `Execution finished successfully in ${result.duration_ms.toFixed(1)}ms.`)
        addExecutionHistory(result)
      } else if (result.status === "PENDING_APPROVAL") {
        addConsoleLog("warning", `Execution requires Human-in-the-Loop approval. Added to Approval Queue.`)
        addPendingApproval({
          execution_id: result.execution_id,
          tool_name: metadata.name,
          arguments: args,
          requires_approval: true,
          requested_at: new Date().toLocaleTimeString(),
        })
      } else {
        addConsoleLog("stderr", `Tool execution failed (${result.status}): ${result.error || "Unknown error"}`)
        addExecutionHistory(result)
      }
    } catch (err: any) {
      addConsoleLog("stderr", `Execution HTTP error: ${err.message}`)
    } finally {
      setIsExecuting(false)
    }
  }

  const handleStream = async (args: Record<string, any>) => {
    setIsStreaming(true)
    setActiveTab("console")
    addConsoleLog("info", `Opening SSE stream for tool '${metadata.name}'...`)

    await streamTool(
      metadata.name,
      args,
      (chunk) => addConsoleLog("stdout", chunk),
      (err) => addConsoleLog("stderr", `Stream Error: ${err}`),
      () => {
        addConsoleLog("success", "SSE Stream closed ([DONE]).")
        setIsStreaming(false)
      }
    )
  }

  return (
    <div className="space-y-6">
      {/* Parameter Input Form Card */}
      <div className="bg-secondary/15 border border-border/40 rounded-xl p-4 space-y-4">
        <div className="flex items-center justify-between border-b border-border/40 pb-3">
          <div className="flex items-center gap-2">
            <Play className="h-4 w-4 text-cyan-400" />
            <h3 className="text-xs font-bold text-foreground">Interactive Parameter Runner: {metadata.display_name || metadata.name}</h3>
          </div>
          <span className="text-[10px] font-mono text-muted-foreground">Category: {metadata.category}</span>
        </div>

        <DynamicForm
          metadata={metadata}
          schema={schema}
          formValues={formParameters}
          onValuesChange={setFormParameters}
          onExecute={handleExecute}
          onStream={handleStream}
          isExecuting={isExecuting}
          isStreaming={isStreaming}
        />
      </div>

      {/* Execution Results View Panel */}
      <div className="space-y-2">
        <div className="flex items-center gap-2 text-xs font-bold text-foreground">
          <FileText className="h-4 w-4 text-cyan-400" />
          <span>Execution Outcome Panel</span>
        </div>
        <ResultPanel result={latestResult} />
      </div>
    </div>
  )
}
