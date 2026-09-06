from typing import List, Optional, TypedDict


class CareerMentorState(TypedDict, total=False):
    current_message: str
    target_role: Optional[str]
    career_goal: Optional[str]
    resume_text: Optional[str]
    skills: Optional[str]
    candidate_name: Optional[str]
    chat_history: Optional[List[dict]]
    reply: Optional[str]
    suggested_follow_ups: Optional[List[str]]
    is_valid: Optional[bool]
