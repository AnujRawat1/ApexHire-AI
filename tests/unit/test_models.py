import json
from app.models.analysis import AnalysisSection, Recommendation, RecommendationPriority
from app.models.responses import AnalysisResultResponse, ErrorResponse, HealthResponse


def test_analysis_result_response_serialization():
    section = AnalysisSection(
        key="skills",
        title="Technical Skills",
        score=90,
        summary="Excellent technical skills",
        points=["Point 1", "Point 2"],
    )
    rec = Recommendation(
        title="Improve Project Scope",
        detail="Add architecture details",
        priority=RecommendationPriority.HIGH,
    )
    res = AnalysisResultResponse(
        overall_score=85,
        ats_score=80,
        job_match_score=92,
        summary="Candidate is well-qualified.",
        sections=[section],
        strengths=["Strong Java expertise"],
        weaknesses=["Limited cloud metrics"],
        missing_skills=["Kubernetes"],
        missing_keywords=["CI/CD"],
        recommendations=[rec],
        improvements=["Rewrite project bullets with metrics"],
    )

    data = res.model_dump(by_alias=True)
    # Check camelCase keys required by Spring Boot Jackson
    assert "overallScore" in data
    assert "atsScore" in data
    assert "jobMatchScore" in data
    assert "missingSkills" in data
    assert "missingKeywords" in data
    assert data["overallScore"] == 85
    assert data["jobMatchScore"] == 92
    assert data["sections"][0]["key"] == "skills"
    assert data["recommendations"][0]["priority"] == "high"


def test_analysis_result_response_null_job_match():
    res = AnalysisResultResponse(
        overall_score=75,
        ats_score=70,
        job_match_score=None,
        summary="No JD supplied.",
        sections=[],
        strengths=[],
        weaknesses=[],
        missing_skills=[],
        missing_keywords=[],
        recommendations=[],
        improvements=[],
    )
    data = res.model_dump(by_alias=True)
    assert data["jobMatchScore"] is None


def test_error_response_model():
    err = ErrorResponse.model_validate({
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Invalid resume input",
        }
    })
    assert err.error.code == "VALIDATION_ERROR"
    assert err.error.message == "Invalid resume input"


def test_health_response_model():
    health = HealthResponse()
    assert health.status == "healthy"
