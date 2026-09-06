from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from app.models.analysis import AnalysisSection, Recommendation


class AnalysisResultResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        serialize_by_alias=True,
    )

    overall_score: int = Field(
        ..., ge=0, le=100, description="Overall resume score between 0 and 100"
    )
    ats_score: int = Field(
        ..., ge=0, le=100, description="ATS compatibility score between 0 and 100"
    )
    job_match_score: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
        description="Job match score between 0 and 100, or null if no job description was provided"
    )
    summary: str = Field(
        ..., description="Comprehensive summary of candidate profile and evaluation"
    )
    sections: List[AnalysisSection] = Field(
        default_factory=list,
        description="Detailed section evaluations (skills, keywords, experience, education, projects, content, formatting)"
    )
    strengths: List[str] = Field(
        default_factory=list,
        description="Evidence-based strengths found in the resume"
    )
    weaknesses: List[str] = Field(
        default_factory=list,
        description="Identified weaknesses or areas for improvement"
    )
    missing_skills: List[str] = Field(
        default_factory=list,
        description="Skills relevant to the target role/JD that are missing or lacking evidence"
    )
    missing_keywords: List[str] = Field(
        default_factory=list,
        description="Keywords recommended for searchability and ATS parsing"
    )
    recommendations: List[Recommendation] = Field(
        default_factory=list,
        description="Prioritized list of actionable recommendations"
    )
    improvements: List[str] = Field(
        default_factory=list,
        description="Concrete improvement action items"
    )


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Standardized machine-readable error code")
    message: str = Field(..., description="Human-readable description of the error")


class ErrorResponse(BaseModel):
    error: ErrorDetail


class HealthResponse(BaseModel):
    status: str = Field(default="healthy", description="Service health status indicator")


class CoverLetterGenerateResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        serialize_by_alias=True,
    )

    content: str = Field(..., description="The complete, formatted cover letter")
    key_highlights: List[str] = Field(
        default_factory=list,
        description="Key qualifications, metrics, or points highlighted in the letter"
    )
    target_role: str = Field(..., description="Target job title or role")
    company_name: str = Field(..., description="Target company name")
    tone: str = Field(..., description="Tone used in generation")

