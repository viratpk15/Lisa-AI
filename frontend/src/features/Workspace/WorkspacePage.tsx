import React, { useState, useEffect, useMemo, useRef } from "react"
import { useNavigate, useLocation } from "react-router"
import { motion, AnimatePresence } from "framer-motion"
import { Menu, ChevronLeft, ChevronRight, AlertCircle, RefreshCw } from "lucide-react"
import { useQueryClient, type InfiniteData } from "@tanstack/react-query"
import { useAuthStore } from "@/services/store/authStore"

import { Button } from "@/components/ui/button"
import { Sidebar } from "./components/Sidebar"
import { Header } from "./components/Header"
import { MessageArea } from "./components/MessageArea"
import { Composer } from "./components/Composer"
import { SearchModal } from "./components/SearchModal"
import { dashboardGridVariants } from "@/lib/motion"
import { streamChatMessage, type CancellationToken } from "@/services/api/sse"

import { queryKeys } from "@/services/queries/queryKeys"
import { UnauthorizedError } from "@/services/api/errors"
import {
  useConversationsQuery,
  useConversationDetailQuery,
  useInfiniteConversationMessagesQuery,
  useCreateConversationMutation,
  useDeleteConversationMutation,
  useRenameConversationMutation,
  useTogglePinMutation
} from "@/services/queries/chat"
import type { Conversation, Attachment, Message, PaginatedMessagesResponse } from "@/types/api"

