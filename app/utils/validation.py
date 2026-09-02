from typing import List, Optional
from app.models.analysis import AnalysisSection, Recommendation, RecommendationPriority
from app.exceptions.ai_exceptions import AIResponseValidationException

REQUIRED_SECTION_KEYS = {
    "skills",
    "keywords",
    "experience",
    "education",
    "projects",
    "content",
    "formatting",
}


def validate_score(score: Optional[int], field_name: str, allow_none: bool = False) -> Optional[int]:
    """Validates that a score is an integer between 0 and 100, or None if permitted."""
    if score is None:
        if allow_none:
            return None
        raise AIResponseValidationException(f"Score field '{field_name}' cannot be null.")
    if not isinstance(score, int) or score < 0 or score > 100:
        raise AIResponseValidationException(
            f"Score field '{field_name}' must be an integer between 0 and 100, got: {score}"
        )
    return score


def validate_sections(sections: List[AnalysisSection]) -> List[AnalysisSection]:
    """Ensures sections contain valid scores and expected keys."""
    if not sections:
        raise AIResponseValidationException("Sections analysis returned an empty list.")

    seen_keys = set()
    validated = []
    for section in sections:
        validate_score(section.score, f"section[{section.key}].score")
        if not section.summary or not section.summary.strip():
            raise AIResponseValidationException(f"Section '{section.key}' must have a summary.")
        seen_keys.add(section.key.lower())
        validated.append(section)

    return validated


def validate_recommendations(recs: List[Recommendation]) -> List[Recommendation]:
    """Validates that recommendations have titles, details, and valid priorities."""
    if not recs:
        return []

    validated = []
    for r in recs:
        if not r.title or not r.title.strip():
            continue
        priority = r.priority
        if isinstance(priority, str):
            try:
                priority = RecommendationPriority(priority.lower())
            except ValueError:
                priority = RecommendationPriority.MEDIUM
        validated.append(
            Recommendation(
                title=r.title.strip(),
                detail=r.detail.strip() if r.detail else "",
                priority=priority,
            )
        )
    return validated


def sanitize_string_list(items: List[str]) -> List[str]:
    """Removes empty strings and deduplicates while preserving order."""
    seen = set()
    result = []
    for item in items:
        if item and isinstance(item, str):
            cleaned = item.strip()
            if cleaned and cleaned.lower() not in seen:
                seen.add(cleaned.lower())
                result.append(cleaned)
    return result
