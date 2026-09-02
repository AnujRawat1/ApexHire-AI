import time
import logging
from typing import Optional

from app.config.settings import Settings, get_settings
from app.exceptions.ai_exceptions import (
    AIServiceException,
    InvalidAnalysisRequestException,
)
from app.models.requests import ResumeAnalysisRequest
from app.models.responses import AnalysisResultResponse
from app.services.llm_service import LLMService
from app.services.provider_service import ProviderService
from app.workflows.resume_analysis.graph import build_resume_analysis_graph
from app.workflows.resume_analysis.state import ResumeAnalysisState

logger = logging.getLogger(__name__)


class AnalysisService:
    """Core domain service for executing resume analysis workflows."""

    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        settings: Optional[Settings] = None,
    ):
        self.settings = settings or get_settings()
        self.provider_service = ProviderService(self.settings)
        self.llm_service = llm_service or LLMService(
            provider_service=self.provider_service, settings=self.settings
        )
        self._graph = build_resume_analysis_graph(self.llm_service)

    async def analyze_resume(
        self, request: ResumeAnalysisRequest
    ) -> AnalysisResultResponse:
        """Executes the end-to-end LangGraph resume analysis workflow."""
        start_time = time.perf_counter()
        logger.info(
            f"Starting resume analysis workflow: target_role='{request.target_role}', "
            f"experience_level='{request.experience_level}', "
            f"has_job_description={bool(request.job_description)}"
        )

        initial_state: ResumeAnalysisState = {
            "resume_text": request.resume_text,
            "target_role": request.target_role,
            "experience_level": request.experience_level,
            "job_description": request.job_description,
        }

        try:
            final_state: ResumeAnalysisState = await self._graph.ainvoke(initial_state)
        except AIServiceException:
            raise
        except Exception as e:
            logger.exception(f"Unexpected error during resume analysis workflow: {str(e)}")
            raise AIServiceException(f"Resume analysis failed: {str(e)}") from e

        duration = (time.perf_counter() - start_time) * 1000
        logger.info(
            f"Completed resume analysis workflow in {duration:.2f}ms. "
            f"Overall score: {final_state.get('overall_score')}, "
            f"ATS score: {final_state.get('ats_score')}, "
            f"Job match score: {final_state.get('job_match_score')}"
        )

        return AnalysisResultResponse(
            overall_score=final_state["overall_score"],
            ats_score=final_state["ats_score"],
            job_match_score=final_state.get("job_match_score"),
            summary=final_state["summary"],
            sections=final_state.get("sections") or [],
            strengths=final_state.get("strengths") or [],
            weaknesses=final_state.get("weaknesses") or [],
            missing_skills=final_state.get("missing_skills") or [],
            missing_keywords=final_state.get("missing_keywords") or [],
            recommendations=final_state.get("recommendations") or [],
            improvements=final_state.get("improvements") or [],
        )
