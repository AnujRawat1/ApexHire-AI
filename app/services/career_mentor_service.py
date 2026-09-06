import logging
from typing import Optional

from app.models.career_mentor import (
    CareerMentorChatRequest,
    CareerMentorChatResponse,
)
from app.services.llm_service import LLMService
from app.workflows.career_mentor import build_career_mentor_graph
from app.workflows.career_mentor.state import CareerMentorState

logger = logging.getLogger(__name__)


class CareerMentorService:
    """Service layer orchestrating the Career Mentor LangGraph conversational pipeline."""

    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service or LLMService()
        self.graph = build_career_mentor_graph(self.llm_service)

    async def chat(self, request: CareerMentorChatRequest) -> CareerMentorChatResponse:
        logger.info(
            f"Initiating Career Mentor chat: role='{request.target_role}', "
            f"goal='{request.career_goal}', history_length={len(request.chat_history)}"
        )

        initial_state: CareerMentorState = {
            "current_message": request.message,
            "target_role": request.target_role,
            "career_goal": request.career_goal,
            "resume_text": request.resume_text,
            "skills": request.skills,
            "candidate_name": request.candidate_name,
            "chat_history": [msg.model_dump() for msg in request.chat_history],
        }

        final_state: CareerMentorState = await self.graph.ainvoke(initial_state)

        return CareerMentorChatResponse(
            success=True,
            reply=final_state.get("reply", ""),
            suggested_follow_ups=final_state.get("suggested_follow_ups", []),
            target_role=request.target_role,
            career_goal=request.career_goal,
        )
