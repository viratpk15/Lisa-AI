import React from "react"
import { CodeBlock } from "./CodeBlock"

interface MarkdownRendererProps {
  content: string
  isStreaming?: boolean
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content, isStreaming = false }) => {
  // Parse inline text rules (bold, italic, inline code, links)
  const parseInline = (text: string): React.ReactNode[] => {
    const tokens: React.ReactNode[] = []
    let keyIndex = 0

    // Match patterns: **bold**, *italic*, `code`, [link](url)
    const regex = /(\*\*.*?\*\*|\*.*?\*|`.*?`|\[.*?\]\(.*?\))/g
    const parts = text.split(regex)

    parts.forEach((part) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        tokens.push(<strong key={keyIndex++} className="font-bold text-foreground">{part.slice(2, -2)}</strong>)
      } else if (part.startsWith("*") && part.endsWith("*")) {
        tokens.push(<em key={keyIndex++} className="italic text-muted-foreground">{part.slice(1, -1)}</em>)
      } else if (part.startsWith("`") && part.endsWith("`")) {
        tokens.push(
          <code key={keyIndex++} className="font-mono text-[11px] font-semibold bg-secondary/65 border border-border/60 px-1 py-0.5 rounded text-primary">
            {part.slice(1, -1)}
          </code>
        )
      } else if (part.startsWith("[") && part.includes("](")) {
        const titleMatch = part.match(/\[(.*?)\]/)
        const urlMatch = part.match(/\((.*?)\)/)
        if (titleMatch && urlMatch) {
          tokens.push(
            <a
              key={keyIndex++}
              href={urlMatch[1]}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline font-semibold"
            >
              {titleMatch[1]}
            </a>
          )
        } else {
          tokens.push(part)
        }
      } else {
        tokens.push(part)
      }
    })

    return tokens
  }

  // Parse lines into block elements (paragraphs, headers, lists, code, tables)
  const parseBlocks = (markdown: string): React.ReactNode[] => {
    const blocks: React.ReactNode[] = []
    const lines = markdown.split("\n")
    let keyIdx = 0

    let inList = false
    let listItems: string[] = []

    let inCode = false
    let codeLanguage = ""
    let codeLines: string[] = []

    let inTable = false
    let tableHeaders: string[] = []
    let tableRows: string[][] = []

    const flushList = () => {
      if (listItems.length > 0) {
        blocks.push(
          <ul key={`ul-${keyIdx++}`} className="list-disc pl-6 space-y-1.5 my-3 text-sm text-muted-foreground leading-relaxed">
            {listItems.map((item, idx) => (
              <li key={idx} className="marker:text-primary/70">{parseInline(item)}</li>
            ))}
          </ul>
        )
        listItems = []
      }
      inList = false
    }

    const flushTable = () => {
      if (tableHeaders.length > 0 || tableRows.length > 0) {
        blocks.push(
          <div key={`table-${keyIdx++}`} className="overflow-x-auto my-4 border border-border/80 rounded-lg">
            <table className="min-w-full divide-y divide-border/60 font-sans text-xs text-left">
              <thead className="bg-secondary/40 text-[10px] font-mono font-semibold uppercase tracking-wider text-muted-foreground">
                <tr>
                  {tableHeaders.map((header, idx) => (
                    <th key={idx} className="px-4 py-3 border-r border-border/40 last:border-r-0">
                      {header.trim()}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border/40 bg-transparent text-muted-foreground">
                {tableRows.map((row, rIdx) => (
                  <tr key={rIdx} className="hover:bg-secondary/15 transition-colors">
                    {row.map((cell, cIdx) => (
                      <td key={cIdx} className="px-4 py-2.5 border-r border-border/40 last:border-r-0 font-medium">
                        {parseInline(cell.trim())}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
        tableHeaders = []
        tableRows = []
      }
      inTable = false
    }

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i]

      // Code blocks boundary
      if (line.trim().startsWith("```")) {
        if (inCode) {
          // End of code block
          blocks.push(
            <div key={`code-${keyIdx++}`} className="my-4">
              <CodeBlock language={codeLanguage} code={codeLines.join("\n")} />
            </div>
          )
          codeLines = []
          inCode = false
        } else {
          // Start of code block
          codeLanguage = line.trim().slice(3) || "plaintext"
          inCode = true
        }
        continue
      }

      if (inCode) {
        codeLines.push(line)
        continue
      }

      // Markdown Table parsing
      if (line.trim().startsWith("|") && line.trim().endsWith("|")) {
        flushList()
        inTable = true
        
        // Skip separator line: |---|---|
        if (line.includes("-") && !line.match(/[a-zA-Z0-9]/)) {
          continue
        }

        const cells = line.slice(1, -1).split("|")
        if (tableHeaders.length === 0) {
          tableHeaders = cells
        } else {
          tableRows.push(cells)
        }
        continue
      } else if (inTable) {
        flushTable()
      }

      // Headers
      if (line.startsWith("# ")) {
        flushList()
        blocks.push(
          <h1 key={`h1-${keyIdx++}`} className="text-xl font-bold tracking-tight text-foreground mt-5 mb-2 leading-none border-b border-border/30 pb-2">
            {parseInline(line.slice(2))}
          </h1>
        )
      } else if (line.startsWith("## ")) {
        flushList()
        blocks.push(
          <h2 key={`h2-${keyIdx++}`} className="text-base font-extrabold tracking-tight text-foreground mt-4 mb-2 leading-none">
            {parseInline(line.slice(3))}
          </h2>
        )
      } else if (line.startsWith("### ")) {
        flushList()
        blocks.push(
          <h3 key={`h3-${keyIdx++}`} className="text-sm font-bold text-foreground mt-3.5 mb-1.5 leading-none">
            {parseInline(line.slice(4))}
          </h3>
        )
      }
      // List items
      else if (line.trim().startsWith("- ") || line.trim().startsWith("* ")) {
        inList = true
        listItems.push(line.trim().slice(2))
      } else {
        if (inList) {
          flushList()
        }

        // Empty spacer line
        if (line.trim() === "") {
          blocks.push(<div key={`spacer-${keyIdx++}`} className="h-2" />)
        } else {
          // Standard Paragraph block
          blocks.push(
            <p key={`p-${keyIdx++}`} className="text-sm text-muted-foreground leading-relaxed my-2">
              {parseInline(line)}
            </p>
          )
        }
      }
    }

    if (inList) flushList()
    if (inTable) flushTable()

    return blocks
  }

  return (
    <div className="space-y-1 relative">
      {parseBlocks(content)}
      {isStreaming && (
        <span className="inline-block w-2 h-4 ml-1 bg-primary animate-pulse align-middle rounded-sm" aria-hidden="true" />
      )}
    </div>
  )
}
