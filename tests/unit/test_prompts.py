from app.prompts.resume.overall import OVERALL_USER_PROMPT
from app.prompts.resume.ats import ATS_USER_PROMPT
from app.prompts.resume.job_match import JOB_MATCH_USER_PROMPT
from app.prompts.resume.sections import SECTIONS_USER_PROMPT
from app.prompts.resume.strengths import STRENGTHS_USER_PROMPT
from app.prompts.resume.missing import MISSING_USER_PROMPT
from app.prompts.resume.recommendations import RECOMMENDATIONS_USER_PROMPT
from app.prompts.resume.improvements import IMPROVEMENTS_USER_PROMPT


def test_overall_prompt_formatting():
    formatted = OVERALL_USER_PROMPT.format(
        target_role="Backend Engineer",
        experience_level="Senior (5+ years)",
        resume_text="Sample Resume Text",
    )
    assert "Backend Engineer" in formatted
    assert "Senior (5+ years)" in formatted
    assert "Sample Resume Text" in formatted


def test_job_match_prompt_formatting():
    formatted = JOB_MATCH_USER_PROMPT.format(
        target_role="Data Engineer",
        experience_level="Mid-Level",
        job_description="Seeking Kafka and Spark specialist",
        resume_text="Experience with Spark",
    )
    assert "Data Engineer" in formatted
    assert "Seeking Kafka and Spark specialist" in formatted


def test_sections_prompt_formatting_with_jd():
    jd_context = "\nJob Description Context:\nPython Developer JD\n"
    formatted = SECTIONS_USER_PROMPT.format(
        target_role="Python Developer",
        experience_level="Junior",
        optional_jd_context=jd_context,
        resume_text="Resume details",
    )
    assert "Python Developer JD" in formatted
    assert "Resume details" in formatted
