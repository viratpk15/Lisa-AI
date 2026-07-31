import { useQuery, useMutation, useInfiniteQuery, useQueryClient, type InfiniteData } from "@tanstack/react-query"
import { queryKeys } from "./queryKeys"
import {
  listConversations,
  getConversationDetails,
  getPaginatedMessagesApi,
  createConversationApi,
  renameConversationApi,
  deleteConversationApi,
  pinConversationApi,
  sendMessageApi,
} from "../api/chat"
import type { Conversation, Message, PaginatedMessagesResponse } from "@/types/api"
import { normalizeError, APIError } from "../api/errors"

/** Fetch all active conversation sessions. */
export const useConversationsQuery = () => {
  return useQuery<Conversation[], APIError>({
    queryKey: queryKeys.conversations.list(),
    queryFn: listConversations,
    staleTime: 1000 * 60 * 5,
  })
}

/** Fetch a single conversation session by ID. */
export const useConversationDetailQuery = (sessionId: string | null) => {
  return useQuery<Conversation | null, APIError>({
    queryKey: queryKeys.conversations.detail(sessionId || ""),
    queryFn: async () => {
      if (!sessionId) return null
      return await getConversationDetails(sessionId)
    },
    staleTime: 1000 * 60 * 5,
  })
}

/** Fetch paginated conversation messages for infinite scrolling. */
export const useInfiniteConversationMessagesQuery = (sessionId: string | null, limit = 100) => {
  return useInfiniteQuery<PaginatedMessagesResponse, APIError>({
    queryKey: queryKeys.conversations.messages(sessionId || ""),
    queryFn: async ({ pageParam, signal }) => {
      if (!sessionId) {
        return { messages: [], next_cursor: null, has_more: false }
      }
      const result = await getPaginatedMessagesApi(sessionId, limit, pageParam as number | null, signal)
      console.log('[PAGINATION] Backend response:', {
        session_id: sessionId,
        pageParam,
        messages_count: result.messages?.length,
        has_more: result.has_more,
        next_cursor: result.next_cursor,
      })
      return result
    },
    initialPageParam: null as number | null,
    getNextPageParam: (lastPage) => {
      const next = lastPage.has_more ? lastPage.next_cursor : undefined
      console.log('[PAGINATION] getNextPageParam:', {
        has_more: lastPage.has_more,
        next_cursor: lastPage.next_cursor,
        resolved_next: next,
      })
      return next
    },
    enabled: Boolean(sessionId),
    staleTime: 1000 * 60 * 5,
    gcTime: 1000 * 60 * 60 * 24, // Preserve page cache for 24 hours across navigation
  })
}

/** Send a message to the backend /chat endpoint. */
export const useSendMessageMutation = () => {
  const queryClient = useQueryClient()

  return useMutation<
    { response: string; userMessage: Message; assistantMessage: Message },
    APIError,
    { session_id: string; message: string; attachedFiles?: Array<{ name: string; type: string }> }
  >({
    mutationFn: async ({ session_id, message, attachedFiles }) => {
      if (attachedFiles) {
        void attachedFiles
      }
      const userTime = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      const userMessage: Message = { id: `user-${Date.now()}`, role: "user", content: message, timestamp: userTime }
      try {
        const apiResponse = await sendMessageApi(session_id, message)
        const assistantTime = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
        const assistantMessage: Message = { id: `assistant-${Date.now()}`, role: "assistant", content: apiResponse.response, timestamp: assistantTime }
        return { response: apiResponse.response, userMessage, assistantMessage }
      } catch (rawError) {
        throw normalizeError(rawError)
      }
    },
    onSuccess: (data, variables) => {
      if (variables?.session_id) {
        queryClient.setQueryData<InfiniteData<PaginatedMessagesResponse>>(
          queryKeys.conversations.messages(variables.session_id),
          (oldData) => {
            if (!oldData || !oldData.pages || oldData.pages.length === 0) {
              return {
                pageParams: [null],
                pages: [{ messages: [data.userMessage, data.assistantMessage], next_cursor: null, has_more: false }],
              }
            }
            const newPages = [...oldData.pages]
            const newestPage = newPages[0]
            const existingIds = new Set(newestPage.messages.map((m) => m.id))
            const toAdd: Message[] = []
            if (!existingIds.has(data.userMessage.id)) toAdd.push(data.userMessage)
            if (!existingIds.has(data.assistantMessage.id)) toAdd.push(data.assistantMessage)

            newPages[0] = {
              ...newestPage,
              messages: [...newestPage.messages, ...toAdd],
            }
            console.log('[CACHE UPDATE] setQueryData in useSendMessageMutation — page count preserved:', newPages.length)
            return {
              ...oldData,
              pages: newPages,
            }
          }
        )
      }
    },
    onSettled: (_data, _error, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.conversations.list() })
      if (variables?.session_id) {
        queryClient.invalidateQueries({ queryKey: queryKeys.conversations.detail(variables.session_id) })
      }
    },
  })
}

/** Create a new conversation thread. */
export const useCreateConversationMutation = () => {
  const queryClient = useQueryClient()
  return useMutation<Conversation, APIError, void>({
    mutationFn: async () => {
      return await createConversationApi()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.conversations.list() })
    },
  })
}

/** Delete a conversation thread. */
export const useDeleteConversationMutation = () => {
  const queryClient = useQueryClient()
  return useMutation<void, APIError, string>({
    mutationFn: async (sessionId) => {
      await deleteConversationApi(sessionId)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.conversations.list() })
    },
  })
}

/** Rename a conversation thread title. */
export const useRenameConversationMutation = () => {
  const queryClient = useQueryClient()
  return useMutation<void, APIError, { sessionId: string; title: string }>({
    mutationFn: async ({ sessionId, title }) => {
      await renameConversationApi(sessionId, title)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.conversations.list() })
    },
  })
}

/** Toggle pinned status for a conversation thread. */
export const useTogglePinMutation = () => {
  const queryClient = useQueryClient()
  return useMutation<void, APIError, string>({
    mutationFn: async (sessionId) => {
      const conv = await getConversationDetails(sessionId)
      await pinConversationApi(sessionId, !conv.pinned)
    },
    onSuccess: (_, sessionId) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.conversations.list() })
      queryClient.invalidateQueries({ queryKey: queryKeys.conversations.detail(sessionId) })
    },
  })
}
