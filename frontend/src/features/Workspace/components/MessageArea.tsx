import React, { useEffect, useRef, useState, useCallback, useLayoutEffect, useMemo } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Loader2, ArrowDown, AlertCircle, RefreshCw } from "lucide-react"
import { useVirtualizer } from "./useVirtualizer"
import { MessageBubble } from "./MessageBubble"
import { MarkdownRenderer } from "./MarkdownRenderer"
import { EmptyState } from "./EmptyState"
import { cursorVariants } from "@/lib/motion"
import { cleanAssistantText } from "@/utils/cleanText"
import type { Message } from "@/types/api"

interface MessageAreaProps {
  messages: Message[]
  isThinking: boolean
  isStreaming: boolean
  streamingText: string
  hasMoreHistory?: boolean
  isFetchingOlder?: boolean
  isFetchOlderError?: boolean
  onFetchOlder?: () => void
  onRetryFetchOlder?: () => void
  onSelectPrompt: (prompt: string) => void
  onNewChat: () => void
  onRegenerate: () => void
}

const SCROLL_THRESHOLD = 120 // px from bottom — within this range, auto-scroll is active
const VIRTUALIZATION_THRESHOLD = 300 // Threshold count for dynamic virtualization

export const MessageArea: React.FC<MessageAreaProps> = ({
  messages,
  isThinking,
  isStreaming,
  streamingText,
  hasMoreHistory = false,
  isFetchingOlder = false,
  isFetchOlderError = false,
  onFetchOlder,
  onRetryFetchOlder,
  onSelectPrompt,
  onNewChat,
  onRegenerate
}) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const [isNearBottom, setIsNearBottom] = useState(true)
  const [showScrollButton, setShowScrollButton] = useState(false)

  // Scroll restoration refs
  const oldScrollHeightRef = useRef<number>(0)
  const oldScrollTopRef = useRef<number>(0)
  const lastFetchTimeRef = useRef<number>(0)

  // Track the message count before each render to distinguish appends (new send) from prepends (old page load)
  const prevMessageCountRef = useRef<number>(0)
  // Mirror isFetchingOlder into a ref so the auto-scroll effect can read it without being a dependency
  const isFetchingOlderRef = useRef<boolean>(isFetchingOlder)
  isFetchingOlderRef.current = isFetchingOlder

  // Deduplicate messages by ID to guarantee stable rendering and zero duplicates
  const uniqueMessages = useMemo(() => {
    const map = new Map<string, Message>()
    for (const m of messages) {
      if (m && m.id) {
        map.set(m.id, m)
      }
    }
    return Array.from(map.values())
  }, [messages])

  // Threshold-based Virtualization: enable TanStack Virtual only for 301+ messages
  const isVirtualized = uniqueMessages.length > VIRTUALIZATION_THRESHOLD

  const virtualizer = useVirtualizer({
    count: uniqueMessages.length,
    getScrollElement: () => containerRef.current,
    estimateSize: () => 120,
    overscan: 5,
    enabled: isVirtualized,
  })

  // Throttled scroll position checker
  const handleScroll = useCallback(() => {
    const el = containerRef.current
    if (!el) return

    // 1. Bottom check for streaming auto-scroll
    const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight
    const nearBottom = distanceFromBottom <= SCROLL_THRESHOLD
    setIsNearBottom(nearBottom)
    setShowScrollButton(!nearBottom)

    console.log('[SCROLL] scrollTop:', el.scrollTop, 'scrollHeight:', el.scrollHeight, 'clientHeight:', el.clientHeight, 'hasMoreHistory:', hasMoreHistory, 'isFetchingOlder:', isFetchingOlder)

    // 2. Top check for reverse infinite scroll
    if (el.scrollTop <= 200 && hasMoreHistory && !isFetchingOlder && !isFetchOlderError) {
      const now = Date.now()
      if (now - lastFetchTimeRef.current > 200) { // 200ms throttle
        lastFetchTimeRef.current = now
        oldScrollHeightRef.current = el.scrollHeight
        oldScrollTopRef.current = el.scrollTop
        console.log('[SCROLL] TOP REACHED — calling onFetchOlder(). scrollTop:', el.scrollTop)
        onFetchOlder?.()
      }
    }
  }, [hasMoreHistory, isFetchingOlder, isFetchOlderError, onFetchOlder])

  // Scroll restoration after prepending older messages page.
  // Runs synchronously before paint (useLayoutEffect) so it wins over any subsequent useEffect.
  useLayoutEffect(() => {
    const el = containerRef.current
    if (!el) return

    if (oldScrollHeightRef.current > 0) {
      const newScrollHeight = el.scrollHeight
      const heightDiff = newScrollHeight - oldScrollHeightRef.current
      if (heightDiff > 0) {
        el.scrollTop = oldScrollTopRef.current + heightDiff
        console.log('[SCROLL] Scroll restored after prepend. heightDiff:', heightDiff, 'new scrollTop:', el.scrollTop)
      }
      oldScrollHeightRef.current = 0
    }
  }, [uniqueMessages.length])

  const scrollToBottom = useCallback((behavior: ScrollBehavior = "smooth") => {
    const el = containerRef.current
    if (el) {
      el.scrollTo({ top: el.scrollHeight, behavior })
    }
  }, [])

  // Auto-scroll ONLY when a genuinely new user message is appended (not when older pages are prepended).
  //
  // The previous logic fired on ANY uniqueMessages.length increase, including when
  // fetchNextPage() prepended older messages — causing the viewport to jump back to bottom
  // and destroying the useLayoutEffect scroll restoration.
  //
  // Guard conditions:
  //   - The count genuinely grew (not just a re-render)
  //   - The last message is a user message (i.e. the user just sent something)
  //   - No history fetch is in progress (if isFetchingOlder is true, the length change
  //     was caused by prepending old pages, NOT by the user sending a new message)
  useEffect(() => {
    const currentCount = uniqueMessages.length
    const prevCount = prevMessageCountRef.current
    prevMessageCountRef.current = currentCount

    // Skip: no change, or we are currently loading older history (this is a prepend, not an append)
    if (currentCount <= prevCount || isFetchingOlderRef.current) {
      return
    }

    const lastMsg = uniqueMessages[currentCount - 1]
    if (lastMsg?.role === "user") {
      console.log('[SCROLL] New user message appended — scrolling to bottom')
      scrollToBottom("instant")
      setIsNearBottom(true)
      setShowScrollButton(false)
    }
  }, [uniqueMessages, scrollToBottom])

  // Streaming scroll protection: auto-scroll ONLY if user is already at bottom
  useEffect(() => {
    if ((isStreaming || isThinking) && isNearBottom) {
      scrollToBottom("instant")
    }
  }, [streamingText, isThinking, isStreaming, isNearBottom, scrollToBottom])

  // Initial scroll to bottom on mount
  useEffect(() => {
    scrollToBottom("instant")
  }, [scrollToBottom])

  // Stage 5 DOM count monitoring
  useLayoutEffect(() => {
    const domCount = document.querySelectorAll("[data-message-id]").length
    console.log("[STAGE 5 - DOM] Number of rendered message elements:", domCount)
  })

  if (uniqueMessages.length === 0) {
    return <EmptyState onSelectPrompt={onSelectPrompt} onNewChat={onNewChat} />
  }

  console.log("[STAGE 4 - RENDERING] messages.length:", uniqueMessages.length)
  if (uniqueMessages.length > 0) {
    console.log("[STAGE 4 - RENDERING] First rendered id:", uniqueMessages[0].id)
    console.log("[STAGE 4 - RENDERING] Last rendered id:", uniqueMessages[uniqueMessages.length - 1].id)
  }

  return (
    <div className="flex-1 relative overflow-hidden flex flex-col">
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto px-4 py-6 space-y-6 scrollbar-thin select-text"
      >
        {/* Top Loading Indicator for Infinite Scroll */}
        {isFetchingOlder && (
          <div className="flex items-center justify-center gap-2 py-2 font-mono text-xs text-muted-foreground bg-secondary/20 rounded-lg border border-border/40">
            <Loader2 className="h-3.5 w-3.5 animate-spin text-primary" />
            <span>Loading older messages...</span>
          </div>
        )}

        {/* Retry Banner on Pagination Error */}
        {isFetchOlderError && (
          <div className="flex items-center justify-between px-3 py-2 text-xs text-destructive bg-destructive/10 rounded-lg border border-destructive/30">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>Failed to load older messages.</span>
            </div>
            <button
              onClick={() => onRetryFetchOlder?.()}
              className="flex items-center gap-1 font-semibold hover:underline cursor-pointer"
            >
              <RefreshCw className="h-3 w-3" />
              Retry
            </button>
          </div>
        )}

        {/* Messages List: Threshold-Based Virtualization vs Standard Stack */}
        {isVirtualized ? (
          <div
            style={{
              height: `${virtualizer.getTotalSize()}px`,
              width: "100%",
              position: "relative",
            }}
          >
            {virtualizer.getVirtualItems().map((virtualRow) => {
              const msg = uniqueMessages[virtualRow.index]
              return (
                <div
                  key={msg.id}
                  ref={virtualizer.measureElement}
                  data-index={virtualRow.index}
                  style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    width: "100%",
                    transform: `translateY(${virtualRow.start}px)`,
                  }}
                >
                  <MessageBubble message={msg} onRegenerate={onRegenerate} />
                </div>
              )
            })}
          </div>
        ) : (
          uniqueMessages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} onRegenerate={onRegenerate} />
          ))
        )}

        {/* Thinking state bubble */}
        {isThinking && (
          <div className="flex gap-3 max-w-3xl mr-auto select-none" role="status" aria-live="polite">
            <span className="sr-only">Assistant is responding</span>
            <div className="h-8 w-8 rounded-lg border font-mono text-xs flex items-center justify-center shrink-0 shadow-sm bg-primary text-primary-foreground border-primary/20">
              A
            </div>
            <div className="space-y-1.5 font-mono text-xs text-muted-foreground bg-secondary/15 border border-border/50 rounded-xl p-3.5 flex items-center gap-3">
              <Loader2 className="h-4 w-4 text-primary animate-spin" />
              <div className="space-y-0.5">
                <span className="font-bold text-foreground block">Thinking...</span>
                <span className="text-[10px] text-muted-foreground block">Resolving nodes: evaluate_context_vectors</span>
              </div>
            </div>
          </div>
        )}

        {/* Streaming state bubble */}
        {isStreaming && (
          <div className="flex gap-3 max-w-3xl mr-auto" role="status" aria-live="polite">
            <span className="sr-only">Assistant is responding</span>
            <div className="h-8 w-8 rounded-lg border font-mono text-xs flex items-center justify-center shrink-0 shadow-sm bg-primary text-primary-foreground border-primary/20">
              A
            </div>
            <div className="space-y-1 min-w-0 flex-1">
              <div className="relative px-4 py-3 rounded-2xl border border-transparent text-sm leading-relaxed text-foreground bg-transparent">
                <MarkdownRenderer content={cleanAssistantText(streamingText || "...")} />
                <motion.span
                  variants={cursorVariants}
                  animate="blink"
                  className="inline-block w-2 h-4 ml-1 bg-primary rounded-xs align-middle"
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Floating Jump-to-Bottom / New Messages Pill */}
      <AnimatePresence>
        {showScrollButton && (
          <motion.button
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 8 }}
            transition={{ duration: 0.18 }}
            onClick={() => {
              scrollToBottom("smooth")
              setShowScrollButton(false)
              setIsNearBottom(true)
            }}
            aria-label="Scroll to latest message"
            className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-1.5 px-3.5 py-1.5 rounded-full border border-primary/40 bg-background/95 backdrop-blur-md text-xs font-medium text-foreground shadow-lg hover:border-primary transition-colors z-10"
          >
            <ArrowDown className="h-3.5 w-3.5 text-primary" />
            {isStreaming ? "New messages ↓" : "Latest message"}
          </motion.button>
        )}
      </AnimatePresence>
    </div>
  )
}
