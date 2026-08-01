"""
Jarvis AIOS — Knowledge Routing Test Suite
-------------------------------------------

Verifies intent classification and knowledge routing across:
1. General Knowledge queries (e.g. "Who is Elon Musk?") -> GENERAL_KNOWLEDGE / LLM
2. Conversation Memory queries (e.g. "Who am I?") -> MEMORY
3. Document QA queries (e.g. "Summarize this PDF") -> DOCUMENT_QA / RAG
4. Live Search queries (e.g. "Bitcoin price") -> LIVE_SEARCH / Search Tool
5. Tool Execution queries (e.g. "List workspace files") -> TOOL / Tool Engine
6. Document QA with no matching chunk -> RAG Hard Gate Fallback
"""

from app.Jarvis.intent_router import QueryIntent, QueryIntentClassifier
from app.Jarvis.runtime import _evaluate_tool_and_rag_context


def test_classify_general_knowledge():
    """General knowledge questions should classify as GENERAL_KNOWLEDGE."""
    q1 = "Who is Elon Musk?"
    q2 = "Explain FastAPI"
    q3 = "What is LangGraph?"
    q4 = "Difference between SQL and NoSQL"
    q5 = "Explain JWT"

    for query in [q1, q2, q3, q4, q5]:
        intent = QueryIntentClassifier.classify(query)
        assert intent == QueryIntent.GENERAL_KNOWLEDGE, f"Expected GENERAL_KNOWLEDGE for '{query}', got {intent}"


def test_classify_memory():
    """Memory and identity questions should classify as MEMORY."""
    q1 = "Who am I?"
    q2 = "What is my name?"
    q3 = "What did I tell you?"
    q4 = "What project are we building?"

    for query in [q1, q2, q3, q4]:
        intent = QueryIntentClassifier.classify(query)
        assert intent == QueryIntent.MEMORY, f"Expected MEMORY for '{query}', got {intent}"


def test_classify_document_qa():
    """Explicit document requests or queries with active attachments should classify as DOCUMENT_QA."""
    q1 = "Summarize this PDF"
    q2 = "Explain page 10"
    q3 = "What does the report say?"
    q4 = "Search my documents"

    for query in [q1, q2, q3, q4]:
        intent = QueryIntentClassifier.classify(query)
        assert intent == QueryIntent.DOCUMENT_QA, f"Expected DOCUMENT_QA for '{query}', got {intent}"

    # Query with active attachment
    intent_attachment = QueryIntentClassifier.classify("What is this?", has_attachment=True)
    assert intent_attachment == QueryIntent.DOCUMENT_QA


def test_classify_live_search_structured():
    """Structured live data (stocks, crypto, weather domain) should classify as LIVE_SEARCH via Layer 1."""
    structured_queries = [
        "Bitcoin price",
        "Weather in New York",
        "Gold price today",
        "Nifty 50 index",
        "USD to INR exchange rate",
    ]
    for query in structured_queries:
        intent = QueryIntentClassifier.classify(query)
        assert intent == QueryIntent.LIVE_SEARCH, f"Expected LIVE_SEARCH for '{query}', got {intent}"


def test_classify_live_search_time_sensitive():
    """Time-sensitive product/version/news queries must route to LIVE_SEARCH, not GENERAL_KNOWLEDGE."""
    time_sensitive_queries = [
        "latest iPhone models",
        "latest MacBook chips",
        "latest AI news",
        "newest Python version",
        "current CEO of Intel",
        "latest React version",
        "today's weather",
        "IPL score today",
        "latest OpenAI model",
        "current Android version",
        "what is the latest MacOS",
        "newest LLM released",
        "latest breaking news",
        "recently released GPT model",
        "latest GPU from NVIDIA",
    ]
    for query in time_sensitive_queries:
        intent = QueryIntentClassifier.classify(query)
        assert intent == QueryIntent.LIVE_SEARCH, (
            f"Expected LIVE_SEARCH for time-sensitive query '{query}', got {intent}"
        )


def test_stable_knowledge_stays_general():
    """Stable conceptual/technical questions must NOT be routed to LIVE_SEARCH."""
    stable_queries = [
        "Explain FastAPI",
        "What is LangGraph?",
        "How does JWT work?",
        "Difference between SQL and NoSQL",
        "Who is Elon Musk?",
        "What is a transformer model?",
        "Explain how Python decorators work",
        "What is the CAP theorem?",
    ]
    for query in stable_queries:
        intent = QueryIntentClassifier.classify(query)
        assert intent == QueryIntent.GENERAL_KNOWLEDGE, (
            f"Expected GENERAL_KNOWLEDGE for stable query '{query}', got {intent}"
        )


def test_classify_tool():
    """Tool invocation queries should classify as TOOL."""
    q1 = "List workspace files"
    q2 = "Read file sample.txt"
    q3 = "Run python code"

    for query in [q1, q2, q3]:
        intent = QueryIntentClassifier.classify(query)
        assert intent == QueryIntent.TOOL, f"Expected TOOL for '{query}', got {intent}"


def test_evaluate_general_knowledge_no_rag_fallback():
    """General knowledge questions must return no RAG fallback directives."""
    messages = _evaluate_tool_and_rag_context("Who is Elon Musk?")
    assert messages == []  # No RAG fallback, direct LLM generation


def test_evaluate_memory_identity_response():
    """Memory identity queries ('Who am I?') should return memory directive, not document fallback."""
    messages = _evaluate_tool_and_rag_context("Who am I?")
    assert len(messages) == 1
    content = str(messages[0].content)
    assert "MEMORY SUBSYSTEM DIRECTIVE" in content
    assert "I couldn't find sufficient evidence in the uploaded documents" not in content


def test_evaluate_document_qa_unmatched_fallback():
    """Explicit document QA query ('Summarize the attached report document') must:
    1. Classify as DOCUMENT_QA (due to 'the attached' keyword).
    2. Return RAG HARD GATE FAILURE when no matching document chunks exist.
    """
    # Step 1: Classifier must route this as DOCUMENT_QA
    intent = QueryIntentClassifier.classify("Summarize the attached report document")
    assert intent == QueryIntent.DOCUMENT_QA, f"Expected DOCUMENT_QA but got {intent}"

    # Step 2: Runtime must return RAG fallback when no document chunks are found
    messages = _evaluate_tool_and_rag_context(
        "Summarize the attached report document",
        session_id="test_session_nonexistent",
    )
    assert len(messages) == 1, f"Expected 1 message (RAG fallback), got {len(messages)}"
    content = str(messages[0].content)
    assert "RAG HARD GATE FAILURE" in content
    assert "I couldn't find sufficient evidence in the uploaded documents." in content
