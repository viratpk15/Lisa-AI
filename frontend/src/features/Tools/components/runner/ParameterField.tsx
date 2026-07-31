interface ParameterFieldProps {
  name: string
  propSchema: Record<string, any>
  isRequired: boolean
  value: any
  onChange: (val: any) => void
  error?: string
}

export function ParameterField({
  name,
  propSchema,
  isRequired,
  value,
  onChange,
  error,
}: ParameterFieldProps) {
  const type = propSchema.type || "string"
  const description = propSchema.description || ""
  const enumValues: string[] | undefined = propSchema.enum

  const renderInput = () => {
    if (enumValues && enumValues.length > 0) {
      return (
        <select
          value={value ?? enumValues[0] ?? ""}
          onChange={(e) => onChange(e.target.value)}
          className="w-full px-3 py-1.5 text-xs bg-secondary/30 border border-border/50 rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 transition-all capitalize"
        >
          {enumValues.map((option) => (
            <option key={option} value={option} className="bg-[#121826] text-foreground">
              {option}
            </option>
          ))}
        </select>
      )
    }

    if (type === "boolean") {
      return (
        <label className="relative inline-flex items-center cursor-pointer select-none">
          <input
            type="checkbox"
            checked={Boolean(value)}
            onChange={(e) => onChange(e.target.checked)}
            className="sr-only peer"
          />
          <div className="w-9 h-5 bg-secondary/60 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-cyan-500/50 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-cyan-500" />
          <span className="ml-2 text-xs font-mono text-muted-foreground">
            {value ? "Enabled (true)" : "Disabled (false)"}
          </span>
        </label>
      )
    }

    if (type === "number" || type === "integer") {
      return (
        <input
          type="number"
          value={value ?? ""}
          onChange={(e) => onChange(e.target.value === "" ? "" : Number(e.target.value))}
          className="w-full px-3 py-1.5 text-xs font-mono bg-secondary/30 border border-border/50 rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 transition-all"
        />
      )
    }

    if (type === "object" || type === "array") {
      return (
        <textarea
          rows={3}
          value={typeof value === "object" ? JSON.stringify(value, null, 2) : value ?? ""}
          onChange={(e) => {
            const raw = e.target.value
            try {
              const parsed = JSON.parse(raw)
              onChange(parsed)
            } catch {
              onChange(raw)
            }
          }}
          placeholder={type === "array" ? '["item1", "item2"]' : '{"key": "value"}'}
          className="w-full px-3 py-2 text-xs font-mono bg-[#0D1117] border border-border/50 rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 transition-all"
        />
      )
    }

    // Default string input / textarea if long description or content field
    if (name.toLowerCase().includes("content") || name.toLowerCase().includes("code") || name.toLowerCase().includes("query")) {
      return (
        <textarea
          rows={4}
          value={value ?? ""}
          onChange={(e) => onChange(e.target.value)}
          placeholder={`Enter ${name}...`}
          className="w-full px-3 py-2 text-xs font-mono bg-[#0D1117] border border-border/50 rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 transition-all"
        />
      )
    }

    return (
      <input
        type="text"
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value)}
        placeholder={`Enter ${name}...`}
        className="w-full px-3 py-1.5 text-xs bg-secondary/30 border border-border/50 rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 transition-all"
      />
    )
  }

  return (
    <div className="space-y-1.5 p-3 bg-secondary/20 border border-border/40 rounded-lg">
      <div className="flex items-center justify-between">
        <label className="text-xs font-bold text-foreground font-mono flex items-center gap-1.5">
          <span>{name}</span>
          {isRequired ? (
            <span className="px-1.5 py-0.2 text-[9px] font-semibold bg-rose-500/20 text-rose-400 border border-rose-500/30 rounded">
              Required
            </span>
          ) : (
            <span className="px-1.5 py-0.2 text-[9px] font-normal text-muted-foreground bg-secondary/40 rounded">
              Optional
            </span>
          )}
        </label>
        <span className="text-[10px] font-mono text-muted-foreground capitalize">Type: {type}</span>
      </div>

      {description && <p className="text-[11px] text-muted-foreground leading-relaxed">{description}</p>}

      {renderInput()}

      {error && <span className="text-[10px] text-rose-400 font-semibold">{error}</span>}
    </div>
  )
}
