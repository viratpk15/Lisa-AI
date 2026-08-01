"""
Jarvis Runtime

Public entry point for Jarvis AIOS. Constructs the initial LangGraph state
and invokes the graph. Wraps each request in an execution trace so that
every request produces a complete, developer-friendly trace (observability).
Tracing is fully optional: if tracing fails, the request proceeds normally.
"""

from datetime import datetime
import json
import logging
import time
import uuid
from typing import Generator

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.LangGraph.graph import graph
from app.LLM.client import llm_client
from app.Memory.manager import memory_manager
from app.Observability.manager import observability_manager
from app.Observability.trace import calculate_duration, measure_time, trace_context
from app.Prompts.conversation import CONVERSATION_PROMPT
from app.Tools.registry import registry
from app.RAG.rag_manager import rag_manager
from app.Tools.search_providers.classifier import SearchIntentClassifier

logger = logging.getLogger(__name__)

# Maximum number of characters of the user request stored in a trace.
_MAX_TRACED_REQUEST_LENGTH: int = 500


def _format_sse(event_type: str, data: dict) -> str:
    """Format structured Server-Sent Event (SSE) payload string."""
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


def _clean_assistant_text(raw_text: str) -> str:
    """Extract clean text from raw LLM output or JSON envelopes (e.g. {"type":"final","response":"..."})."""
    if not raw_text:
        return ""
    text = raw_text.strip()
    if text.startswith("{") and text.endswith("}"):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                if "response" in parsed and isinstance(parsed["response"], str):
                    return parsed["response"]
                if "data" in parsed and isinstance(parsed["data"], str):
                    return parsed["data"]
        except Exception:
            pass
    return text


def _get_runtime_context_message() -> SystemMessage:
    """Generate dynamic system context including current date and time."""
    now = datetime.now()
    formatted = now.strftime("%A, %B %d, %Y at %I:%M %p")
    ctx_text = (
        f"--- RUNTIME ENVIRONMENT CONTEXT ---\n"
        f"Current System Date & Time: {formatted}\n"
        f"Note: Use this temporal context ONLY when answering queries that specifically require temporal grounding.\n"
        f"Do NOT mention date, time, system status, or disclaimers unless the user specifically asks for them.\n"
        f"-----------------------------------"
    )
    return SystemMessage(content=ctx_text)


# Session-level search memory: stores last search results per session for follow-up reuse.
# Structure: { session_id: {"query": str, "provider": str, "results": list, "citations": str} }
_SESSION_SEARCH_MEMORY: dict[str, dict] = {}

# Follow-up phrases that signal the user wants to dig into previous search results
_FOLLOWUP_SIGNALS = [
    "tell me more", "more about", "elaborate", "expand on", "go deeper",
    "second article", "second result", "first article", "first result",
    "third article", "third result", "last article", "last result",
    "source?", "what's the source", "where did you get", "the article",
    "summarize again", "summarize that", "re-summarize",
    "from that search", "in that article", "those results",
]


from app.Tools.live_information import live_tool_registry, ToolResult

from app.Jarvis.intent_router import QueryIntent, QueryIntentClassifier

