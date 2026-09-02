import logging
from typing import Callable, Coroutine, Any
from app.models.analysis import FullResumeAnalysisOutput
from app.prompts.resume.comprehensive import (
    COMPREHENSIVE_SYSTEM_PROMPT,
    COMPREHENSIVE_USER_PROMPT,
)
from app.services.llm_service import LLMService
from app.workflows.resume_analysis.state import ResumeAnalysisState

logger = logging.getLogger(__name__)


def create_comprehensive_analysis_node(
    llm_service: LLMService,
) -> Callable[[ResumeAnalysisState], Coroutine[Any, Any, dict]]:
    """Factory to create the fast, unified comprehensive analysis node."""

    async def comprehensive_analysis_node(state: ResumeAnalysisState) -> dict:
        logger.info("Executing Comprehensive Resume Analysis Node")
        jd = state.get("job_description")
        jd_context = f"\nTarget Job Description:\n\"\"\"\n{jd}\n\"\"\"\n" if jd and jd.strip() else "\n(No specific Job Description provided; evaluate against standard target role expectations and set job_match_score to null)\n"

        prompt = COMPREHENSIVE_USER_PROMPT.format(
            target_role=state["target_role"],
            experience_level=state["experience_level"],
            job_description_context=jd_context,
            resume_text=state["resume_text"],
        )

        result: FullResumeAnalysisOutput = await llm_service.generate_structured(
            schema=FullResumeAnalysisOutput,
            prompt=prompt,
            system_instruction=COMPREHENSIVE_SYSTEM_PROMPT,
        )

        # Ensure job_match_score is null if no JD was provided
        job_match_score = result.job_match_score if jd and jd.strip() else None

        return {
            "overall_score": result.overall_score,
            "ats_score": result.ats_score,
            "job_match_score": job_match_score,
            "summary": result.summary,
            "sections": result.sections,
            "strengths": result.strengths,
            "weaknesses": result.weaknesses,
            "missing_skills": result.missing_skills,
            "missing_keywords": result.missing_keywords,
            "recommendations": result.recommendations,
            "improvements": result.improvements,
        }

    return comprehensive_analysis_node
