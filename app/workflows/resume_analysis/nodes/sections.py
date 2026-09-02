import logging
from typing import Callable, Coroutine, Any
from app.models.analysis import SectionsAnalysisOutput
from app.prompts.resume.sections import SECTIONS_SYSTEM_PROMPT, SECTIONS_USER_PROMPT
from app.services.llm_service import LLMService
from app.utils.validation import validate_sections
from app.workflows.resume_analysis.state import ResumeAnalysisState

logger = logging.getLogger(__name__)


def create_sections_node(
    llm_service: LLMService,
) -> Callable[[ResumeAnalysisState], Coroutine[Any, Any, dict]]:
    """Factory to create the 7-section analysis node."""

    async def sections_node(state: ResumeAnalysisState) -> dict:
        logger.info("Executing 7-Section Analysis Node")
        jd = state.get("job_description")
        jd_context = f"\nJob Description Context:\n{jd}\n" if jd and jd.strip() else ""

        prompt = SECTIONS_USER_PROMPT.format(
            target_role=state["target_role"],
            experience_level=state["experience_level"],
            optional_jd_context=jd_context,
            resume_text=state["resume_text"],
        )

        result: SectionsAnalysisOutput = await llm_service.generate_structured(
            schema=SectionsAnalysisOutput,
            prompt=prompt,
            system_instruction=SECTIONS_SYSTEM_PROMPT,
        )

        validated_sections = validate_sections(result.sections)

        return {
            "sections": validated_sections,
        }

    return sections_node