def _evaluate_tool_and_rag_context(
    message: str,
    session_id: str = "",
    attachment_ids: list[str] | None = None,
    active_document_id: str | None = None,
    active_filename: str | None = None,
) -> list[SystemMessage]:
    """Knowledge Router: Classifies intent BEFORE retrieval and dispatches to appropriate subsystem."""
    has_active_doc = bool(active_document_id or active_filename)
    has_attachment = bool(attachment_ids)

    # If session_id is provided and there are session attachments, treat as doc-context session
    if not has_attachment and session_id:
        try:
            session_atts = rag_manager.repo.list_session_attachments(session_id)
            if session_atts:
                has_attachment = True
        except Exception:
            pass

    intent = QueryIntentClassifier.classify(
        message=message,
        has_active_doc=has_active_doc,
        has_attachment=has_attachment,
    )

    logger.info("[KNOWLEDGE-ROUTER] Query='%s' -> Classified Intent: %s", message[:60], intent.value)

    # 1. MEMORY INTENT
    if intent == QueryIntent.MEMORY:
        msg_lower = message.lower()
        if any(p in msg_lower for p in ["who am i", "what is my name", "what's my name", "do you know my name"]):
            mem_directive = (
                "=== MEMORY SUBSYSTEM DIRECTIVE ===\n"
                "The user is asking about their identity ('Who am I?' / 'What is my name?').\n"
                "1. Check the conversation history and memory below to see if the user previously stated their name or identity.\n"
                "2. If their name or identity was previously stated, tell them their name.\n"
                "3. If their name has NOT been provided in the conversation history or memory, respond naturally with:\n"
                "   'I don't know yet. You haven't told me your name.'\n"
                "4. Do NOT reference documents, files, or missing document evidence.\n"
                "==================================="
            )
            return [SystemMessage(content=mem_directive)]
        return []

    # 2. GENERAL KNOWLEDGE / CHAT INTENT
    if intent in (QueryIntent.GENERAL_KNOWLEDGE, QueryIntent.CHAT):
        # Answer directly using LLM knowledge. Zero RAG calls, zero document error fallbacks.
        return []

    # 3. LIVE SEARCH INTENT
    if intent == QueryIntent.LIVE_SEARCH:
        # Check structured live info first (stocks, crypto, weather, etc.)
        classification = SearchIntentClassifier.classify(message)
        if classification.is_live_info:
            domain = classification.domain or "commodity"
            logger.info(
                "[LIVE-DATA-LOG] Query='%s' Intent=%s Domain=%s Provider=%s Confidence=%.2f",
                message[:60], classification.intent, domain, classification.provider, classification.confidence
            )

            tool_result: ToolResult = live_tool_registry.dispatch(domain=domain, query=message)

            if not tool_result.success or not tool_result.verified or tool_result.confidence < 0.8:
                fail_closed_text = (
                    f"=== LIVE DATA HARD GATE FAILURE ===\n"
                    f"Domain: {domain} | Query: '{message}'\n"
                    f"Status: Fail-Closed - Verified live data unavailable ({tool_result.error or 'Unverified'})\n"
                    f"SYSTEM DIRECTIVE (FAIL CLOSED): Verified real-time data could not be retrieved from reliable sources.\n"
                    f"Do NOT invent, guess, estimate, or approximate numbers from pretrained memory.\n"
                    f"YOU MUST RESPOND EXACTLY WITH: 'I couldn't retrieve verified live data right now.'\n"
                    f"==================================="
                )
                return [SystemMessage(content=fail_closed_text)]

            structured_text = (
                f"=== VERIFIED LIVE STRUCTURED DATA ===\n"
                f"Domain: {domain} | Source: {tool_result.source} | Confidence: {tool_result.confidence} | Timestamp: {tool_result.timestamp.isoformat()}\n"
                f"Payload: {json.dumps(tool_result.payload, indent=2)}\n"
                f"=====================================\n"
                f"LLM FORMATTING DIRECTIVES:\n"
                f"1. You are acting ONLY as a text formatter for the verified JSON payload above.\n"
                f"2. Present the exact numeric values, units, and currency specified in the payload.\n"
                f"3. Do NOT infer, estimate, calculate, fill missing values, or alter any numbers."
            )
            return [SystemMessage(content=structured_text)]

        # General web search fallback for live events/news
        try:
            search_tool = registry.get("web_search")
            if search_tool:
                res = search_tool.execute(query=message)
                if res.get("status") == "success" and res.get("results"):
                    citation_blocks = [f"[Result {idx}]\nTitle: {r.get('title')}\nSource: {r.get('source')}\nSnippet: {r.get('snippet')}" for idx, r in enumerate(res["results"], start=1)]
                    return [SystemMessage(content="=== LIVE SEARCH RESULTS ===\n" + "\n\n".join(citation_blocks))]
        except Exception as e:
            logger.error("[SEARCH-ROUTER] Search Execution Exception: %s", str(e))
        return []

    # 4. TOOL INTENT
    if intent == QueryIntent.TOOL:
        msg_lower = message.lower()
        context_lines: list[str] = []

        # Date / Time
        if any(kw in msg_lower for kw in ["date", "time", "clock", "today", "day of week"]):
            dt_tool = registry.get("datetime")
            if dt_tool:
                res = dt_tool.execute()
                if res:
                    context_lines.append(f"Current Date & Time Tool Output: {res}")

        # Math / Calculation
        if any(kw in msg_lower for kw in ["calculate", "math", "evaluate", "square root", "factorial", "equation"]) or (
            any(op in message for op in ["+", "*", "/", "^"]) and any(c.isdigit() for c in message)
        ):
            calc_tool = registry.get("calculator")
            if calc_tool:
                expr = message.replace("calculate", "").replace("math", "").replace("evaluate", "").strip() or message
                res = calc_tool.execute(expression=expr)
                if res:
                    context_lines.append(f"Calculator Tool Output: {res}")

        # Python / Code execution
        if any(kw in msg_lower for kw in ["python", "run code", "execute code", "script"]):
            py_tool = registry.get("python")
            if py_tool:
                res = py_tool.execute(code=message)
                if res:
                    context_lines.append(f"Python Tool Output: {res}")

        # Filesystem
        if any(kw in msg_lower for kw in ["read file", "list workspace", "list files", "directory", "folder", "filesystem", "file content"]):
            fs_tool = registry.get("filesystem") or registry.get("file_reader")
            if fs_tool:
                res = fs_tool.execute(path="." if "list" in msg_lower else message)
                if res:
                    context_lines.append(f"Filesystem Tool Output: {res}")

        # Git
        if any(kw in msg_lower for kw in ["git", "repository", "commit", "branch", "diff"]):
            git_tool = registry.get("git")
            if git_tool:
                res = git_tool.execute(command="status" if "status" in msg_lower else "log")
                if res:
                    context_lines.append(f"Git Tool Output: {res}")

        # Browser
        if any(kw in msg_lower for kw in ["browse", "navigate url", "open page", "web page", "browser"]):
            browser_tool = registry.get("browser")
            if browser_tool:
                res = browser_tool.execute(url=message)
                if res:
                    context_lines.append(f"Browser Tool Output: {res}")

        if context_lines:
            combined_text = "--- RETRIEVED TOOL CONTEXT ---\n" + "\n".join(context_lines) + "\n-------------------------------"
            return [SystemMessage(content=combined_text)]
        return []

    # 5. DOCUMENT QA INTENT
    if intent == QueryIntent.DOCUMENT_QA:
        try:
            from app.RAG.reference_resolver import ReferenceResolver
            from app.Config.settings import RAG_MIN_CONFIDENCE

            session_atts = rag_manager.repo.list_session_attachments(session_id) if session_id else []
            target_doc_ids, primary_fn, is_comparison = ReferenceResolver.resolve_references(
                message=message,
                session_id=session_id,
                session_attachments=session_atts,
                active_document_id=active_document_id,
                active_filename=active_filename,
            )

            rag_res = rag_manager.hybrid_search(
                query=message,
                document_ids=target_doc_ids if target_doc_ids else None,
                filename=primary_fn if (primary_fn and not is_comparison) else None,
                session_id=session_id,
                top_k=5,
                alpha=0.50,
                use_reranker=True,
            )
            results = rag_res.get("results", [])
            top_score = results[0]["rerank_score"] if results else 0.0

            # FAIL-CLOSED HARD GATE ONLY FOR DOCUMENT QA INTENT
            if not results or top_score < RAG_MIN_CONFIDENCE:
                logger.warning(
                    "[RAG-LOG] HARD GATE HALTED for DOCUMENT_QA: Low retrieval confidence (score=%.4f < threshold=%.4f) for query='%s'",
                    top_score, RAG_MIN_CONFIDENCE, message[:60]
                )
                fail_closed_text = (
                    f"=== RAG HARD GATE FAILURE ===\n"
                    f"Query: '{message}'\n"
                    f"Status: Fail-Closed - Insufficient document evidence (Top Rerank Score: {top_score:.4f} < Threshold: {RAG_MIN_CONFIDENCE:.4f})\n"
                    f"SYSTEM DIRECTIVE (FAIL CLOSED): The retrieved document context does not contain sufficient evidence to answer this query.\n"
                    f"Do NOT invent, guess, estimate, or extrapolate from pretrained model memory.\n"
                    f"Do NOT invent project members, names, figures, tables, or slide contents.\n"
                    f"YOU MUST RESPOND EXACTLY WITH: 'I couldn't find sufficient evidence in the uploaded documents.'\n"
                    f"==================================="
                )
                return [SystemMessage(content=fail_closed_text)]

            from app.RAG.intent_classifier import DocumentIntent
            from app.RAG.response_planner import ResponsePlanner
            from app.RAG.prompts import (
                OVERVIEW_PROMPT_TEMPLATE,
                SUMMARIZATION_PROMPT_TEMPLATE,
                COMPARISON_PROMPT_TEMPLATE,
                PRESENTATION_PROMPT_TEMPLATE,
                QA_PROMPT_TEMPLATE,
            )

            doc_intent = rag_res.get("intent", DocumentIntent.Q_AND_A)
            doc_type = rag_res.get("document_type", "notes")
            resp_plan = ResponsePlanner.create_response_plan(doc_intent, doc_type, primary_filename=primary_fn or "Document")

            evidence_blocks = []
            for idx, r in enumerate(results, start=1):
                meta = r.get("metadata", {})
                fn = meta.get("filename") or primary_fn or "Document"
                pg = meta.get("page_number") or meta.get("slide_number") or 1
                sec = meta.get("heading") or meta.get("section") or "General"
                evidence_blocks.append(
                    f"[Evidence Chunk {idx}]\n"
                    f"Source: {fn} | Page/Slide: {pg} | Section: {sec}\n"
                    f"Chunk ID: {r.get('chunk_id')} | Rerank Score: {r.get('rerank_score')}\n"
                    f"Content:\n{r.get('raw_text', '')}"
                )

            structured_evidence_str = "\n\n".join(evidence_blocks)
            plan_obj = rag_res.get("retrieval_plan")
            strat_name = getattr(plan_obj, "strategy", "ADAPTIVE")

            if doc_intent == DocumentIntent.OVERVIEW:
                prompt_str = OVERVIEW_PROMPT_TEMPLATE.format(
                    primary_filename=primary_fn or "Document",
                    document_type=doc_type,
                    strategy=strat_name,
                    structured_evidence=structured_evidence_str,
                    response_directives=resp_plan.formatting_directives,
                )
            elif doc_intent == DocumentIntent.SUMMARIZATION:
                prompt_str = SUMMARIZATION_PROMPT_TEMPLATE.format(
                    primary_filename=primary_fn or "Document",
                    document_type=doc_type,
                    strategy=strat_name,
                    structured_evidence=structured_evidence_str,
                    response_directives=resp_plan.formatting_directives,
                )
            elif doc_intent == DocumentIntent.COMPARISON:
                prompt_str = COMPARISON_PROMPT_TEMPLATE.format(
                    primary_filename=primary_fn or "Documents",
                    strategy=strat_name,
                    structured_evidence=structured_evidence_str,
                    response_directives=resp_plan.formatting_directives,
                )
            elif doc_intent == DocumentIntent.PRESENTATION:
                prompt_str = PRESENTATION_PROMPT_TEMPLATE.format(
                    primary_filename=primary_fn or "Presentation",
                    strategy=strat_name,
                    structured_evidence=structured_evidence_str,
                    response_directives=resp_plan.formatting_directives,
                )
            else:
                prompt_str = QA_PROMPT_TEMPLATE.format(
                    primary_filename=primary_fn or "Document",
                    top_score=top_score,
                    structured_evidence=structured_evidence_str,
                )

            return [SystemMessage(content=prompt_str)]

        except Exception as e:
            logger.error("[RAG-LOG] Retrieval Error: %s", str(e))
            return []

    return []


