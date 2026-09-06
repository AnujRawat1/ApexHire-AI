from langgraph.graph import StateGraph, START, END

from app.services.llm_service import LLMService
from app.workflows.career_mentor.nodes.chat_node import create_career_mentor_chat_node
from app.workflows.career_mentor.state import CareerMentorState


def build_career_mentor_graph(llm_service: LLMService):
    """Assembles and compiles the LangGraph StateGraph for Career Mentor chat."""
    workflow = StateGraph(CareerMentorState)

    chat_node = create_career_mentor_chat_node(llm_service)
    workflow.add_node("chat", chat_node)

    workflow.add_edge(START, "chat")
    workflow.add_edge("chat", END)

    return workflow.compile()
