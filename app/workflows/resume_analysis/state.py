from typing import List, Optional, TypedDict
from app.models.analysis import AnalysisSection, Recommendation


class ResumeAnalysisState(TypedDict, total=False):
    # Inputs
    resume_text: str
    target_role: str
    experience_level: str
    job_description: Optional[str]

    # Overall & ATS Analysis
    overall_score: Optional[int]
    summary: Optional[str]
    ats_score: Optional[int]

    # Job Match (nullable if no JD provided)
    job_match_score: Optional[int]

    # Section-by-Section Analysis
    sections: Optional[List[AnalysisSection]]

    # Strengths and Weaknesses
    strengths: Optional[List[str]]
    weaknesses: Optional[List[str]]

    # Missing Skills and Keywords
    missing_skills: Optional[List[str]]
    missing_keywords: Optional[List[str]]

    # Recommendations and Action Items
    recommendations: Optional[List[Recommendation]]
    improvements: Optional[List[str]]

    # Workflow metadata / errors
    errors: Optional[List[str]]
    is_valid: Optional[bool]
