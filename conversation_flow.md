# Conversation Flow Specifications

## 1. Flow Overview

The conversation subsystem handles end-to-end communication between the user's workspace interface and the backend AIOS engine:

1. **Session Selection**: User selects or creates a conversation session (`session_id`).
2. **Message Dispatch**: User submits prompt; request is sent to `POST /chat`.
3. **Session Ownership Validation**: Backend verifies `session_id` belongs to the authenticated JWT user.
4. **Cognitive Runtime Execution**: Runtime constructs state, delegates to LangGraph and Tool Engine, and produces answer.
5. **Message Persistence & Rendering**: Assistant response is appended to the message history, saved to storage, and displayed in the UI.

---

## 2. Session Lifecycle States

| State | Trigger | Action / Outcome |
| :--- | :--- | :--- |
| **Session Active** | User clicks thread in Sidebar | Sets `selectedId`, renders `messages` history |
| **Session Created** | User clicks "New Chat" | Creates `ses_<timestamp>`, initializes empty history |
| **Message Pending** | Prompt submitted | Displays thinking indicator (`isPending = true`) |
| **Response Received** | `POST /chat` returns 200 OK | Appends `assistantMessage`, clears `isPending` |
| **Error Handled** | `POST /chat` fails (e.g. 401/403/500/0) | Displays error banner, offers `Retry` action |
| **Session Deleted** | User clicks Delete | Removes session ID, selects next remaining thread |
