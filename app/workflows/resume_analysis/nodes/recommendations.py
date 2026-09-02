import logging
from typing import Callable, Coroutine, Any
from app.models.analysis import RecommendationsOutput
from app.prompts.resume.recommendations import (
    RECOMMENDATIONS_SYSTEM_PROMPT,
    RECOMMENDATIONS_USER_PROMPT,
)
from app.services.llm_service import LLMService
from app.utils.validation import validate_recommendations
from app.workflows.resume_analysis.state import ResumeAnalysisState

logger = logging.getLogger(__name__)


def create_recommendations_node(
    llm_service: LLMService,
) -> Callable[[ResumeAnalysisState], Coroutine[Any, Any, dict]]:
    """Factory to create the Prioritized Recommendations analysis node."""

    async def recommendations_node(state: ResumeAnalysisState) -> dict:
        logger.info("Executing Recommendations Node")
        jd = state.get("job_description")
        jd_context = f"\nJob Description Context:\n{jd}\n" if jd and jd.strip() else ""

        prompt = RECOMMENDATIONS_USER_PROMPT.format(
            target_role=state["target_role"],
            experience_level=state["experience_level"],
            optional_jd_context=jd_context,
            resume_text=state["resume_text"],
        )

        result: RecommendationsOutput = await llm_service.generate_structured(
            schema=RecommendationsOutput,
            prompt=prompt,
            system_instruction=RECOMMENDATIONS_SYSTEM_PROMPT,
        )

        validated_recs = validate_recommendations(result.recommendations)

        return {
            "recommendations": validated_recs,
        }

    return recommendations_node
