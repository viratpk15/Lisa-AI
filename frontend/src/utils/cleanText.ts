/**
 * Safe assistant text helper. Ensures plain text is returned directly,
 * with optional backward-compatibility fallback for legacy JSON envelopes.
 */
export function cleanAssistantText(raw: string): string {
  if (!raw) return ""
  const trimmed = raw.trim()

  // Backward-compatibility check for legacy JSON envelopes
  if (trimmed.startsWith("{") && trimmed.endsWith("}")) {
    try {
      const parsed = JSON.parse(trimmed)
      if (parsed && typeof parsed === "object" && typeof parsed.response === "string") {
        return parsed.response
      }
    } catch {
      // Return raw string if not valid JSON
    }
  }

  return raw
}
