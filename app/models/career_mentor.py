from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

from pydantic.alias_generators import to_camel


class ChatMessage(BaseModel):
    """Represents a single message turn in the conversation."""
    model_config = ConfigDict(populate_by_name=True)

    role: Literal["user", "assistant", "system"]
    content: str


class CareerMentorChatRequest(BaseModel):
    """Payload sent to Python service for a Career Mentor response."""
    model_config = ConfigDict(populate_by_name=True)

    message: str = Field(..., alias="currentMessage", description="Current message prompt from the candidate")
    target_role: Optional[str] = Field(default="Software Engineer", alias="targetRole")
    career_goal: Optional[str] = Field(default=None, alias="careerGoal")
    resume_text: Optional[str] = Field(default=None, alias="resumeText")
    skills: Optional[str] = None
    candidate_name: Optional[str] = Field(default=None, alias="candidateName")
    chat_history: List[ChatMessage] = Field(default_factory=list, alias="chatHistory")


class CareerMentorOutput(BaseModel):
    """Structured LLM response for career mentorship."""
    reply: str = Field(..., description="Actionable, articulate, and structured mentor response in clean markdown")
    suggested_follow_ups: List[str] = Field(
        default_factory=list,
        description="2 to 3 concise, highly relevant follow-up questions the user can ask next",
    )


class CareerMentorChatResponse(BaseModel):
    """API response returned to Spring Boot gateway."""
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        serialize_by_alias=True,
    )

    reply: str
    suggested_follow_ups: List[str] = Field(default_factory=list)
    target_role: Optional[str] = None
    career_goal: Optional[str] = None
