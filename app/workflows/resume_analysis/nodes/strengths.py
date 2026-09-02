import logging
from typing import Callable, Coroutine, Any
from app.models.analysis import StrengthsWeaknessesOutput
from app.prompts.resume.strengths import STRENGTHS_SYSTEM_PROMPT, STRENGTHS_USER_PROMPT
from app.services.llm_service import LLMService
from app.utils.validation import sanitize_string_list
from app.workflows.resume_analysis.state import ResumeAnalysisState

logger = logging.getLogger(__name__)


def create_strengths_node(
    llm_service: LLMService,
) -> Callable[[ResumeAnalysisState], Coroutine[Any, Any, dict]]:
    """Factory to create the Strengths and Weaknesses analysis node."""

    async def strengths_node(state: ResumeAnalysisState) -> dict:
        logger.info("Executing Strengths and Weaknesses Analysis Node")
        jd = state.get("job_description")
        jd_context = f"\nJob Description Context:\n{jd}\n" if jd and jd.strip() else ""

        prompt = STRENGTHS_USER_PROMPT.format(
            target_role=state["target_role"],
            experience_level=state["experience_level"],
            optional_jd_context=jd_context,
            resume_text=state["resume_text"],
        )

        result: StrengthsWeaknessesOutput = await llm_service.generate_structured(
            schema=StrengthsWeaknessesOutput,
            prompt=prompt,
            system_instruction=STRENGTHS_SYSTEM_PROMPT,
        )

        return {
            "strengths": sanitize_string_list(result.strengths),
            "weaknesses": sanitize_string_list(result.weaknesses),
        }

    return strengths_node
