import pytest
from unittest.mock import AsyncMock

from app.exceptions.ai_exceptions import AIResponseValidationException
from app.models.analysis import (
    OverallAnalysisOutput,
    ATSAnalysisOutput,
    JobMatchOutput,
    SectionsAnalysisOutput,
    AnalysisSection,
    StrengthsWeaknessesOutput,
    MissingElementsOutput,
    RecommendationsOutput,
    Recommendation,
    RecommendationPriority,
    ImprovementsOutput,
)
from app.workflows.resume_analysis.nodes.overall import create_overall_node
from app.workflows.resume_analysis.nodes.ats import create_ats_node
from app.workflows.resume_analysis.nodes.job_match import create_job_match_node
from app.workflows.resume_analysis.nodes.sections import create_sections_node
from app.workflows.resume_analysis.nodes.strengths import create_strengths_node
from app.workflows.resume_analysis.nodes.missing import create_missing_node
from app.workflows.resume_analysis.nodes.recommendations import create_recommendations_node
from app.workflows.resume_analysis.nodes.improvements import create_improvements_node
from app.workflows.resume_analysis.nodes.validation import create_validation_node
from app.workflows.resume_analysis.state import ResumeAnalysisState


@pytest.mark.asyncio
async def test_overall_node():
    mock_llm = AsyncMock()
    mock_llm.generate_structured.return_value = OverallAnalysisOutput(
        overall_score=85, summary="Strong profile."
    )
    node = create_overall_node(mock_llm)
    state: ResumeAnalysisState = {
        "resume_text": "Sample text",
        "target_role": "Backend Engineer",
        "experience_level": "Senior",
    }
    result = await node(state)
    assert result["overall_score"] == 85
    assert result["summary"] == "Strong profile."


@pytest.mark.asyncio
async def test_ats_node():
    mock_llm = AsyncMock()
    mock_llm.generate_structured.return_value = ATSAnalysisOutput(ats_score=78)
    node = create_ats_node(mock_llm)
    state: ResumeAnalysisState = {
        "resume_text": "Sample text",
        "target_role": "Backend Engineer",
        "experience_level": "Senior",
    }
    result = await node(state)
    assert result["ats_score"] == 78


@pytest.mark.asyncio
async def test_job_match_node_without_jd():
    mock_llm = AsyncMock()
    node = create_job_match_node(mock_llm)
    state: ResumeAnalysisState = {
        "resume_text": "Sample text",
        "target_role": "Backend Engineer",
        "experience_level": "Senior",
        "job_description": None,
    }
    result = await node(state)
    assert result["job_match_score"] is None
    mock_llm.generate_structured.assert_not_called()


@pytest.mark.asyncio
async def test_job_match_node_with_jd():
    mock_llm = AsyncMock()
    mock_llm.generate_structured.return_value = JobMatchOutput(job_match_score=92)
    node = create_job_match_node(mock_llm)
    state: ResumeAnalysisState = {
        "resume_text": "Sample text",
        "target_role": "Backend Engineer",
        "experience_level": "Senior",
        "job_description": "We need Java and Spring Boot experience.",
    }
    result = await node(state)
    assert result["job_match_score"] == 92


@pytest.mark.asyncio
async def test_sections_node():
    mock_llm = AsyncMock()
    mock_llm.generate_structured.return_value = SectionsAnalysisOutput(
        sections=[
            AnalysisSection(
                key="skills",
                title="Skills",
                score=85,
                summary="Solid skills.",
                points=["Java", "Kafka"],
            )
        ]
    )
    node = create_sections_node(mock_llm)
    state: ResumeAnalysisState = {
        "resume_text": "Sample text",
        "target_role": "Backend Engineer",
        "experience_level": "Senior",
    }
    result = await node(state)
    assert len(result["sections"]) == 1
    assert result["sections"][0].key == "skills"


