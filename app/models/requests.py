from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, AliasChoices, field_validator


class ResumeAnalysisRequest(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
    )

    resume_text: str = Field(
        ...,
        min_length=30,
        description="Raw text content of candidate resume (minimum 30 characters)",
        validation_alias=AliasChoices("resume_text", "resumeText"),
    )
    target_role: str = Field(
        ...,
        min_length=2,
        max_length=80,
        description="Target job title or role (e.g. Backend Engineer, Fullstack Developer)",
        validation_alias=AliasChoices("target_role", "targetRole"),
    )
    experience_level: str = Field(
        ...,
        min_length=2,
        max_length=60,
        description="Experience level (e.g. Entry Level, Mid-Level, Senior 5+ years)",
        validation_alias=AliasChoices("experience_level", "experienceLevel"),
    )
    job_description: Optional[str] = Field(
        default=None,
        max_length=20000,
        description="Optional job description text to perform targeted match scoring",
        validation_alias=AliasChoices("job_description", "jobDescription"),
    )

    @field_validator("resume_text")
    @classmethod
    def validate_resume_content(cls, v: str) -> str:
        if not v or len(v.strip()) < 30:
            raise ValueError("resume_text must contain at least 30 non-whitespace characters.")
        return v.strip()

    @field_validator("target_role")
    @classmethod
    def validate_target_role(cls, v: str) -> str:
        if not v or len(v.strip()) < 2:
            raise ValueError("target_role must be at least 2 characters long.")
        return v.strip()

    @field_validator("experience_level")
    @classmethod
    def validate_experience_level(cls, v: str) -> str:
        if not v or len(v.strip()) < 2:
            raise ValueError("experience_level must be at least 2 characters long.")
        return v.strip()

    @field_validator("job_description")
    @classmethod
    def validate_job_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            return stripped if len(stripped) > 0 else None
        return None
