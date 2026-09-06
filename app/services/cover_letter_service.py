import time
import logging
from typing import Optional

from app.config.settings import Settings, get_settings
from app.exceptions.ai_exceptions import AIServiceException
from app.models.requests import CoverLetterGenerateRequest
from app.models.responses import CoverLetterGenerateResponse
from app.services.llm_service import LLMService
from app.services.provider_service import ProviderService
from app.workflows.cover_letter.graph import build_cover_letter_graph
from app.workflows.cover_letter.state import CoverLetterState

logger = logging.getLogger(__name__)


class CoverLetterService:
    """Core domain service for executing LangGraph cover letter workflows."""

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
        self._graph = build_cover_letter_graph(self.llm_service)

    async def generate_cover_letter(
        self, request: CoverLetterGenerateRequest
    ) -> CoverLetterGenerateResponse:
        """Executes the end-to-end LangGraph cover letter workflow."""
        start_time = time.perf_counter()
        logger.info(
            f"Starting cover letter workflow: role='{request.target_role}', "
            f"company='{request.company_name}', tone='{request.tone}', "
            f"has_resume={bool(request.resume_text)}, "
            f"has_jd={bool(request.job_description)}"
        )

        initial_state: CoverLetterState = {
            "candidate_name": request.candidate_name,
            "candidate_email": request.candidate_email,
            "target_role": request.target_role,
            "company_name": request.company_name,
            "job_description": request.job_description,
            "resume_text": request.resume_text,
            "skills": request.skills,
            "additional_info": request.additional_info,
            "tone": request.tone,
        }

        try:
            final_state: CoverLetterState = await self._graph.ainvoke(initial_state)
        except AIServiceException:
            raise
        except Exception as e:
            logger.exception(f"Unexpected error during cover letter workflow: {str(e)}")
            raise AIServiceException(f"Cover letter generation failed: {str(e)}") from e

        duration = (time.perf_counter() - start_time) * 1000
        logger.info(
            f"Completed cover letter workflow in {duration:.2f}ms for role '{request.target_role}' "
            f"at '{request.company_name}'"
        )

        return CoverLetterGenerateResponse(
            content=final_state["content"],
            key_highlights=final_state.get("key_highlights") or [],
            target_role=request.target_role,
            company_name=request.company_name,
            tone=request.tone,
        )