@pytest.mark.asyncio
async def test_strengths_node():
    mock_llm = AsyncMock()
    mock_llm.generate_structured.return_value = StrengthsWeaknessesOutput(
        strengths=["Strong Java and Spring Boot"],
        weaknesses=["No Kubernetes metrics"],
    )
    node = create_strengths_node(mock_llm)
    state: ResumeAnalysisState = {
        "resume_text": "Sample text",
        "target_role": "Backend Engineer",
        "experience_level": "Senior",
    }
    result = await node(state)
    assert result["strengths"] == ["Strong Java and Spring Boot"]
    assert result["weaknesses"] == ["No Kubernetes metrics"]


@pytest.mark.asyncio
async def test_missing_node():
    mock_llm = AsyncMock()
    mock_llm.generate_structured.return_value = MissingElementsOutput(
        missing_skills=["Docker", "AWS ECS"],
        missing_keywords=["Microservices", "REST"],
    )
    node = create_missing_node(mock_llm)
    state: ResumeAnalysisState = {
        "resume_text": "Sample text",
        "target_role": "Backend Engineer",
        "experience_level": "Senior",
    }
    result = await node(state)
    assert "Docker" in result["missing_skills"]
    assert "Microservices" in result["missing_keywords"]


@pytest.mark.asyncio
async def test_recommendations_node():
    mock_llm = AsyncMock()
    mock_llm.generate_structured.return_value = RecommendationsOutput(
        recommendations=[
            Recommendation(
                title="Quantify metrics",
                detail="Add performance metrics to experience",
                priority=RecommendationPriority.HIGH,
            )
        ]
    )
    node = create_recommendations_node(mock_llm)
    state: ResumeAnalysisState = {
        "resume_text": "Sample text",
        "target_role": "Backend Engineer",
        "experience_level": "Senior",
    }
    result = await node(state)
    assert len(result["recommendations"]) == 1
    assert result["recommendations"][0].priority == RecommendationPriority.HIGH


@pytest.mark.asyncio
async def test_improvements_node():
    mock_llm = AsyncMock()
    mock_llm.generate_structured.return_value = ImprovementsOutput(
        improvements=["Rewrite project bullets with metrics", "Add cloud architecture details"]
    )
    node = create_improvements_node(mock_llm)
    state: ResumeAnalysisState = {
        "resume_text": "Sample text",
        "target_role": "Backend Engineer",
        "experience_level": "Senior",
    }
    result = await node(state)
    assert len(result["improvements"]) == 2


@pytest.mark.asyncio
async def test_validation_node_valid():
    node = create_validation_node()
    state: ResumeAnalysisState = {
        "overall_score": 85,
        "ats_score": 80,
        "job_match_score": None,
        "summary": "Valid summary.",
        "sections": [
            AnalysisSection(
                key="skills",
                title="Skills",
                score=85,
                summary="Good skills.",
                points=["Java"],
            )
        ],
        "strengths": ["Strong Java"],
        "weaknesses": ["No cloud metrics"],
        "missing_skills": ["AWS"],
        "missing_keywords": ["CI/CD"],
        "recommendations": [
            Recommendation(
                title="Add metrics",
                detail="Quantify impact",
                priority=RecommendationPriority.HIGH,
            )
        ],
        "improvements": ["Rewrite bullets"],
        "job_description": None,
    }
    result = await node(state)
    assert result["is_valid"] is True
    assert result["overall_score"] == 85
    assert result["job_match_score"] is None


@pytest.mark.asyncio
async def test_validation_node_missing_summary():
    node = create_validation_node()
    state: ResumeAnalysisState = {
        "overall_score": 85,
        "ats_score": 80,
        "job_match_score": None,
        "summary": "   ",
        "sections": [
            AnalysisSection(
                key="skills",
                title="Skills",
                score=85,
                summary="Good skills.",
                points=["Java"],
            )
        ],
    }
    with pytest.raises(AIResponseValidationException):
        await node(state)
