import React, { useState } from "react"
import { motion } from "framer-motion"
import { Copy, Check, ThumbsUp, ThumbsDown, RefreshCw, Sparkles, User, Settings } from "lucide-react"
import { MarkdownRenderer } from "./MarkdownRenderer"
import { messageVariants } from "@/lib/motion"
import { cleanAssistantText } from "@/utils/cleanText"

interface Message {
  id: string
  role: "user" | "assistant" | "system"
  content: string
  timestamp: string
}

interface MessageBubbleProps {
  message: Message
  onRegenerate?: () => void
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message, onRegenerate }) => {
  const [copied, setCopied] = useState(false)
  const [like, setLike] = useState<boolean | null>(null)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(cleanAssistantText(message.content))
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error("Failed to copy message content:", err)
    }
  }

  if (message.role === "system") {
    return (
      <motion.div
        variants={messageVariants}
        initial="initial"
        animate="animate"
        className="flex items-center justify-center p-3 select-none"
      >
        <div className="flex items-center gap-2 px-3 py-1 bg-secondary/15 border border-border/40 rounded-full text-[10px] font-mono text-muted-foreground leading-none">
          <Settings className="h-3 w-3 text-primary/70 shrink-0" />
          <span>{message.content}</span>
          <span className="text-muted-foreground/50">({message.timestamp})</span>
        </div>
      </motion.div>
    )
  }

  const isUser = message.role === "user"
  const displayContent = isUser ? message.content : cleanAssistantText(message.content)

  return (
    <motion.div
      data-message-id={message.id}
      variants={messageVariants}
      initial="initial"
      animate="animate"
      className={`flex gap-3 max-w-3xl ${isUser ? "ml-auto flex-row-reverse" : "mr-auto"}`}
    >
      {/* Avatar block */}
      <div className={`h-8 w-8 rounded-lg border font-mono text-xs flex items-center justify-center shrink-0 shadow-sm ${isUser ? "bg-secondary/60 border-border/80 text-foreground" : "bg-primary text-primary-foreground border-primary/20"}`}>
        {isUser ? <User className="h-4.5 w-4.5 text-muted-foreground" /> : <Sparkles className="h-4 w-4" />}
      </div>

      {/* Message content panel */}
      <div className="space-y-1 min-w-0">
        <div className={`relative px-4 py-3 rounded-2xl border text-sm leading-relaxed ${isUser ? "bg-secondary/25 border-border/80 text-foreground" : "bg-transparent border-transparent text-foreground"}`}>
          <MarkdownRenderer content={displayContent} />
        </div>

        {/* Action icons bar for assistant messages */}
        {!isUser && (
          <div className="flex items-center gap-2 pl-4 text-[10px] font-mono text-muted-foreground/60 select-none">
            <span>{message.timestamp}</span>
            <span>•</span>
            <div className="flex items-center gap-0.5">
              {/* Copy */}
              <button
                onClick={handleCopy}
                className="p-1 rounded hover:bg-secondary text-muted-foreground/50 hover:text-foreground cursor-pointer focus:outline-none transition-colors"
                title="Copy response text"
              >
                {copied ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
              </button>

              {/* Regenerate */}
              {onRegenerate && (
                <button
                  onClick={onRegenerate}
                  className="p-1 rounded hover:bg-secondary text-muted-foreground/50 hover:text-foreground cursor-pointer focus:outline-none transition-colors"
                  title="Regenerate reply"
                >
                  <RefreshCw className="h-3 w-3" />
                </button>
              )}

              {/* Like */}
              <button
                onClick={() => setLike(like === true ? null : true)}
                className={`p-1 rounded hover:bg-secondary cursor-pointer focus:outline-none transition-colors ${like === true ? "text-emerald-400" : "text-muted-foreground/50 hover:text-foreground"}`}
                title="Positive feedback"
              >
                <ThumbsUp className="h-3 w-3" />
              </button>

              {/* Dislike */}
              <button
                onClick={() => setLike(like === false ? null : false)}
                className={`p-1 rounded hover:bg-secondary cursor-pointer focus:outline-none transition-colors ${like === false ? "text-red-400" : "text-muted-foreground/50 hover:text-foreground"}`}
                title="Negative feedback"
              >
                <ThumbsDown className="h-3 w-3" />
              </button>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  )
}
