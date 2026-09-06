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


class CoverLetterGenerateRequest(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
    )

    candidate_name: Optional[str] = Field(
        default=None,
        max_length=120,
        description="Candidate's full name",
        validation_alias=AliasChoices("candidate_name", "candidateName"),
    )
    candidate_email: Optional[str] = Field(
        default=None,
        max_length=120,
        description="Candidate's email address",
        validation_alias=AliasChoices("candidate_email", "candidateEmail"),
    )
    target_role: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Target job title or role (e.g. Senior Backend Engineer)",
        validation_alias=AliasChoices("target_role", "targetRole"),
    )
    company_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the company being applied to (e.g. Stripe)",
        validation_alias=AliasChoices("company_name", "companyName"),
    )
    job_description: Optional[str] = Field(
        default=None,
        max_length=30000,
        description="Job description or posting requirements",
        validation_alias=AliasChoices("job_description", "jobDescription"),
    )
    resume_text: Optional[str] = Field(
        default=None,
        max_length=50000,
        description="Extracted plain text from the candidate's resume",
        validation_alias=AliasChoices("resume_text", "resumeText"),
    )
    skills: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Specific skills or technologies to emphasize",
        validation_alias=AliasChoices("skills", "skillsToEmphasize"),
    )
    additional_info: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Optional personal notes, achievements, or context",
        validation_alias=AliasChoices("additional_info", "additionalInfo"),
    )
    tone: str = Field(
        default="Professional",
        max_length=40,
        description="Writing tone: Professional, Confident, Friendly, Concise, or Enthusiastic",
        validation_alias=AliasChoices("tone", "writingTone"),
    )

