from typing import List, Optional, TypedDict


class CoverLetterState(TypedDict, total=False):
    # Inputs
    candidate_name: Optional[str]
    candidate_email: Optional[str]
    target_role: str
    company_name: str
    job_description: Optional[str]
    resume_text: Optional[str]
    skills: Optional[str]
    additional_info: Optional[str]
    tone: str

    # Outputs
    content: Optional[str]
    key_highlights: Optional[List[str]]

    # Workflow metadata / validation
    is_valid: Optional[bool]
    errors: Optional[List[str]]
