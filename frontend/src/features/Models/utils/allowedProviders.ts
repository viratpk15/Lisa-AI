// frontend/src/features/Models/utils/allowedProviders.ts

/**
 * Locked provider display filter:
 * Explicitly show: Groq, NVIDIA NIM, Mistral
 * Explicitly hide: Gemini, Anthropic, Ollama, OpenRouter, Cerebras, Together, Fireworks
 */
export function isAllowedProvider(p: { provider_name?: string; display_name?: string }) {
  const name = (p.provider_name || "").toLowerCase()
  const display = (p.display_name || "").toLowerCase()

  if (
    name.includes("gemini") || display.includes("gemini") ||
    name.includes("anthropic") || display.includes("anthropic") ||
    name.includes("ollama") || display.includes("ollama") ||
    name.includes("openrouter") || display.includes("openrouter") ||
    name.includes("cerebras") || display.includes("cerebras") ||
    name.includes("together") || display.includes("together") ||
    name.includes("fireworks") || display.includes("fireworks")
  ) {
    return false
  }

  return (
    name.includes("groq") || display.includes("groq") ||
    name.includes("nvidia") || display.includes("nvidia") || name.includes("nim") || display.includes("nim") ||
    name.includes("mistral") || display.includes("mistral")
  )
}
