import pytest
from pydantic import ValidationError

from app.exceptions.ai_exceptions import AIResponseValidationException
from app.models.analysis import AnalysisSection, Recommendation, RecommendationPriority
from app.models.requests import ResumeAnalysisRequest
from app.utils.validation import (
    validate_score,
    validate_sections,
    validate_recommendations,
    sanitize_string_list,
)


def test_resume_request_validation_valid():
    req = ResumeAnalysisRequest(
        resume_text="A" * 50,
        target_role="Backend Engineer",
        experience_level="Senior (5+ years)",
        job_description="Job description details here.",
    )
    assert req.target_role == "Backend Engineer"
    assert req.job_description == "Job description details here."


def test_resume_request_validation_camel_case():
    req = ResumeAnalysisRequest(
        resumeText="A" * 50,
        targetRole="Frontend Engineer",
        experienceLevel="Mid-Level",
        jobDescription="Optional description",
    )
    assert req.resume_text == "A" * 50
    assert req.target_role == "Frontend Engineer"
    assert req.experience_level == "Mid-Level"


def test_resume_request_too_short_resume():
    with pytest.raises(ValidationError):
        ResumeAnalysisRequest(
            resume_text="Short resume",
            target_role="Backend Engineer",
            experience_level="Senior",
        )


def test_resume_request_empty_role():
    with pytest.raises(ValidationError):
        ResumeAnalysisRequest(
            resume_text="A" * 50,
            target_role=" ",
            experience_level="Senior",
        )


def test_validate_score_valid():
    assert validate_score(85, "test_score") == 85
    assert validate_score(0, "test_score") == 0
    assert validate_score(100, "test_score") == 100


def test_validate_score_allow_none():
    assert validate_score(None, "test_score", allow_none=True) is None


def test_validate_score_disallow_none():
    with pytest.raises(AIResponseValidationException):
        validate_score(None, "test_score", allow_none=False)


def test_validate_score_out_of_bounds():
    with pytest.raises(AIResponseValidationException):
        validate_score(105, "test_score")
    with pytest.raises(AIResponseValidationException):
        validate_score(-5, "test_score")


def test_validate_sections_valid():
    sections = [
        AnalysisSection(
            key="skills",
            title="Technical Skills",
            score=88,
            summary="Solid skills.",
            points=["Java", "Spring Boot"],
        )
    ]
    validated = validate_sections(sections)
    assert len(validated) == 1
    assert validated[0].score == 88


def test_validate_sections_empty():
    with pytest.raises(AIResponseValidationException):
        validate_sections([])


def test_validate_recommendations():
    recs = [
        Recommendation(title="Quantify metrics", detail="Add numbers", priority=RecommendationPriority.HIGH),
        Recommendation(title="   ", detail="Empty title", priority=RecommendationPriority.LOW),
    ]
    validated = validate_recommendations(recs)
    assert len(validated) == 1
    assert validated[0].title == "Quantify metrics"
    assert validated[0].priority == RecommendationPriority.HIGH


def test_sanitize_string_list():
    raw = ["Java", "  Python  ", "", "java", "Go", "   ", "Python"]
    sanitized = sanitize_string_list(raw)
    assert sanitized == ["Java", "Python", "Go"]
