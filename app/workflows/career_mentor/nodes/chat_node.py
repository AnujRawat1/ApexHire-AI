import re
import logging
from typing import Callable, Coroutine, Any, List

from app.models.career_mentor import CareerMentorOutput
from app.prompts.career_mentor import (
    CAREER_MENTOR_SYSTEM_PROMPT,
    CAREER_MENTOR_USER_PROMPT,
)
from app.services.llm_service import LLMService
from app.workflows.career_mentor.state import CareerMentorState
from app.workflows.cover_letter.nodes.generation import sanitize_extracted_text

logger = logging.getLogger(__name__)


def format_chat_history(history: List[dict]) -> str:
    """Formats recent conversation turns into a clean markdown block."""
    if not history:
        return "Conversation History: New conversation session started."

    formatted_turns = []
    # Use last 10 messages for sliding window
    recent_history = history[-10:]
    for msg in recent_history:
        role = "User" if msg.get("role") == "user" else "Mentor"
        content = (msg.get("content") or "").strip()
        formatted_turns.append(f"{role}: {content}")

    return "Recent Conversation History:\n" + "\n\n".join(formatted_turns)


def create_career_mentor_chat_node(
    llm_service: LLMService,
) -> Callable[[CareerMentorState], Coroutine[Any, Any, dict]]:
    """Factory creating the Career Mentor LangGraph chat node."""

    async def chat_node(state: CareerMentorState) -> dict:
        logger.info(
            f"Executing Career Mentor Chat Node: role='{state.get('target_role')}', "
            f"goal='{state.get('career_goal')}'"
        )

        candidate_name = (state.get("candidate_name") or "").strip() or "Candidate"
        target_role = (state.get("target_role") or "").strip() or "Software Engineer"
        career_goal = (state.get("career_goal") or "").strip() or "Advance engineering career"

        raw_resume = state.get("resume_text") or ""
        sanitized_resume = sanitize_extracted_text(raw_resume)
        resume_section = (
            f"Candidate Resume / Background:\n\"\"\"\n{sanitized_resume.strip()}\n\"\"\""
            if sanitized_resume.strip()
            else "Candidate Resume / Background: Not provided. Advise based on general industry benchmarks."
        )

        skills = state.get("skills") or ""
        skills_section = (
            f"Candidate Skills to Emphasize:\n{skills.strip()}"
            if skills.strip()
            else ""
        )

        history = state.get("chat_history") or []
        history_section = format_chat_history(history)

        current_message = state.get("current_message", "").strip()

        user_prompt = CAREER_MENTOR_USER_PROMPT.format(
            candidate_name=candidate_name,
            target_role=target_role,
            career_goal=career_goal,
            resume_section=resume_section,
            skills_section=skills_section,
            history_section=history_section,
            current_message=current_message,
        )

        result: CareerMentorOutput = await llm_service.generate_structured(
            schema=CareerMentorOutput,
            prompt=user_prompt,
            system_instruction=CAREER_MENTOR_SYSTEM_PROMPT,
        )

        # Light cleanup of reply
        clean_reply = result.reply.strip()
        # Clean multi-spaces
        clean_reply = re.sub(r'[ \t]{2,}', ' ', clean_reply)

        clean_follow_ups = [
            re.sub(r'[ \t]{2,}', ' ', fu).strip()
            for fu in (result.suggested_follow_ups or [])
            if fu and fu.strip()
        ]

        return {
            "reply": clean_reply,
            "suggested_follow_ups": clean_follow_ups,
            "is_valid": True,
        }

    return chat_node
