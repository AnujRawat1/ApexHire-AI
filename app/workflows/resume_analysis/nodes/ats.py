import logging
from typing import Callable, Coroutine, Any
from app.models.analysis import ATSAnalysisOutput
from app.prompts.resume.ats import ATS_SYSTEM_PROMPT, ATS_USER_PROMPT
from app.services.llm_service import LLMService
from app.workflows.resume_analysis.state import ResumeAnalysisState

logger = logging.getLogger(__name__)


def create_ats_node(
    llm_service: LLMService,
) -> Callable[[ResumeAnalysisState], Coroutine[Any, Any, dict]]:
    """Factory to create the ATS assessment node."""

    async def ats_node(state: ResumeAnalysisState) -> dict:
        logger.info("Executing ATS Assessment Node")
        prompt = ATS_USER_PROMPT.format(
            target_role=state["target_role"],
            resume_text=state["resume_text"],
        )

        result: ATSAnalysisOutput = await llm_service.generate_structured(
            schema=ATSAnalysisOutput,
            prompt=prompt,
            system_instruction=ATS_SYSTEM_PROMPT,
        )

        return {
            "ats_score": result.ats_score,
        }

    return ats_node
