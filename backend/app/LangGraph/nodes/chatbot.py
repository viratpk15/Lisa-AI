from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from app.Memory.manager import memory_manager
from app.LangGraph.state import State
from app.LLM.client import llm_client

load_dotenv()

llm = llm_client


def chatbot(state: State):
    """
    LangGraph Chatbot Node

    Flow:
    1. Get conversation memory for this session
    2. Save user message
    3. Send full conversation to the LLM
    4. Save AI response
    5. Return updated state
    """

    # Get this user's conversation memory
    memory = memory_manager.get_conversation(state["session_id"])

    # Store user message
    memory.add_message(HumanMessage(content=state["message"]))

    # Send complete conversation history to the LLM
    response = llm.invoke(memory.messages)

    # Store AI response
    memory.add_message(AIMessage(content=response.content))

    # Update LangGraph state
    return {"response": response.content}
