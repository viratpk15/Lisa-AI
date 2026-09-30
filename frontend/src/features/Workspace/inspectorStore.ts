import { create } from "zustand"

export interface InspectorEmailData {
  id: number
  subject: string
  sender: string
  received_at: string
  category: string | null
  priority_score: number | null
  is_urgent: boolean
  action_required: boolean
  action_items?: string[]
  deadline?: string | null
  summary_text?: string | null
  verification?: {
    is_verified: boolean
    spf_status?: string | null
    dkim_status?: string | null
    dmarc_status?: string | null
  } | null
}

export interface InspectorAIData {
  sessionTitle?: string
  model?: string
  status?: "idle" | "thinking" | "streaming"
  activeAttachment?: string
  messageCount?: number
}

interface InspectorState {
  aiContext: InspectorAIData | null
  emailContext: InspectorEmailData | null
  setAIContext: (data: InspectorAIData | null) => void
  setEmailContext: (data: InspectorEmailData | null) => void
}

export const useInspectorStore = create<InspectorState>((set) => ({
  aiContext: null,
  emailContext: null,
  setAIContext: (data) => set({ aiContext: data }),
  setEmailContext: (data) => set({ emailContext: data }),
}))