class Jarvis:
    def chat(
        self,
        session_id: str,
        message: str,
    ) -> str:
        # Wrap the entire request in a trace. The trace is optional and
        # never affects execution: failures inside tracing are swallowed.
        with trace_context(
            session_id,
            message[:_MAX_TRACED_REQUEST_LENGTH],
        ):
            result = graph.invoke(
                {
                    "session_id": session_id,
                    "message": message,
                    "action": {},
                    "observation": {},
                    "response": "",
                    "iteration_count": 0,
                    "plan": {},
                    "request_type": "conversation",
                    "execution_outcome": None,
                    "execution_start_time": time.perf_counter(),
                    "replanning_count": 0,
                    "tool_retry_count": 0,
                    "consecutive_failures": 0,
                    "step_execution_history": [],
                    "termination_reason": None,
                }
            )

        raw_resp = result.get("response", "")
        return _clean_assistant_text(raw_resp)

    def chat_stream(
        self,
        session_id: str,
        message: str,
        attachment_ids: list[str] | None = None,
        active_document_id: str | None = None,
        active_filename: str | None = None,
    ) -> Generator[str, None, None]:
        """Stream chat tokens in real-time using provider-independent LLMClient and structured SSE."""
        start_time = measure_time()
        req_id = f"REQ-{uuid.uuid4().hex[:6]}"
        logger.info("[%s] START session=%s msg='%s'", req_id, session_id, message[:40].replace('\n', ' '))

        with trace_context(
            session_id,
            message[:_MAX_TRACED_REQUEST_LENGTH],
        ):
            # 1. Emit thinking event immediately
            yield _format_sse("thinking", {"status": "Thinking..."})

            # 2. Memory & semantic retrieval
            memory = memory_manager.get_conversation(session_id)
            mem_start = measure_time()
            relevant_memories = memory_manager.get_relevant_memories(
                session_id=session_id,
                query=message,
                top_k=5,
            )
            mem_duration = calculate_duration(mem_start)

            summary_used = bool(
                memory.messages
                and memory.messages[0].__class__.__name__ == "SystemMessage"
                and "Conversation Summary:" in memory.messages[0].content
            )
            observability_manager.record_memory_info(
                conversation_messages=len(memory.messages),
                summary_used=summary_used,
                semantic_memories=len(relevant_memories),
                retrieval_latency_ms=mem_duration,
            )

            # 3. Assemble system and context messages
            messages: list = [
                SystemMessage(content=CONVERSATION_PROMPT),
                _get_runtime_context_message(),
            ]
            messages.extend(memory.messages)

            if relevant_memories:
                memories_text = "Relevant Memories:\n" + "\n".join(
                    f"- {m.content}" for m in relevant_memories
                )
                messages.append(SystemMessage(content=memories_text))

            # Smart Routing: Connect ToolRegistry tools and RAGManager ReferenceResolver
            tool_rag_messages = _evaluate_tool_and_rag_context(
                message=message,
                session_id=session_id,
                attachment_ids=attachment_ids,
                active_document_id=active_document_id,
                active_filename=active_filename,
            )

            # Format user message payload with subsystem context for LLaMA-3 / Groq compatibility
            user_content = message
            if tool_rag_messages:
                context_str = "\n\n".join([str(m.content) for m in tool_rag_messages])
                user_content = f"{context_str}\n\nUser Query: {message}"

            user_msg = HumanMessage(content=user_content)
            messages.append(user_msg)

            # Save clean user message to memory & SQLite persistence
            memory.add_message(HumanMessage(content=message))
            logger.info("[%s] USER MESSAGE SAVED session=%s", req_id, session_id)

            logger.info("[%s] TOTAL MESSAGES SENT TO LLM: %d", req_id, len(messages))
            for idx, m in enumerate(messages):
                logger.info("[%s] LLM-INPUT-MSG[%d] type=%s content='%s'", req_id, idx, m.__class__.__name__, m.content[:80].replace('\n', ' '))

            accumulated_tokens: list[str] = []

            try:
                # 4. Stream tokens via provider-independent LLMClient abstraction
                for token in llm_client.stream(messages):
                    accumulated_tokens.append(token)
                    yield _format_sse("token", {"token": token})

                logger.info("[%s] STREAM COMPLETE session=%s", req_id, session_id)

                raw_full_response = "".join(accumulated_tokens)
                full_response = _clean_assistant_text(raw_full_response)

                # 5. Persist final assistant message ONLY upon successful completion
                memory.add_message(AIMessage(content=full_response))
                logger.info("[%s] ASSISTANT SAVED session=%s", req_id, session_id)

                # Record LLM usage metrics
                observability_manager.record_llm_usage(
                    model_name=getattr(llm_client.provider, "model", "") or "",
                    latency_ms=calculate_duration(start_time),
                )

                # 6. Emit done event with clean assistant text
                yield _format_sse("done", {"response": full_response})
                logger.info("[%s] END session=%s", req_id, session_id)

            except Exception as exc:
                logger.error("[%s] Inference exception during streaming for session %s: %s", req_id, session_id, str(exc))
                yield _format_sse("error", {"error": str(exc)})
                raise


jarvis = Jarvis()