export default function WorkspacePage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const clearAuth = useAuthStore((state) => state.clearAuth)
  const [windowWidth, setWindowWidth] = useState(typeof window !== "undefined" ? window.innerWidth : 1200)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [inputText, setInputText] = useState("")
  const [isSearchOpen, setIsSearchOpen] = useState(false)

  // Cmd+K global search shortcut listener
  useEffect(() => {
    const handleCmdK = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault()
        setIsSearchOpen((prev) => !prev)
      }
    }
    window.addEventListener("keydown", handleCmdK)
    return () => window.removeEventListener("keydown", handleCmdK)
  }, [])

  // Real-time SSE streaming state
  const [isThinking, setIsThinking] = useState(false)
  const [isStreaming, setIsStreaming] = useState(false)
  const [streamingText, setStreamingText] = useState("")
  const [streamError, setStreamError] = useState<string | null>(null)
  const [cancelToken, setCancelToken] = useState<CancellationToken | null>(null)
  const [optimisticUserMsg, setOptimisticUserMsg] = useState<Message | null>(null)
  const [sessionActiveAttachmentMap, setSessionActiveAttachmentMap] = useState<Record<string, Attachment>>({})

  // Real backend queries & mutations
  const { data: conversations = [], isError: isConvError, error: convError, refetch } = useConversationsQuery()
  const activeId = selectedId || (conversations.length > 0 ? conversations[0].id : null)
  const { data: conversationDetail } = useConversationDetailQuery(activeId)

  // Infinite scroll query for history messages
  const {
    data: infiniteMessagesData,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isError: isInfiniteError,
    refetch: refetchInfinite,
  } = useInfiniteConversationMessagesQuery(activeId)

  const createConvMutation = useCreateConversationMutation()
  const deleteConvMutation = useDeleteConversationMutation()
  const renameConvMutation = useRenameConversationMutation()
  const togglePinMutation = useTogglePinMutation()

  // Ref tracking previous active session and page count to detect unexpected cache drops
  const prevActiveIdRef = useRef<string | null>(null)
  const prevPageCountRef = useRef<number>(0)

  // Flatten all paginated message pages in chronological (ASC) order
  // NOTE: Infinite query cache is the SOLE source of truth for rendered messages.
  const allPaginatedMessages: Message[] = useMemo(() => {
    if (!infiniteMessagesData?.pages || infiniteMessagesData.pages.length === 0) {
      return []
    }

    const pages = infiniteMessagesData.pages
    const pageParams = infiniteMessagesData.pageParams
    const totalPageCount = pages.length

    // Diagnostics check for cache preservation
    if (prevActiveIdRef.current === activeId) {
      if (totalPageCount < prevPageCountRef.current) {
        console.warn(
          `[CACHE WARNING] Page count decreased from ${prevPageCountRef.current} to ${totalPageCount} for session ${activeId}`
        )
      }
    } else {
      prevActiveIdRef.current = activeId
    }
    prevPageCountRef.current = totalPageCount

    const msgs: Message[] = []
    const reversedPages = [...pages].reverse()
    for (const p of reversedPages as PaginatedMessagesResponse[]) {
      if (p?.messages) {
        msgs.push(...p.messages)
      }
    }

    console.log("[DIAGNOSTICS - INFINITE QUERY CACHE]", {
      sessionId: activeId,
      pagesLength: totalPageCount,
      pageParamsLength: pageParams?.length ?? 0,
      totalFlattenedMessages: msgs.length,
      hasNextPage: Boolean(hasNextPage),
      nextCursor: pages[0]?.next_cursor ?? null,
    })

    return msgs
  }, [infiniteMessagesData, activeId, hasNextPage])

  // Track window size resize events for panels layout responsive boundaries
  useEffect(() => {
    const handleResize = () => {
      setWindowWidth(window.innerWidth)
      if (window.innerWidth < 1024) {
        setSidebarOpen(false)
      } else {
        setSidebarOpen(true)
      }
    }
    window.addEventListener("resize", handleResize)
    handleResize()
    return () => window.removeEventListener("resize", handleResize)
  }, [])

  const location = useLocation()

  // Save selected session to localStorage on change for refresh persistence
  useEffect(() => {
    if (selectedId) {
      localStorage.setItem("jarvis_last_active_session_id", selectedId)
    }
  }, [selectedId])

  // Auto-select initial conversation on load, restoring from URL parameter or localStorage
  useEffect(() => {
    const searchParams = new URLSearchParams(location.search)
    const savedSessionId = localStorage.getItem("jarvis_last_active_session_id")
    const querySessionId = searchParams.get("session_id") || (location.state as { sessionId?: string })?.sessionId || savedSessionId

    if (querySessionId && conversations.some((c) => c.id === querySessionId)) {
      if (selectedId !== querySessionId) {
        setSelectedId(querySessionId)
      }
    } else if (!selectedId && conversations.length > 0) {
      setSelectedId(conversations[0].id)
    }
  }, [conversations, selectedId, location])

  const existingSummary = conversations.find((c) => c.id === activeId)
  const selectedChat: Conversation | null = existingSummary
    ? {
        ...existingSummary,
        messages: allPaginatedMessages
      }
    : (activeId
        ? {
            id: activeId,
            title: conversationDetail?.title || "New Conversation",
            preview: "",
            time: "Just now",
            pinned: false,
            model: "Gemini 2.5 Pro",
            unread: false,
            group: "Today",
            messages: allPaginatedMessages
          }
        : null)

  const handleSelectChat = (id: string) => {
    if (isStreaming && cancelToken) {
      cancelToken.abort()
    }
    setIsThinking(false)
    setIsStreaming(false)
    setStreamingText("")
    setOptimisticUserMsg(null)
    setSelectedId(id)
  }

  const handleNewChat = () => {
    if (isStreaming && cancelToken) {
      cancelToken.abort()
    }
    setIsThinking(false)
    setIsStreaming(false)
    setStreamingText("")
    setOptimisticUserMsg(null)

    createConvMutation.mutate(undefined, {
      onSuccess: (newConv) => {
        setSelectedId(newConv.id)
      }
    })
  }

  const handleTogglePin = (id: string, e?: React.MouseEvent) => {
    if (e) e.stopPropagation()
    togglePinMutation.mutate(id)
  }

  const handleDeleteChat = (id: string, e?: React.MouseEvent) => {
    if (e) e.stopPropagation()
    deleteConvMutation.mutate(id, {
      onSuccess: () => {
        if (selectedId === id) {
          const remaining = conversations.filter((c) => c.id !== id)
          setSelectedId(remaining.length > 0 ? remaining[0].id : null)
        }
      }
    })
  }

  const handleRenameChat = (newTitle: string) => {
    if (!selectedId) return
    renameConvMutation.mutate({ sessionId: selectedId, title: newTitle })
  }

  const handleExport = (format: "markdown" | "json") => {
    if (!selectedChat) return
    let blob: Blob
    let filename: string
    
    if (format === "json") {
      blob = new Blob([JSON.stringify(selectedChat, null, 2)], { type: "application/json" })
      filename = `${selectedChat.title.toLowerCase().replace(/\s+/g, "-")}.json`
    } else {
      const mdContent = selectedChat.messages
        .map((m) => `### ${m.role.toUpperCase()} (${m.timestamp})\n\n${m.content}`)
        .join("\n\n---\n\n")
      blob = new Blob([mdContent], { type: "text/markdown" })
      filename = `${selectedChat.title.toLowerCase().replace(/\s+/g, "-")}.md`
    }

    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  }

  // Submit prompt using real-time SSE streaming
  const handleSend = async (text: string, attachedFiles: Attachment[]) => {
    let fullPrompt = text
    if (attachedFiles && attachedFiles.length > 0) {
      const fileRefs = attachedFiles.map(a => `[Attached File: ${a.name} (${a.type})]`).join("\n")
      fullPrompt = text ? `${text}\n\n${fileRefs}` : fileRefs
    }

    if (!fullPrompt.trim()) return

    let activeSessionId = selectedId || selectedChat?.id
    if (!activeSessionId) {
      try {
        const newConv = await createConvMutation.mutateAsync()
        activeSessionId = newConv.id
        setSelectedId(newConv.id)
      } catch {
        setStreamError("Failed to initialize conversation session.")
        return
      }
    }

    // Clear previous errors & reset stream buffers
    setStreamError(null)
    setIsThinking(true)
    setIsStreaming(false)
    setStreamingText("")

    const userTime = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    const optMsg: Message = {
      id: `user-opt-${Date.now()}`,
      role: "user",
      content: fullPrompt,
      timestamp: userTime
    }
    setOptimisticUserMsg(optMsg)

    const targetSessionId = activeSessionId
    if (attachedFiles && attachedFiles.length > 0) {
      setSessionActiveAttachmentMap((prev) => ({ ...prev, [targetSessionId]: attachedFiles[0] }))
    }

    const activeAtt = attachedFiles && attachedFiles.length > 0 ? attachedFiles[0] : sessionActiveAttachmentMap[targetSessionId]
    const attachmentIds = attachedFiles && attachedFiles.length > 0 ? attachedFiles.map((a) => a.id) : (activeAtt ? [activeAtt.id] : [])
    const activeFilename = activeAtt ? activeAtt.name : undefined

    const tokenHandle = streamChatMessage(
      targetSessionId,
      fullPrompt,
      {
        onThinking: () => {
          setIsThinking(true)
          setIsStreaming(false)
        },
        onToken: (tokenStr: string) => {
          setIsThinking(false)
          setIsStreaming(true)
          setStreamingText((prev) => prev + tokenStr)
        },
        onDone: async (finalResponseText?: string) => {
        const userTime = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
        const assistantTime = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })

        const realUserMsg: Message = {
          id: `user-${Date.now()}`,
          role: "user",
          content: fullPrompt,
          timestamp: userTime,
        }

        const assistantMsg: Message = {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: finalResponseText || streamingText,
          timestamp: assistantTime,
        }

        // Cache diagnostic logging before setQueryData
        const cacheBefore = queryClient.getQueryData<InfiniteData<PaginatedMessagesResponse>>(
          queryKeys.conversations.messages(targetSessionId)
        )
        console.log("[DIAGNOSTICS - PRE-STREAM-DONE CACHE]", {
          sessionId: targetSessionId,
          pageCountBefore: cacheBefore?.pages?.length ?? 0,
          pageParamsCountBefore: cacheBefore?.pageParams?.length ?? 0,
        })

        // Update infinite query cache in-place by appending user + assistant messages to newest page (pages[0])
        queryClient.setQueryData<InfiniteData<PaginatedMessagesResponse>>(
          queryKeys.conversations.messages(targetSessionId),
          (oldData) => {
            if (!oldData || !oldData.pages || oldData.pages.length === 0) {
              return {
                pageParams: [null],
                pages: [
                  {
                    messages: [realUserMsg, assistantMsg],
                    next_cursor: null,
                    has_more: false,
                  },
                ],
              }
            }
            const newPages = [...oldData.pages]
            const newestPage = newPages[0]

            const existingIds = new Set(newestPage.messages.map((m) => m.id))
            const toAdd: Message[] = []
            if (!existingIds.has(realUserMsg.id)) {
              const userContentExists = newestPage.messages.some(
                (m) => m.role === "user" && m.content === realUserMsg.content
              )
              if (!userContentExists) {
                toAdd.push(realUserMsg)
              }
            }
            if (!existingIds.has(assistantMsg.id)) {
              toAdd.push(assistantMsg)
            }

            newPages[0] = {
              ...newestPage,
              messages: [...newestPage.messages, ...toAdd],
            }

            return {
              ...oldData,
              pages: newPages,
            }
          }
        )

        // Cache diagnostic logging after setQueryData
        const cacheAfter = queryClient.getQueryData<InfiniteData<PaginatedMessagesResponse>>(
          queryKeys.conversations.messages(targetSessionId)
        )
        console.log("[DIAGNOSTICS - POST-STREAM-DONE CACHE]", {
          sessionId: targetSessionId,
          pageCountAfter: cacheAfter?.pages?.length ?? 0,
          pageParamsCountAfter: cacheAfter?.pageParams?.length ?? 0,
        })

        // Invalidate ONLY metadata queries, NEVER invalidating messages infinite cache
        await queryClient.invalidateQueries({ queryKey: queryKeys.conversations.detail(targetSessionId) })
        await queryClient.invalidateQueries({ queryKey: queryKeys.conversations.list() })

        setIsThinking(false)
        setIsStreaming(false)
        setStreamingText("")
        setCancelToken(null)
        setOptimisticUserMsg(null)
      },
      onError: (err: Error) => {
        setIsThinking(false)
        setIsStreaming(false)
        setStreamingText("")
        setCancelToken(null)
        setStreamError(err.message || "Failed to stream response from server.")

        if (err instanceof UnauthorizedError) {
          // Use clearAuth to clear both localStorage and Zustand auth state atomically
          clearAuth()
          navigate("/auth", { replace: true })
        }
      }
    },
    attachmentIds,
    undefined,
    activeFilename
  )

    setCancelToken(tokenHandle)
  }

  const handleStopGeneration = () => {
    if (cancelToken) {
      cancelToken.abort()
    }
    setIsThinking(false)
    setIsStreaming(false)
    setStreamingText("")
    setCancelToken(null)
    setOptimisticUserMsg(null)
  }

  const handleSelectPrompt = (prompt: string) => {
    setInputText(prompt)
  }

  const isMobile = windowWidth < 768

  // Active message list combining loaded history + optimistic user message safely
  const activeMessages: Message[] = selectedChat ? [
    ...(selectedChat.messages || []),
    ...(optimisticUserMsg && !(selectedChat.messages || []).some(m => m.role === "user" && m.content === optimisticUserMsg.content) ? [optimisticUserMsg] : [])
  ] : (optimisticUserMsg ? [optimisticUserMsg] : [])

  return (
    <motion.div
      variants={dashboardGridVariants}
      initial="initial"
      animate="animate"
      className="flex h-full w-full bg-background overflow-hidden relative"
    >
      {/* 1. Sidebar - Left Side */}
      <AnimatePresence mode="wait">
        {sidebarOpen && (
          <motion.div
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: isMobile ? "100%" : 280, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className={`h-full shrink-0 z-40 ${isMobile ? "absolute inset-0 bg-background" : "relative"}`}
          >
            <Sidebar
              conversations={conversations}
              selectedId={selectedId || (selectedChat?.id ?? null)}
              onSelect={(id) => {
                handleSelectChat(id)
                if (isMobile) setSidebarOpen(false)
              }}
              onNewChat={handleNewChat}
              onTogglePin={handleTogglePin}
              onDelete={handleDeleteChat}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* 2. Main Workspace Split Panel */}
      <div className="flex-1 flex flex-col h-full overflow-hidden relative bg-background">
        
        {/* Toggle Sidebar handle for Desktop/Tablet */}
        {!isMobile && (
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="absolute left-0 top-50 z-50 h-10 w-4 rounded-r-md border border-l-0 border-border/80 bg-sidebar hover:bg-secondary text-muted-foreground flex items-center justify-center cursor-pointer transition-colors shadow-sm focus:outline-none"
            title={sidebarOpen ? "Hide sidebar" : "Show sidebar"}
          >
            {sidebarOpen ? <ChevronLeft className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
          </button>
        )}

        {/* Global Error Banner if API connection fails */}
        {(streamError || isConvError) && (
          <div className="bg-destructive/15 border-b border-destructive/30 px-4 py-2 text-xs flex items-center justify-between text-destructive shrink-0">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>
                {streamError || convError?.message || "Backend communications error. Check server availability."}
              </span>
            </div>
            <Button
              variant="outline"
              size="xs"
              onClick={() => {
                setStreamError(null)
                refetch()
              }}
              className="gap-1 border-destructive/40 text-destructive hover:bg-destructive/10"
            >
              <RefreshCw className="h-3 w-3" />
              Retry
            </Button>
          </div>
        )}

        {selectedChat ? (
          <>
            {/* Header */}
            <div className="flex items-center bg-background shrink-0">
              {isMobile && (
                <Button
                  onClick={() => setSidebarOpen(true)}
                  variant="ghost"
                  size="icon"
                  className="h-9 w-9 ml-2 text-muted-foreground cursor-pointer"
                >
                  <Menu className="h-4.5 w-4.5" />
                </Button>
              )}
              <div className="flex-1 min-w-0">
                <Header
                  title={selectedChat.title}
                  model={selectedChat.model}
                  scope="Personal Cloud AI"
                  pinned={selectedChat.pinned}
                  onTogglePin={() => handleTogglePin(selectedChat.id)}
                  onRename={handleRenameChat}
                  onDelete={() => handleDeleteChat(selectedChat.id)}
                  onExport={handleExport}
                  onOpenSearch={() => setIsSearchOpen(true)}
                />
              </div>
            </div>

            {/* Conversation Messages List viewport */}
            <MessageArea
              messages={activeMessages}
              isThinking={isThinking}
              isStreaming={isStreaming}
              streamingText={streamingText}
              hasMoreHistory={Boolean(hasNextPage)}
              isFetchingOlder={isFetchingNextPage}
              isFetchOlderError={isInfiniteError}
              onFetchOlder={() => {
                fetchNextPage().then((res) => {
                  console.log("[STAGE 2 - REACT QUERY] pages.length:", res.data?.pages.length)
                  console.log("[STAGE 2 - REACT QUERY] pageParams:", res.data?.pageParams)
                  console.log("[STAGE 2 - REACT QUERY] hasNextPage:", res.hasNextPage)
                  console.log("[STAGE 2 - REACT QUERY] isFetchingNextPage:", res.isFetchingNextPage)
                })
              }}
              onRetryFetchOlder={() => refetchInfinite()}
              onSelectPrompt={handleSelectPrompt}
              onNewChat={handleNewChat}
              onRegenerate={() => {
                if (selectedChat.messages.length > 0) {
                  const lastUserMsg = [...selectedChat.messages].reverse().find((m) => m.role === "user")
                  if (lastUserMsg) {
                    handleSend(lastUserMsg.content, [])
                  }
                }
              }}
            />

            {/* Prompt Composer input panel */}
            <Composer
              onSend={handleSend}
              inputText={inputText}
              setInputText={setInputText}
              disabled={isThinking || isStreaming}
              isStreaming={isStreaming || isThinking}
              onStopGeneration={handleStopGeneration}
              sessionId={selectedChat?.id}
            />
          </>
        ) : (
          <div className="flex-1 flex flex-col h-full bg-background justify-between">
            {isMobile && (
              <div className="p-3 border-b border-border/60 flex items-center shrink-0">
                <Button
                  onClick={() => setSidebarOpen(true)}
                  variant="ghost"
                  size="icon"
                  className="h-9 w-9 text-muted-foreground cursor-pointer"
                >
                  <Menu className="h-4.5 w-4.5" />
                </Button>
                <span className="font-bold text-xs uppercase tracking-wider text-muted-foreground font-mono ml-2">Jarvis OS</span>
              </div>
            )}
            <MessageArea
              messages={[]}
              isThinking={false}
              isStreaming={false}
              streamingText=""
              onSelectPrompt={handleSelectPrompt}
              onNewChat={handleNewChat}
              onRegenerate={() => {}}
            />
            <Composer
              onSend={handleSend}
              inputText={inputText}
              setInputText={setInputText}
              disabled={false}
            />
          </div>
        )}

        {/* Global Search Modal */}
        <SearchModal
          isOpen={isSearchOpen}
          onClose={() => setIsSearchOpen(false)}
          onSelectConversation={handleSelectChat}
        />
      </div>
    </motion.div>
  )
}


