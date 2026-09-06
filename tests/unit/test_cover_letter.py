import pytest
from unittest.mock import AsyncMock
from pydantic import ValidationError

from app.models.cover_letter import CoverLetterOutput
from app.models.requests import CoverLetterGenerateRequest
from app.models.responses import CoverLetterGenerateResponse
from app.services.cover_letter_service import CoverLetterService
from app.workflows.cover_letter.nodes.generation import create_cover_letter_generation_node
from app.workflows.cover_letter.nodes.validation import create_cover_letter_validation_node
from app.workflows.cover_letter.state import CoverLetterState
from app.exceptions.ai_exceptions import AIResponseValidationException


def test_cover_letter_request_valid():
    req = CoverLetterGenerateRequest(
        candidate_name="Alex Mercer",
        candidate_email="alex@example.com",
        target_role="Staff Backend Engineer",
        company_name="Stripe",
        job_description="Seeking a distributed systems engineer...",
        skills="Go, Kubernetes, Kafka, Distributed Systems",
        additional_info="10 years experience scaling transaction engines",
        tone="Confident",
    )
    assert req.target_role == "Staff Backend Engineer"
    assert req.company_name == "Stripe"
    assert req.tone == "Confident"
    assert req.candidate_name == "Alex Mercer"


def test_cover_letter_request_camel_case():
    req = CoverLetterGenerateRequest(
        candidateName="Jordan Lee",
        candidateEmail="jordan@example.com",
        targetRole="Frontend Engineer",
        companyName="Linear",
        skillsToEmphasize="React, Tailwind, TypeScript",
        additionalInfo="Passionate about slick UI animations",
        writingTone="Enthusiastic",
    )
    assert req.candidate_name == "Jordan Lee"
    assert req.target_role == "Frontend Engineer"
    assert req.company_name == "Linear"
    assert req.tone == "Enthusiastic"


def test_cover_letter_request_missing_required():
    with pytest.raises(ValidationError):
        CoverLetterGenerateRequest(
            company_name="Acme Corp"
        )


@pytest.mark.asyncio
async def test_cover_letter_generation_node():
    mock_llm_service = AsyncMock()
    mock_llm_service.generate_structured.return_value = CoverLetterOutput(
        content="Dear Hiring Team at Stripe,\n\nI am writing to express strong interest...",
        key_highlights=["Distributed systems expertise", "High-throughput API design"],
    )

    node = create_cover_letter_generation_node(mock_llm_service)
    state: CoverLetterState = {
        "candidate_name": "Jordan",
        "target_role": "Backend Engineer",
        "company_name": "Stripe",
        "tone": "Confident",
    }

    result = await node(state)
    assert "Dear Hiring Team at Stripe" in result["content"]
    assert len(result["key_highlights"]) == 2


@pytest.mark.asyncio
async def test_cover_letter_validation_node_valid():
    node = create_cover_letter_validation_node()
    state: CoverLetterState = {
        "content": "Dear Hiring Team,\n\nThis is a sufficiently long cover letter exceeding 50 characters to pass validation checks cleanly.",
    }
    result = await node(state)
    assert result["is_valid"] is True


@pytest.mark.asyncio
async def test_cover_letter_validation_node_too_short():
    node = create_cover_letter_validation_node()
    state: CoverLetterState = {
        "content": "Too short.",
    }
    with pytest.raises(AIResponseValidationException):
        await node(state)


@pytest.mark.asyncio
async def test_cover_letter_service_mocked():
    mock_llm_service = AsyncMock()
    mock_llm_service.generate_structured.return_value = CoverLetterOutput(
        content="Dear Hiring Team at Acme,\n\nI am thrilled to apply for the Backend Engineer role with 5+ years of experience.",
        key_highlights=["5+ years Python experience", "High throughput microservices"],
    )

    service = CoverLetterService(llm_service=mock_llm_service)
    req = CoverLetterGenerateRequest(
        target_role="Backend Engineer",
        company_name="Acme",
        tone="Professional",
    )
    res = await service.generate_cover_letter(req)

    assert isinstance(res, CoverLetterGenerateResponse)
    assert "Dear Hiring Team at Acme" in res.content
    assert len(res.key_highlights) == 2
    assert res.target_role == "Backend Engineer"
    assert res.company_name == "Acme"
