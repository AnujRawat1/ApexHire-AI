import pytest
from unittest.mock import AsyncMock
from pydantic import ValidationError

from app.models.career_mentor import (
    ChatMessage,
    CareerMentorChatRequest,
    CareerMentorChatResponse,
    CareerMentorOutput,
)
from app.services.career_mentor_service import CareerMentorService
from app.workflows.career_mentor.nodes.chat_node import (
    create_career_mentor_chat_node,
    format_chat_history,
)
from app.workflows.career_mentor.state import CareerMentorState


def test_career_mentor_request_valid():
    req = CareerMentorChatRequest(
        message="How do I transition from Senior to Staff Backend Engineer?",
        target_role="Staff Backend Engineer",
        career_goal="Lead technical architecture and distributed systems at scale",
        candidate_name="Alex Mercer",
        chat_history=[
            ChatMessage(role="user", content="Hello!"),
            ChatMessage(role="assistant", content="Hi Alex! How can I help with your career?"),
        ],
    )
    assert req.message == "How do I transition from Senior to Staff Backend Engineer?"
    assert req.target_role == "Staff Backend Engineer"
    assert req.career_goal == "Lead technical architecture and distributed systems at scale"
    assert len(req.chat_history) == 2


def test_career_mentor_request_camel_case():
    req = CareerMentorChatRequest(
        currentMessage="What skills should I learn for Kubernetes?",
        targetRole="DevOps Engineer",
        careerGoal="Pass CKA exam and manage clusters",
        resumeText="5 years Linux administration experience",
        candidateName="Sam",
        chatHistory=[
            {"role": "user", "content": "I want to learn Kubernetes."},
        ],
    )
    assert req.message == "What skills should I learn for Kubernetes?"
    assert req.target_role == "DevOps Engineer"
    assert req.candidate_name == "Sam"
    assert len(req.chat_history) == 1
    assert req.chat_history[0].role == "user"


def test_career_mentor_request_missing_message():
    with pytest.raises(ValidationError):
        CareerMentorChatRequest(target_role="Software Engineer")


def test_format_chat_history():
    empty = format_chat_history([])
    assert "New conversation session" in empty

    history = [
        {"role": "user", "content": "Tell me about system design."},
        {"role": "assistant", "content": "Start with horizontal scaling."},
    ]
    formatted = format_chat_history(history)
    assert "User: Tell me about system design." in formatted
    assert "Mentor: Start with horizontal scaling." in formatted


@pytest.mark.asyncio
async def test_career_mentor_chat_node():
    mock_llm_service = AsyncMock()
    mock_llm_service.generate_structured.return_value = CareerMentorOutput(
        reply="Focus on high-availability design and distributed consensus.",
        suggested_follow_ups=[
            "What distributed consensus algorithms should I know?",
            "How do I explain Raft vs Paxos?",
        ],
    )

    node = create_career_mentor_chat_node(mock_llm_service)
    state: CareerMentorState = {
        "current_message": "Tell me about distributed consensus.",
        "target_role": "Staff Backend Engineer",
        "candidate_name": "Jordan",
    }

    result = await node(state)
    assert "high-availability" in result["reply"]
    assert len(result["suggested_follow_ups"]) == 2
    assert result["is_valid"] is True


@pytest.mark.asyncio
async def test_career_mentor_service_mocked():
    mock_llm_service = AsyncMock()
    mock_llm_service.generate_structured.return_value = CareerMentorOutput(
        reply="Practice the STAR method for behavioral questions at Stripe.",
        suggested_follow_ups=["Give me an example of an ambiguous technical challenge."],
    )

    service = CareerMentorService(llm_service=mock_llm_service)
    req = CareerMentorChatRequest(
        message="How should I prep for behavioral interviews?",
        target_role="Software Engineer",
    )

    res = await service.chat(req)
    assert isinstance(res, CareerMentorChatResponse)
    assert "STAR method" in res.reply
    assert len(res.suggested_follow_ups) == 1
    assert res.target_role == "Software Engineer"
