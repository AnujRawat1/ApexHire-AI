import logging
from typing import Callable, Coroutine, Any
from app.models.analysis import JobMatchOutput
from app.prompts.resume.job_match import JOB_MATCH_SYSTEM_PROMPT, JOB_MATCH_USER_PROMPT
from app.services.llm_service import LLMService
from app.workflows.resume_analysis.state import ResumeAnalysisState

logger = logging.getLogger(__name__)


def create_job_match_node(
    llm_service: LLMService,
) -> Callable[[ResumeAnalysisState], Coroutine[Any, Any, dict]]:
    """Factory to create the Job Match analysis node."""

    async def job_match_node(state: ResumeAnalysisState) -> dict:
        jd = state.get("job_description")
        if not jd or not jd.strip():
            logger.info("No Job Description provided. Setting job_match_score to None.")
            return {"job_match_score": None}

        logger.info("Executing Job Match Analysis Node against provided Job Description")
        prompt = JOB_MATCH_USER_PROMPT.format(
            target_role=state["target_role"],
            experience_level=state["experience_level"],
            job_description=jd,
            resume_text=state["resume_text"],
        )

        result: JobMatchOutput = await llm_service.generate_structured(
            schema=JobMatchOutput,
            prompt=prompt,
            system_instruction=JOB_MATCH_SYSTEM_PROMPT,
        )

        return {
            "job_match_score": result.job_match_score,
        }

    return job_match_node
