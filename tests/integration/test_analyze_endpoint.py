import pytest
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.api.routes.resume import get_analysis_service
from app.models.analysis import AnalysisSection, Recommendation, RecommendationPriority
from app.models.responses import AnalysisResultResponse
from app.config.settings import get_settings


@pytest.fixture
def valid_api_key():
    return get_settings().ai_service_api_key


@pytest.fixture
def mock_analysis_response():
    return AnalysisResultResponse(
        overall_score=88,
        ats_score=82,
        job_match_score=90,
        summary="Outstanding backend developer with deep Java and cloud experience.",
        sections=[
            AnalysisSection(
                key="skills",
                title="Technical Skills",
                score=90,
                summary="Solid tech stack.",
                points=["Java 17", "Spring Boot", "Kafka"],
            )
        ],
        strengths=["Strong architectural background", "Solid cloud deployment skills"],
        weaknesses=["Limited frontend exposure"],
        missing_skills=["Kubernetes Helm"],
        missing_keywords=["CI/CD pipeline"],
        recommendations=[
            Recommendation(
                title="Add Kubernetes metrics",
                detail="Quantify deployment scale",
                priority=RecommendationPriority.HIGH,
            )
        ],
        improvements=["Rewrite project bullets using metrics"],
    )


@pytest.mark.asyncio
async def test_analyze_unauthorized_no_token():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/resume/analyze",
            json={
                "resume_text": "A" * 50,
                "target_role": "Backend Engineer",
                "experience_level": "Senior",
            },
        )
        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_analyze_unauthorized_invalid_token():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/resume/analyze",
            headers={"Authorization": "Bearer wrong-api-key"},
            json={
                "resume_text": "A" * 50,
                "target_role": "Backend Engineer",
                "experience_level": "Senior",
            },
        )
        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_analyze_validation_error_short_resume(valid_api_key):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/resume/analyze",
            headers={"Authorization": f"Bearer {valid_api_key}"},
            json={
                "resume_text": "Too short",
                "target_role": "Backend Engineer",
                "experience_level": "Senior",
            },
        )
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_analyze_success_bearer_token(valid_api_key, mock_analysis_response):
    mock_svc = AsyncMock()
    mock_svc.analyze_resume.return_value = mock_analysis_response

    app.dependency_overrides[get_analysis_service] = lambda: mock_svc
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/resume/analyze",
                headers={
                    "Authorization": f"Bearer {valid_api_key}",
                    "X-Request-ID": "test-req-12345",
                },
                json={
                    "resumeText": "Experienced backend engineer with 5 years in Java and Spring Boot." * 2,
                    "targetRole": "Backend Engineer",
                    "experienceLevel": "Senior (5+ years)",
                    "jobDescription": "Looking for Senior Java / Spring Boot expert",
                },
            )
            assert response.status_code == 200
            assert response.headers.get("X-Request-ID") == "test-req-12345"

            data = response.json()
            assert data["overallScore"] == 88
            assert data["atsScore"] == 82
            assert data["jobMatchScore"] == 90
            assert "summary" in data
            assert len(data["sections"]) == 1
            assert len(data["strengths"]) == 2
            assert len(data["recommendations"]) == 1
            assert data["recommendations"][0]["priority"] == "high"
    finally:
        app.dependency_overrides.pop(get_analysis_service, None)


@pytest.mark.asyncio
async def test_analyze_success_x_api_key_header(valid_api_key, mock_analysis_response):
    mock_svc = AsyncMock()
    mock_svc.analyze_resume.return_value = mock_analysis_response

    app.dependency_overrides[get_analysis_service] = lambda: mock_svc
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/resume/analyze",
                headers={"X-API-Key": valid_api_key},
                json={
                    "resume_text": "Experienced backend engineer with 5 years in Java and Spring Boot." * 2,
                    "target_role": "Backend Engineer",
                    "experience_level": "Senior (5+ years)",
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert data["overallScore"] == 88
    finally:
        app.dependency_overrides.pop(get_analysis_service, None)
