# Developer Walkthrough: Sprint 5.3 Conversation Integration

## 1. How Conversation Flow Works

1. **User enters text prompt** inside `Composer.tsx` and clicks Send or presses Enter.
2. `handleSend` inside `WorkspacePage.tsx` invokes `sendMessageMutation.mutate({ session_id, message })`.
3. `useSendMessageMutation` in `frontend/src/services/queries/chat.ts`:
   - Immediately appends user prompt to the session state (optimistic update).
   - Calls `sendMessageApi(session_id, message)` in `chat.ts`.
   - `apiClient` adds `Authorization: Bearer <jwt_token>` header and issues `POST /chat` request to backend.
4. **Backend FastAPI processing**:
   - `routes.py` verifies session ownership with `verify_session_ownership`.
   - `chat_service.chat(session_id, message)` delegates to `jarvis.chat(session_id, message)`.
   - Returns `{ response: "<AI generated text>" }`.
5. **Mutation completion**:
   - `assistantMessage` is appended to the conversation thread.
   - `saveStoredConversations` updates local storage cache.
   - `queryClient.invalidateQueries` triggers reactive component update across the UI.

---

## 2. Using React Query Hooks in Workspace Components

```typescript
import {
  useConversationsQuery,
  useSendMessageMutation,
  useCreateConversationMutation,
  useDeleteConversationMutation
} from "@/services/queries/chat"

// Access active session threads
const { data: conversations = [], isLoading } = useConversationsQuery()

// Dispatch chat mutation
const sendMessageMutation = useSendMessageMutation()

sendMessageMutation.mutate({
  session_id: activeSessionId,
  message: "Run diagnostics on memory cache"
})
```

---

## 3. Session Persistence & Browser Refresh

Conversations are maintained under `jarvis_conversations_v1` in `localStorage`.  
When a user refreshes their browser or returns to the application:
1. `useConversationsQuery` initializes with persisted sessions.
2. Selected session ID selects the matching conversation thread.
3. Message history renders immediately without data loss.
