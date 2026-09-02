import logging
from typing import Callable, Coroutine, Any
from app.exceptions.ai_exceptions import AIResponseValidationException
from app.utils.validation import validate_score, validate_sections, validate_recommendations
from app.workflows.resume_analysis.state import ResumeAnalysisState

logger = logging.getLogger(__name__)


def create_validation_node() -> Callable[[ResumeAnalysisState], Coroutine[Any, Any, dict]]:
    """Factory to create the final workflow output validation node."""

    async def validation_node(state: ResumeAnalysisState) -> dict:
        logger.info("Executing Final Output Validation Node")

        # Validate Scores
        overall_score = validate_score(state.get("overall_score"), "overall_score", allow_none=False)
        ats_score = validate_score(state.get("ats_score"), "ats_score", allow_none=False)
        job_match_score = validate_score(
            state.get("job_match_score"),
            "job_match_score",
            allow_none=True if not state.get("job_description") else False,
        )

        summary = state.get("summary")
        if not summary or not summary.strip():
            raise AIResponseValidationException("Validation failed: summary is empty.")

        sections = validate_sections(state.get("sections") or [])
        recommendations = validate_recommendations(state.get("recommendations") or [])
        strengths = state.get("strengths") or []
        weaknesses = state.get("weaknesses") or []
        missing_skills = state.get("missing_skills") or []
        missing_keywords = state.get("missing_keywords") or []
        improvements = state.get("improvements") or []

        return {
            "overall_score": overall_score,
            "ats_score": ats_score,
            "job_match_score": job_match_score,
            "summary": summary.strip(),
            "sections": sections,
            "recommendations": recommendations,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "missing_skills": missing_skills,
            "missing_keywords": missing_keywords,
            "improvements": improvements,
            "is_valid": True,
        }

    return validation_node
