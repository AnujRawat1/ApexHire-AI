import logging
from typing import Callable, Coroutine, Any

from app.exceptions.ai_exceptions import AIResponseValidationException
from app.workflows.cover_letter.state import CoverLetterState

logger = logging.getLogger(__name__)


def create_cover_letter_validation_node() -> Callable[[CoverLetterState], Coroutine[Any, Any, dict]]:
    """Factory creating the validation node for generated cover letters."""

    async def validation_node(state: CoverLetterState) -> dict:
        content = state.get("content")
        errors = []

        if not content or not content.strip():
            errors.append("Generated cover letter content is empty.")
        elif len(content.strip()) < 50:
            errors.append("Generated cover letter is suspiciously short (< 50 chars).")

        if errors:
            err_msg = "; ".join(errors)
            logger.error(f"Cover letter validation failed: {err_msg}")
            raise AIResponseValidationException(f"Cover letter validation failure: {err_msg}")

        logger.info("Cover letter output passed all validation checks")
        return {"is_valid": True, "errors": []}

    return validation_node
