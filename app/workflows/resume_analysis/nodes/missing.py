import logging
from typing import Callable, Coroutine, Any
from app.models.analysis import MissingElementsOutput
from app.prompts.resume.missing import MISSING_SYSTEM_PROMPT, MISSING_USER_PROMPT
from app.services.llm_service import LLMService
from app.utils.validation import sanitize_string_list
from app.workflows.resume_analysis.state import ResumeAnalysisState

logger = logging.getLogger(__name__)


def create_missing_node(
    llm_service: LLMService,
) -> Callable[[ResumeAnalysisState], Coroutine[Any, Any, dict]]:
    """Factory to create the Missing Skills and Keywords analysis node."""

    async def missing_node(state: ResumeAnalysisState) -> dict:
        logger.info("Executing Missing Skills and Keywords Analysis Node")
        jd = state.get("job_description")
        jd_context = f"\nJob Description Context:\n{jd}\n" if jd and jd.strip() else ""

        prompt = MISSING_USER_PROMPT.format(
            target_role=state["target_role"],
            experience_level=state["experience_level"],
            optional_jd_context=jd_context,
            resume_text=state["resume_text"],
        )

        result: MissingElementsOutput = await llm_service.generate_structured(
            schema=MissingElementsOutput,
            prompt=prompt,
            system_instruction=MISSING_SYSTEM_PROMPT,
        )

        return {
            "missing_skills": sanitize_string_list(result.missing_skills),
            "missing_keywords": sanitize_string_list(result.missing_keywords),
        }

    return missing_node
