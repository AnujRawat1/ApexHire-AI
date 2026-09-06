import re
import logging
from typing import Callable, Coroutine, Any

from app.models.cover_letter import CoverLetterOutput
from app.prompts.cover_letter import (
    COVER_LETTER_SYSTEM_PROMPT,
    COVER_LETTER_USER_PROMPT,
)
from app.services.llm_service import LLMService
from app.workflows.cover_letter.state import CoverLetterState

logger = logging.getLogger(__name__)


def sanitize_extracted_text(text: str) -> str:
    """Repairs common PDF extraction and OCR artifacts in raw resume text."""
    if not text:
        return text

    # Fix broken slashes with units or percentage: e.g. "50 /ms" -> "50ms", "100 /%" -> "100%", "10 /MB" -> "10MB"
    cleaned = re.sub(r'(\d+)\s*/\s*([a-zA-Z%]+)', r'\1\2', text)
    # Fix broken slash numbers: e.g. "Spring Security /6" -> "Spring Security 6"
    cleaned = re.sub(r'/\s*(\d+)', r' \1', cleaned)
    # Collapse double or triple spaces between letters: e.g. "high  performance" -> "high performance"
    cleaned = re.sub(r'([a-zA-Z0-9]) {2,}([a-zA-Z0-9])', r'\1 \2', cleaned)
    return cleaned


def clean_cover_letter_output(content: str) -> str:
    """Cleans up formatting artifacts and repairs typography in generated cover letter output."""
    if not content:
        return content

    # 1. Run OCR/PDF extraction text sanitization on output
    cleaned = sanitize_extracted_text(content)

    # 2. Fix double or triple spaces within lines
    cleaned = re.sub(r'[ \t]{2,}', ' ', cleaned)

    # 3. Clean up backticks
    cleaned = re.sub(r'`(.*?)`', r'\1', cleaned)

    # 4. Standardize bullet symbols to unicode bullet '•'
    cleaned = re.sub(r'^[*\-]\s+', '• ', cleaned, flags=re.MULTILINE)

    return cleaned.strip()


def create_cover_letter_generation_node(
    llm_service: LLMService,
) -> Callable[[CoverLetterState], Coroutine[Any, Any, dict]]:
    """Factory creating the Cover Letter generation node."""

    async def generation_node(state: CoverLetterState) -> dict:
        logger.info(
            f"Executing Cover Letter Generation Node: role='{state.get('target_role')}', "
            f"company='{state.get('company_name')}', tone='{state.get('tone')}'"
        )

        candidate_name = (state.get("candidate_name") or "").strip() or "Candidate"
        candidate_email = (state.get("candidate_email") or "").strip() or "Not provided"

        jd = state.get("job_description")
        job_description_section = (
            f"Target Job Description:\n\"\"\"\n{jd.strip()}\n\"\"\""
            if jd and jd.strip()
            else "Target Job Description: Not provided. Focus on industry-standard expectations for this role."
        )

        skills = state.get("skills")
        skills_section = (
            f"Skills to Emphasize:\n{skills.strip()}"
            if skills and skills.strip()
            else ""
        )

        additional_info = state.get("additional_info")
        additional_info_section = (
            f"Additional Context / Highlights to Include:\n{additional_info.strip()}"
            if additional_info and additional_info.strip()
            else ""
        )

        raw_resume = state.get("resume_text") or ""
        sanitized_resume = sanitize_extracted_text(raw_resume)
        resume_section = (
            f"Candidate Resume Context:\n\"\"\"\n{sanitized_resume.strip()}\n\"\"\""
            if sanitized_resume.strip()
            else "Candidate Resume Context: None provided. Use candidate details and role context."
        )

        user_prompt = COVER_LETTER_USER_PROMPT.format(
            target_role=state["target_role"].strip(),
            company_name=state["company_name"].strip(),
            tone=(state.get("tone") or "Professional").strip(),
            candidate_name=candidate_name,
            candidate_email=candidate_email,
            job_description_section=job_description_section,
            skills_section=skills_section,
            additional_info_section=additional_info_section,
            resume_section=resume_section,
        )

        result: CoverLetterOutput = await llm_service.generate_structured(
            schema=CoverLetterOutput,
            prompt=user_prompt,
            system_instruction=COVER_LETTER_SYSTEM_PROMPT,
        )

        cleaned_content = clean_cover_letter_output(result.content)
        cleaned_highlights = [clean_cover_letter_output(h) for h in (result.key_highlights or [])]

        return {
            "content": cleaned_content,
            "key_highlights": cleaned_highlights,
        }

    return generation_node
