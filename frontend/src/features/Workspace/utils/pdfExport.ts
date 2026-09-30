/**
 * Lisa AIOS — Discussion PDF Export Utility
 * Generates an executive, print-ready Question & Answer transcript PDF.
 */

import type { Message } from "@/types/api"

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;")
}

function formatContent(content: string): string {
  const safe = escapeHtml(content)
  // Format code blocks
  const withCodeBlocks = safe.replace(/```([\s\S]*?)```/g, (_match, code) => {
    return `<pre style="background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 6px; padding: 10px; font-family: monospace; font-size: 11px; white-space: pre-wrap; word-break: break-all; margin: 8px 0;"><code>${code}</code></pre>`
  })
  // Format linebreaks
  return withCodeBlocks.replace(/\n/g, "<br/>")
}

export function exportDiscussionPdf(
  title: string,
  model: string,
  messages: Message[]
): void {
  const printWindow = window.open("", "_blank")
  if (!printWindow) {
    alert("Please allow popups to generate the Discussion PDF.")
    return
  }

  const dateStr = new Date().toLocaleDateString(undefined, {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })

  const messagesHtml = messages
    .map((msg, idx) => {
      const isUser = msg.role.toLowerCase() === "user"
      return `
        <div style="margin-bottom: 18px; page-break-inside: avoid; border: 1px solid ${isUser ? "#cbd5e1" : "#e2e8f0"}; border-radius: 10px; padding: 14px 16px; background-color: ${isUser ? "#f8fafc" : "#ffffff"};">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; border-bottom: 1px solid ${isUser ? "#e2e8f0" : "#f1f5f9"}; padding-bottom: 6px;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <span style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; padding: 2px 8px; border-radius: 4px; ${isUser ? "background: #0f172a; color: #ffffff;" : "background: #4f46e5; color: #ffffff;"}">
                ${isUser ? "👤 Question " + (Math.floor(idx / 2) + 1) : "🤖 Lisa AIOS Answer"}
              </span>
              <span style="font-size: 11px; color: #64748b; font-weight: 500;">
                ${isUser ? "User" : "Lisa AIOS"}
              </span>
            </div>
            <span style="font-size: 11px; color: #94a3b8; font-family: monospace;">
              ${msg.timestamp || ""}
            </span>
          </div>
          <div style="font-size: 13px; line-height: 1.6; color: #1e293b;">
            ${formatContent(msg.content)}
          </div>
        </div>
      `
    })
    .join("")

  const html = `
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>${escapeHtml(title)} — Lisa AIOS Discussion</title>
        <style>
          @media print {
            body { margin: 0; padding: 20mm; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
            .no-print { display: none !important; }
          }
          body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #ffffff;
            color: #0f172a;
            max-width: 800px;
            margin: 0 auto;
            padding: 30px 20px;
          }
          .header-box {
            border-bottom: 2px solid #0f172a;
            padding-bottom: 16px;
            margin-bottom: 24px;
          }
          .title {
            font-size: 24px;
            font-weight: 800;
            margin: 0 0 6px 0;
            color: #0f172a;
          }
          .meta {
            font-size: 12px;
            color: #64748b;
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
          }
          .btn-print {
            background: #0f172a;
            color: #ffffff;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            margin-bottom: 20px;
          }
        </style>
      </head>
      <body>
        <div class="no-print" style="margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; background: #f8fafc; border: 1px solid #e2e8f0; padding: 12px 16px; border-radius: 8px;">
          <span style="font-size: 13px; color: #475569;">Discussion transcript ready to save as PDF</span>
          <button class="btn-print" onclick="window.print()">Save as PDF / Print</button>
        </div>

        <div class="header-box">
          <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #4f46e5; font-weight: 700; margin-bottom: 4px;">
            Lisa AIOS · Discussion Transcript
          </div>
          <h1 class="title">${escapeHtml(title)}</h1>
          <div class="meta">
            <span><strong>Generated:</strong> ${dateStr}</span>
            <span><strong>Model:</strong> ${escapeHtml(model)}</span>
            <span><strong>Exchanges:</strong> ${messages.length} messages</span>
          </div>
        </div>

        <div>
          ${messagesHtml}
        </div>

        <div style="margin-top: 30px; padding-top: 16px; border-top: 1px solid #e2e8f0; text-align: center; font-size: 11px; color: #94a3b8;">
          Confidential · Exported from Lisa AIOS Personal Operating System
        </div>

        <script>
          window.onload = function() {
            setTimeout(function() {
              window.print();
            }, 300);
          };
        </script>
      </body>
    </html>
  `

  printWindow.document.open()
  printWindow.document.write(html)
  printWindow.document.close()
}
