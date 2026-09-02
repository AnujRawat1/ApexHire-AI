import logging
from typing import Callable, Coroutine, Any
from app.models.analysis import ImprovementsOutput
from app.prompts.resume.improvements import (
    IMPROVEMENTS_SYSTEM_PROMPT,
    IMPROVEMENTS_USER_PROMPT,
)
from app.services.llm_service import LLMService
from app.utils.validation import sanitize_string_list
from app.workflows.resume_analysis.state import ResumeAnalysisState

logger = logging.getLogger(__name__)


def create_improvements_node(
    llm_service: LLMService,
) -> Callable[[ResumeAnalysisState], Coroutine[Any, Any, dict]]:
    """Factory to create the Actionable Improvements analysis node."""

    async def improvements_node(state: ResumeAnalysisState) -> dict:
        logger.info("Executing Actionable Improvements Node")
        jd = state.get("job_description")
        jd_context = f"\nJob Description Context:\n{jd}\n" if jd and jd.strip() else ""

        prompt = IMPROVEMENTS_USER_PROMPT.format(
            target_role=state["target_role"],
            experience_level=state["experience_level"],
            optional_jd_context=jd_context,
            resume_text=state["resume_text"],
        )

        result: ImprovementsOutput = await llm_service.generate_structured(
            schema=ImprovementsOutput,
            prompt=prompt,
            system_instruction=IMPROVEMENTS_SYSTEM_PROMPT,
        )

        return {
            "improvements": sanitize_string_list(result.improvements),
        }

    return improvements_node
