import { useState, useEffect, useMemo } from "react"
import { Play, Zap, RotateCcw, Copy, Check } from "lucide-react"
import type { ToolMetadata } from "../../types/tools.types"
import { ParameterField } from "./ParameterField"

interface DynamicFormProps {
  metadata: ToolMetadata
  schema: Record<string, any>
  formValues: Record<string, any>
  onValuesChange: (values: Record<string, any>) => void
  onExecute: (args: Record<string, any>) => void
  onStream: (args: Record<string, any>) => void
  isExecuting: boolean
  isStreaming: boolean
}

export function DynamicForm({
  metadata,
  schema,
  formValues,
  onValuesChange,
  onExecute,
  onStream,
  isExecuting,
  isStreaming,
}: DynamicFormProps) {
  const [copied, setCopied] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const properties: Record<string, any> = useMemo(() => schema?.properties || metadata.parameter_schema?.properties || {}, [schema, metadata.parameter_schema])
  const requiredFields: string[] = schema?.required || metadata.parameter_schema?.required || []

  // Set default values when tool changes
  useEffect(() => {
    const defaults: Record<string, any> = {}
    Object.entries(properties).forEach(([key, prop]) => {
      if (prop.default !== undefined) {
        defaults[key] = prop.default
      } else if (prop.enum && prop.enum.length > 0) {
        defaults[key] = prop.enum[0]
      }
    })
    if (Object.keys(defaults).length > 0 && Object.keys(formValues).length === 0) {
      onValuesChange(defaults)
    }
  }, [metadata.name, properties, formValues, onValuesChange])

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {}
    requiredFields.forEach((req) => {
      const val = formValues[req]
      if (val === undefined || val === null || (typeof val === "string" && !val.trim())) {
        newErrors[req] = `Field '${req}' is required.`
      }
    })
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleExecute = () => {
    if (validate()) {
      onExecute(formValues)
    }
  }

  const handleStream = () => {
    if (validate()) {
      onStream(formValues)
    }
  }

  const handleReset = () => {
    onValuesChange({})
    setErrors({})
  }

  const handleCopyJson = () => {
    navigator.clipboard.writeText(JSON.stringify(formValues, null, 2))
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="space-y-4">
      {/* Parameter Input Fields */}
      <div className="space-y-3">
        {Object.keys(properties).length === 0 ? (
          <div className="p-4 text-center text-xs text-muted-foreground bg-secondary/20 rounded-lg border border-border/40">
            This tool requires no input parameters.
          </div>
        ) : (
          Object.entries(properties).map(([fieldName, propSchema]) => (
            <ParameterField
              key={fieldName}
              name={fieldName}
              propSchema={propSchema}
              isRequired={requiredFields.includes(fieldName)}
              value={formValues[fieldName]}
              onChange={(val) => {
                onValuesChange({ ...formValues, [fieldName]: val })
                if (errors[fieldName]) {
                  const updated = { ...errors }
                  delete updated[fieldName]
                  setErrors(updated)
                }
              }}
              error={errors[fieldName]}
            />
          ))
        )}
      </div>

      {/* Action Buttons Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-2 pt-3 border-t border-border/40">
        <div className="flex items-center gap-2">
          <button
            onClick={handleExecute}
            disabled={isExecuting || isStreaming}
            className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-bold bg-cyan-500 hover:bg-cyan-400 text-black rounded-lg cursor-pointer transition-all shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Play className="h-3.5 w-3.5 fill-current" />
            {isExecuting ? "Executing..." : "Execute Tool"}
          </button>

          {metadata.supports_streaming && (
            <button
              onClick={handleStream}
              disabled={isExecuting || isStreaming}
              className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-bold bg-violet-500/20 hover:bg-violet-500/30 text-violet-300 border border-violet-500/40 rounded-lg cursor-pointer transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Zap className="h-3.5 w-3.5" />
              {isStreaming ? "Streaming..." : "Stream SSE"}
            </button>
          )}
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleReset}
            className="inline-flex items-center gap-1 px-2.5 py-1.5 text-xs text-muted-foreground hover:text-foreground bg-secondary/30 hover:bg-secondary/60 border border-border/40 rounded-lg cursor-pointer transition-all"
          >
            <RotateCcw className="h-3 w-3" />
            Reset
          </button>

          <button
            onClick={handleCopyJson}
            className="inline-flex items-center gap-1 px-2.5 py-1.5 text-xs text-muted-foreground hover:text-foreground bg-secondary/30 hover:bg-secondary/60 border border-border/40 rounded-lg cursor-pointer transition-all"
          >
            {copied ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
            {copied ? "Copied" : "Copy Payload"}
          </button>
        </div>
      </div>
    </div>
  )
}
