from typing import List
from pydantic import BaseModel, Field


class CoverLetterOutput(BaseModel):
    content: str = Field(
        description="The complete, well-structured cover letter text with greeting, narrative body paragraphs, and professional sign-off"
    )
    key_highlights: List[str] = Field(
        default_factory=list,
        description="3-5 bullet points capturing the key qualifications, metrics, or strengths emphasized in the letter"
    )
