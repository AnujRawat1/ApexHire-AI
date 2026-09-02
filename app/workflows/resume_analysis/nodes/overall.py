import logging
from typing import Callable, Coroutine, Any
from app.models.analysis import OverallAnalysisOutput
from app.prompts.resume.overall import OVERALL_SYSTEM_PROMPT, OVERALL_USER_PROMPT
from app.services.llm_service import LLMService
from app.workflows.resume_analysis.state import ResumeAnalysisState

logger = logging.getLogger(__name__)


def create_overall_node(
    llm_service: LLMService,
) -> Callable[[ResumeAnalysisState], Coroutine[Any, Any, dict]]:
    """Factory to create the overall analysis node."""

    async def overall_node(state: ResumeAnalysisState) -> dict:
        logger.info("Executing Overall Analysis Node")
        prompt = OVERALL_USER_PROMPT.format(
            target_role=state["target_role"],
            experience_level=state["experience_level"],
            resume_text=state["resume_text"],
        )

        result: OverallAnalysisOutput = await llm_service.generate_structured(
            schema=OverallAnalysisOutput,
            prompt=prompt,
            system_instruction=OVERALL_SYSTEM_PROMPT,
        )

        return {
            "overall_score": result.overall_score,
            "summary": result.summary,
        }

    return overall_node
