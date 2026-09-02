import logging
from langgraph.graph import StateGraph, START, END

from app.services.llm_service import LLMService
from app.workflows.resume_analysis.state import ResumeAnalysisState
from app.workflows.resume_analysis.nodes.comprehensive import create_comprehensive_analysis_node
from app.workflows.resume_analysis.nodes.validation import create_validation_node

logger = logging.getLogger(__name__)


def build_resume_analysis_graph(llm_service: LLMService):
    """Compiles the high-speed LangGraph StateGraph for resume analysis."""
    builder = StateGraph(ResumeAnalysisState)

    # Register Workflow Nodes
    builder.add_node("comprehensive_analysis", create_comprehensive_analysis_node(llm_service))
    builder.add_node("validation", create_validation_node())

    # Build Graph Pipeline: START -> comprehensive_analysis -> validation -> END
    builder.add_edge(START, "comprehensive_analysis")
    builder.add_edge("comprehensive_analysis", "validation")
    builder.add_edge("validation", END)

    logger.info("Compiled High-Performance LangGraph Resume Analysis Workflow")
    return builder.compile()
