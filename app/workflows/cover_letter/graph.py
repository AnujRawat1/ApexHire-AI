import logging
from langgraph.graph import StateGraph, START, END

from app.services.llm_service import LLMService
from app.workflows.cover_letter.state import CoverLetterState
from app.workflows.cover_letter.nodes.generation import create_cover_letter_generation_node
from app.workflows.cover_letter.nodes.validation import create_cover_letter_validation_node

logger = logging.getLogger(__name__)


def build_cover_letter_graph(llm_service: LLMService):
    """Compiles the LangGraph StateGraph for cover letter generation and validation."""
    builder = StateGraph(CoverLetterState)

    # Register workflow nodes
    builder.add_node("generation", create_cover_letter_generation_node(llm_service))
    builder.add_node("validation", create_cover_letter_validation_node())

    # Build Graph Pipeline: START -> generation -> validation -> END
    builder.add_edge(START, "generation")
    builder.add_edge("generation", "validation")
    builder.add_edge("validation", END)

    logger.info("Compiled LangGraph Cover Letter Workflow")
    return builder.compile()
