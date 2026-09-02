from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class RecommendationPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Recommendation(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str = Field(..., description="Actionable title for recommendation")
    detail: str = Field(..., description="Specific detail and concrete action guidance")
    priority: RecommendationPriority = Field(
        default=RecommendationPriority.MEDIUM,
        description="Priority level: high, medium, or low"
    )


class AnalysisSection(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    key: str = Field(
        ...,
        description="Section key (skills, keywords, experience, education, projects, content, formatting)"
    )
    title: str = Field(..., description="Human-readable title of the section")
    score: int = Field(..., ge=0, le=100, description="Score between 0 and 100")
    summary: str = Field(..., description="Concise assessment summary of the section")
    points: List[str] = Field(
        default_factory=list,
        description="Key observations and evaluation points"
    )


# --- Structured LLM Schemas ---

class OverallAnalysisOutput(BaseModel):
    overall_score: int = Field(
        ..., ge=0, le=100, description="Overall score between 0 and 100 based on resume quality and role fit"
    )
    summary: str = Field(
        ..., description="Comprehensive summary of the candidate's profile, role fit, and experience alignment"
    )


class ATSAnalysisOutput(BaseModel):
    ats_score: int = Field(
        ..., ge=0, le=100, description="ATS machine-readability and compatibility score between 0 and 100"
    )


class JobMatchOutput(BaseModel):
    job_match_score: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
        description="Job match score between 0 and 100 against the provided job description, or null if no JD provided"
    )


class SectionsAnalysisOutput(BaseModel):
    sections: List[AnalysisSection] = Field(
        ...,
        description="List of detailed section evaluations (skills, keywords, experience, education, projects, content, formatting)"
    )


class StrengthsWeaknessesOutput(BaseModel):
    strengths: List[str] = Field(
        ..., description="Concrete, evidence-backed strengths found in the resume"
    )
    weaknesses: List[str] = Field(
        ..., description="Concrete, evidence-backed weaknesses or gaps found in the resume"
    )


class MissingElementsOutput(BaseModel):
    missing_skills: List[str] = Field(
        ..., description="Skills relevant to the target role/JD that are missing or insufficiently demonstrated"
    )
    missing_keywords: List[str] = Field(
        ..., description="Keywords/industry terminology that would enhance search and ATS match"
    )


class RecommendationsOutput(BaseModel):
    recommendations: List[Recommendation] = Field(
        ..., description="Actionable recommendations prioritized as high, medium, or low"
    )


class ImprovementsOutput(BaseModel):
    improvements: List[str] = Field(
        ..., description="Specific, concrete improvement actions (e.g. rewrite bullets with metrics, strengthen summary)"
    )


class FullResumeAnalysisOutput(BaseModel):
    """Unified high-performance schema for complete resume evaluation."""
    overall_score: int = Field(..., ge=0, le=100, description="Overall score between 0 and 100")
    ats_score: int = Field(..., ge=0, le=100, description="ATS compatibility score between 0 and 100")
    job_match_score: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
        description="Job match score between 0 and 100 against JD, or null if no JD"
    )
    summary: str = Field(..., description="Comprehensive profile summary and role alignment assessment")
    sections: List[AnalysisSection] = Field(
        ...,
        description="List of 7 section evaluations: skills, keywords, experience, education, projects, content, formatting"
    )
    strengths: List[str] = Field(..., description="Evidence-backed candidate strengths")
    weaknesses: List[str] = Field(..., description="Identified gaps or candidate weaknesses")
    missing_skills: List[str] = Field(..., description="Critical missing skills for target role/JD")
    missing_keywords: List[str] = Field(..., description="Missing industry keywords")
    recommendations: List[Recommendation] = Field(..., description="Prioritized recommendations (high/medium/low)")
    improvements: List[str] = Field(..., description="Specific actionable improvements")
