# ApexHire / ApexResume — Complete Project Problem Statement

## 1. Project Overview

**ApexHire** is an AI-powered career platform designed to help candidates improve their employability through resume analysis, interview preparation, career mentorship, and future job-oriented capabilities.

The first major module is **ApexResume**, an AI-powered resume analysis system.

The resume system allows an authenticated user to:

- Upload a PDF resume.
- Select a target job role.
- Select an experience level.
- Optionally provide a job description.
- Run an AI-powered resume analysis.
- Receive an overall resume score.
- Receive an ATS compatibility score.
- Receive a job-match score when a job description is supplied.
- Review detailed section-level analysis.
- Understand strengths and weaknesses.
- Identify missing skills and keywords.
- Receive prioritized recommendations.
- Receive actionable improvement suggestions.
- Save analysis reports.
- View previous reports.
- Search, filter, sort, and paginate reports.
- View the original resume alongside its analysis.
- Download the uploaded resume.
- Delete reports.
- Update report metadata such as its title.

The project is intended to evolve into a broader AI career platform, so the architecture must remain modular and extensible.

---

# 2. Core Problem Statement

Job applicants often submit resumes without knowing:

- Whether the resume is ATS-friendly.
- Whether the resume matches the target role.
- Which skills or keywords are missing.
- Whether the experience section effectively communicates impact.
- Whether projects demonstrate relevant technical capability.
- Whether formatting could cause ATS parsing problems.
- How competitive the resume is for a particular job description.
- What specific changes should be made before applying.

Traditional resume review is manual, inconsistent, time-consuming, and difficult to scale.

ApexResume addresses this problem by creating an automated AI-powered resume evaluation system that analyzes a candidate's resume against a target role, experience level, and optionally a specific job description.

The system must transform an uploaded resume into a structured, explainable, actionable report rather than simply returning generic AI-generated advice.

---

# 3. Product Goals

## Primary Goals

1. Provide automated resume analysis.
2. Provide ATS compatibility evaluation.
3. Provide job-description matching.
4. Identify strengths and weaknesses.
5. Identify missing skills and keywords.
6. Generate prioritized recommendations.
7. Generate actionable resume improvements.
8. Persist reports for future reference.
9. Provide secure user-specific report access.
10. Maintain a clean separation between frontend, core backend, and AI processing.
11. Support future AI career modules without requiring a major architectural rewrite.

## Secondary Goals

- Keep analysis results structured and predictable.
- Make the AI workflow modular.
- Allow multiple LLM providers.
- Handle AI failures gracefully.
- Prevent API keys from reaching the frontend.
- Support scalable storage.
- Support asynchronous processing in the future.
- Maintain strong validation and security.
- Make the backend easy to test and maintain.

---

# 4. High-Level Architecture

The target architecture is:

```text
                    ┌───────────────────────┐
                    │      React Frontend   │
                    │      ApexHire UI      │
                    └───────────┬───────────┘
                                │
                                │ HTTPS / REST
                                ▼
                    ┌───────────────────────┐
                    │   Spring Boot Backend │
                    │                       │
                    │ Authentication        │
                    │ Authorization         │
                    │ Resume APIs           │
                    │ Persistence           │
                    │ File Storage          │
                    │ API Orchestration     │
                    └───────────┬───────────┘
                                │
                                │ REST
                                ▼
                    ┌───────────────────────┐
                    │ Python AI Backend     │
                    │ FastAPI               │
                    │ LangGraph             │
                    │ LangChain             │
                    │ AI Workflows          │
                    └───────────┬───────────┘
                                │
                     ┌──────────┴──────────┐
                     ▼                     ▼
              ┌──────────────┐      ┌──────────────┐
              │ Gemini       │      │ Groq / Other │
              │ LLM          │      │ LLM Provider │
              └──────────────┘      └──────────────┘
```

The Spring Boot backend is the primary application backend.

The Python backend is an internal AI-processing service.

The frontend must not communicate directly with the LLM provider.

---

# 5. Existing Frontend Resume Functionality

The current frontend defines the expected resume-analysis experience.

## 5.1 Resume Analyzer

Route:

```text
/resume-analyzer
```

Purpose:

Main interface for uploading and analyzing resumes.

Features:

- PDF drag-and-drop upload.
- PDF-only validation.
- Maximum file size of 10 MB.
- Target role selection.
- Experience level selection.
- Optional resume title.
- Optional job description.
- AI analysis progress.
- Recent reports.
- Redirect to analysis report after successful processing.

Supported target roles:

```text
Frontend Engineer
Backend Engineer
Fullstack Engineer
Mobile Engineer
ML / AI Engineer
Infrastructure / DevOps Engineer
Data Engineer
Embedded / Systems Engineer
```

Supported experience levels:

```text
Junior (0-2 years)
Mid-level (2-5 years)
Senior (5-10 years)
Staff+ (10+ years)
```

---

# 6. Resume Report Page

Route:

```text
/resume-report/:id
```

Purpose:

Display a complete analysis for a specific resume.

Features:

- PDF viewer.
- Analysis panel.
- Report title.
- Target role.
- Experience level.
- Analysis date.
- Original resume download.
- Delete report.
- Navigation back to reports.
- Loading state.
- Error state.

The preferred layout is:

```text
┌───────────────────────┬──────────────────────────┐
│                       │                          │
│     PDF Viewer        │     Analysis Panel       │
│                       │                          │
│     Resume            │     Scores               │
│                       │     Summary              │
│                       │     Sections             │
│                       │     Strengths            │
│                       │     Weaknesses           │
│                       │     Missing Skills       │
│                       │     Keywords             │
│                       │     Recommendations      │
│                       │     Improvements         │
│                       │                          │
└───────────────────────┴──────────────────────────┘
```

---

# 7. All Reports Page

Route:

```text
/resume-reports
```

Purpose:

Allow users to browse and manage historical resume-analysis reports.

Features:

- Search.
- Role filtering.
- Experience-level filtering.
- Sorting.
- Pagination.
- Report count.
- Individual report navigation.

Search should support:

- Report title.
- Original filename.
- Target role.

Sorting options:

```text
newest
oldest
score-high
score-low
```

Default:

```text
newest
```

Pagination:

```text
10 reports per page
```

---

# 8. Analysis Panel Requirements

The analysis panel must display:

## Score Overview

- Overall score.
- ATS score.
- Job match score.

All scores are on a 0–100 scale.

If no job description was supplied:

```text
jobMatchScore = null
```

## Summary

AI-generated overall explanation.

## Section Breakdown

The following sections must be evaluated:

```text
skills
keywords
experience
education
projects
content
formatting
```

Each section contains:

- Section key.
- Display title.
- Score.
- Summary.
- Detailed points.

## Strengths

A list of positive aspects of the resume.

## Weaknesses

A list of problems or areas needing improvement.

## Missing Skills

Skills relevant to the target role that are missing or insufficiently demonstrated.

## Missing Keywords

Relevant keywords that could improve job/ATS matching.

## Recommendations

Prioritized recommendations:

```text
high
medium
low
```

Each recommendation contains:

- Title.
- Detail.
- Priority.

## Suggested Improvements

A numbered list of actionable improvements.

---

# 9. Core Data Model

## ResumeReport

```text
ResumeReport
├── id
├── title
├── fileName
├── fileSize
├── targetRole
├── experienceLevel
├── jobDescription
├── resumeText
├── analysis
├── fileStoragePath
├── user
├── createdAt
└── analyzedAt
```

## AnalysisResult

```text
AnalysisResult
├── overallScore
├── atsScore
├── jobMatchScore
├── summary
├── sections[]
├── strengths[]
├── weaknesses[]
├── missingSkills[]
├── missingKeywords[]
├── recommendations[]
└── improvements[]
```

## AnalysisSection

```text
AnalysisSection
├── key
├── title
├── score
├── summary
└── points[]
```

## Recommendation

```text
Recommendation
├── title
├── detail
└── priority
```

---

# 10. Frontend Input Contract

The frontend analysis request is:

```json
{
  "resumeText": "string",
  "targetRole": "string",
  "experienceLevel": "string",
  "resumeTitle": "string",
  "jobDescription": "string"
}
```

Validation:

```text
resumeText:
    minimum 30 characters

targetRole:
    minimum 2 characters
    maximum 80 characters

experienceLevel:
    minimum 2 characters
    maximum 60 characters

resumeTitle:
    maximum 120 characters

jobDescription:
    maximum 20,000 characters
```

---

# 11. Backend REST API

All resume endpoints require authentication.

## 11.1 Analyze Resume

```http
POST /api/resume/analyze
```

Request:

```json
{
  "resumeText": "string",
  "targetRole": "Backend Engineer",
  "experienceLevel": "Junior (0-2 years)",
  "resumeTitle": "Backend Resume",
  "jobDescription": "optional job description"
}
```

Responsibilities:

1. Authenticate user.
2. Validate request.
3. Build Python AI-service request.
4. Call Python backend.
5. Receive structured analysis.
6. Persist report.
7. Return analysis to frontend.

---

# 12. Upload Resume

```http
POST /api/resume/upload
```

Content type:

```text
multipart/form-data
```

Field:

```text
file
```

Constraints:

```text
PDF only
Maximum 10 MB
```

Response:

```json
{
  "fileId": "string",
  "fileName": "resume.pdf",
  "fileSize": 123456,
  "uploadedAt": "ISO timestamp"
}
```

---

# 13. Get Reports

```http
GET /api/resume/reports
```

Parameters:

```text
page
limit
role
level
search
sort
```

Example:

```text
/api/resume/reports?page=0&limit=10&role=Backend%20Engineer&sort=newest
```

Response:

```json
{
  "reports": [],
  "total": 0,
  "page": 0,
  "limit": 10,
  "totalPages": 0
}
```

The backend must return only reports owned by the authenticated user.

---

# 14. Get Individual Report

```http
GET /api/resume/reports/{id}
```

Responsibilities:

- Validate authentication.
- Verify report ownership.
- Retrieve report.
- Deserialize analysis.
- Return complete report.

---

# 15. Download Resume

```http
GET /api/resume/download/{id}
```

Response:

```text
application/pdf
```

The backend must verify that the authenticated user owns the report before returning the file.

---

# 16. Delete Report

```http
DELETE /api/resume/reports/{id}
```

Expected behavior:

1. Verify ownership.
2. Delete associated file.
3. Delete report.
4. Return success.

Response:

```json
{
  "success": true,
  "message": "Report deleted successfully"
}
```

---

# 17. Update Report

```http
PUT /api/resume/reports/{id}
```

Request:

```json
{
  "title": "Updated Resume Title"
}
```

Purpose:

Allow users to update report metadata.

---

# 18. Spring Boot Backend Responsibilities

Spring Boot acts as the application's main backend and orchestration layer.

It must handle:

- Authentication.
- Authorization.
- JWT validation.
- User identification.
- Request validation.
- Resume APIs.
- Report persistence.
- File storage.
- File retrieval.
- File deletion.
- Communication with Python AI backend.
- Error translation.
- Logging.
- API security.
- Future module integration.

Spring Boot should NOT contain the core LLM prompting/workflow logic.

That responsibility belongs to the Python AI backend.

---

# 19. Spring Boot Package Structure

The resume module should remain modular.

Suggested structure:

```text
com.apexhire
├── auth/
├── resume/
│   ├── config/
│   ├── controller/
│   ├── service/
│   ├── repository/
│   ├── entity/
│   ├── dto/
│   │   ├── request/
│   │   └── response/
│   ├── model/
│   │   ├── langgraph/
│   │   └── enums/
│   ├── exception/
│   └── mapper/
├── interview/
│   └── ...
├── career/
│   └── ...
└── common/
    ├── exception/
    ├── security/
    └── response/
```

Future modules such as Interview should be able to coexist without restructuring the entire backend.

---

# 20. Spring Boot Technologies

Target stack:

```text
Java 17 or Java 21
Spring Boot 3.x
Spring Web
Spring Security
Spring Data JPA
Spring Validation
Spring WebFlux / WebClient
PostgreSQL
JWT
Jackson
Lombok
Spring Boot Actuator
```

Build tool:

```text
Maven
```

---

# 21. Database

The backend should persist resume reports in a relational database.

Recommended:

```text
PostgreSQL
```

Database:

```text
apexhire
```

Main table:

```text
resume_reports
```

Relationship:

```text
User 1 ─────────── N ResumeReport
```

---

# 22. ResumeReport Persistence Model

Conceptual schema:

```text
resume_reports
────────────────────────────────────
id                    UUID
user_id               UUID
title                 VARCHAR
file_name             VARCHAR
file_size             BIGINT
target_role           VARCHAR/ENUM
experience_level      VARCHAR/ENUM
job_description       TEXT
resume_text           TEXT
analysis_json         JSON/TEXT
file_storage_path     VARCHAR
created_at            TIMESTAMP
analyzed_at           TIMESTAMP
```

The report must always be associated with a user.

---

# 23. User Ownership and Authorization

Every report operation must enforce ownership.

A user must never be able to:

- Read another user's report.
- Download another user's resume.
- Delete another user's report.
- Modify another user's report.

Ownership checks should be implemented server-side.

Never trust a user ID supplied by the frontend.

The authenticated identity from the security context must determine the current user.

---

# 24. File Storage

Initial implementation may use local filesystem storage.

Example:

```text
./storage/
    {userId}/
        resumes/
            {fileId}.pdf
```

Production deployment should support object storage such as AWS S3.

The database stores the reference/path rather than relying on the database to store large binary PDF data.

Requirements:

- Unique file IDs.
- PDF validation.
- 10 MB maximum.
- Safe filename handling.
- No path traversal.
- User-specific storage.
- Cleanup after report deletion.
- Proper error handling.

---

# 25. PDF Processing

The current frontend uses PDF.js to extract/display PDF content.

The target backend architecture may continue to receive extracted `resumeText` from the frontend for analysis.

However, the upload API should preserve the original PDF.

The architecture should remain flexible enough to move PDF text extraction to the backend later if required.

---

# 26. Python AI Backend

The Python service is responsible for AI processing.

Technology:

```text
Python
FastAPI
LangGraph
LangChain
Pydantic
```

The service should be independently deployable.

Example:

```text
python-ai-service/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── models/
│   ├── workflows/
│   ├── agents/
│   ├── services/
│   ├── prompts/
│   ├── utils/
│   └── exceptions/
├── tests/
├── requirements.txt
├── .env
└── README.md
```

---

# 27. Python AI Service Responsibilities

The Python service must:

- Validate AI requests.
- Run resume-analysis workflows.
- Call configured LLM providers.
- Produce structured output.
- Handle provider failures.
- Handle malformed AI responses.
- Apply retries where appropriate.
- Support asynchronous execution.
- Support future AI workflows.
- Keep prompts separate from application code.
- Keep provider-specific logic separate from business logic.

---

# 28. AI Providers

The intended providers are:

```text
Gemini
Groq
```

The implementation should use a provider abstraction so that the workflow does not depend directly on a single provider.

Conceptually:

```text
Resume Analysis Workflow
          │
          ▼
     LLM Service
          │
     ┌────┴────┐
     ▼         ▼
  Gemini     Groq
```

Environment variables must hold credentials.

Never hard-code API keys.

---

# 29. LangChain and LangGraph

LangGraph should be used to model the resume-analysis workflow.

LangChain should be used for:

- LLM integration.
- Prompt handling.
- Structured output.
- Provider abstraction.
- Relevant AI utilities.

LangGraph should orchestrate analysis stages.

The workflow must remain modular so that individual nodes can later be:

- Reordered.
- Parallelized.
- Replaced.
- Cached.
- Retried.
- Extended.

---

# 30. Resume Analysis Workflow

Conceptual workflow:

```text
START
  │
  ▼
Validate Input
  │
  ▼
Analyze Overall Resume
  │
  ▼
Analyze ATS Compatibility
  │
  ▼
Analyze Job Match
  │
  ▼
Analyze Resume Sections
  │
  ▼
Identify Strengths & Weaknesses
  │
  ▼
Identify Missing Skills & Keywords
  │
  ▼
Generate Recommendations
  │
  ▼
Generate Improvements
  │
  ▼
Validate Final Structured Result
  │
  ▼
END
```

---

# 31. Analysis Nodes

## Overall Analysis

Evaluate:

- General resume quality.
- Relevance to target role.
- Clarity.
- Professional positioning.
- Experience level alignment.

Output:

```text
overallScore
summary
```

## ATS Analysis

Evaluate:

- Resume structure.
- Formatting.
- Keyword usage.
- Section clarity.
- Machine readability.

Output:

```text
atsScore
```

## Job Match

Only run meaningful job matching when a job description is supplied.

Evaluate:

- Skills overlap.
- Experience relevance.
- Keyword overlap.
- Responsibilities.
- Requirements.
- Technology alignment.

Output:

```text
jobMatchScore
```

If no job description exists:

```text
jobMatchScore = null
```

---

# 32. Section Analysis

Analyze:

```text
Skills
Keywords
Experience
Education
Projects
Content
Formatting
```

Each section must return:

```json
{
  "key": "skills",
  "title": "Skills",
  "score": 85,
  "summary": "string",
  "points": [
    "string"
  ]
}
```

---

# 33. Strength and Weakness Analysis

The AI should identify concrete strengths and weaknesses.

Avoid generic statements such as:

```text
"Your resume is good."
```

Prefer actionable findings based on the actual resume.

Example categories:

```text
Technical depth
Relevant experience
Project quality
Achievement quantification
Keyword coverage
Resume structure
Formatting
Clarity
```

---

# 34. Missing Skills

The system should identify skills that are relevant to the selected target role but are not sufficiently represented in the resume.

The AI should distinguish between:

- Completely missing skills.
- Skills mentioned but poorly demonstrated.
- Skills that are relevant but not necessary.

The output should avoid inventing requirements unrelated to the target role.

---

# 35. Missing Keywords

The system should identify relevant keywords that could improve:

- ATS compatibility.
- Job matching.
- Recruiter discoverability.

If a job description is supplied, the job description should be the primary reference for job-specific keyword identification.

---

# 36. Recommendations

Recommendations should be prioritized.

Format:

```json
{
  "title": "Quantify backend achievements",
  "detail": "Add measurable outcomes...",
  "priority": "high"
}
```

Priorities:

```text
high
medium
low
```

Recommendations should be specific enough for the user to act on.

---

# 37. Improvements

Suggested improvements should be actionable.

Examples of improvement categories:

- Rewrite weak bullet points.
- Add measurable impact.
- Improve technical keyword coverage.
- Remove irrelevant content.
- Improve project descriptions.
- Improve formatting.
- Improve professional summary.

The system should avoid unnecessarily rewriting the entire resume unless a future feature explicitly requests it.

---

# 38. AI Structured Output

The Python backend must return predictable JSON.

Example:

```json
{
  "overall_score": 85,
  "ats_score": 78,
  "job_match_score": 90,
  "summary": "Overall analysis...",
  "sections": [
    {
      "key": "skills",
      "title": "Skills",
      "score": 85,
      "summary": "Strong backend stack...",
      "points": [
        "Good Java coverage",
        "Spring Boot is relevant"
      ]
    }
  ],
  "strengths": [
    "Strong backend technology coverage"
  ],
  "weaknesses": [
    "Limited quantified achievements"
  ],
  "missing_skills": [
    "Docker"
  ],
  "missing_keywords": [
    "REST APIs"
  ],
  "recommendations": [
    {
      "title": "Quantify experience",
      "detail": "Add measurable outcomes...",
      "priority": "high"
    }
  ],
  "improvements": [
    "Rewrite experience bullets using measurable impact"
  ]
}
```

---

# 39. LLM Output Validation

AI output must never be trusted blindly.

The Python service must validate:

- Required fields.
- Numeric ranges.
- Enum values.
- Array types.
- String fields.
- Recommendation priority.
- Nullable job-match score.

Scores must remain:

```text
0 <= score <= 100
```

Malformed AI output must result in a controlled error or retry rather than corrupting the database.

---

# 40. Spring Boot ↔ Python Contract

Spring Boot sends:

```json
{
  "resume_text": "string",
  "target_role": "Backend Engineer",
  "experience_level": "Junior (0-2 years)",
  "job_description": "optional"
}
```

Python returns:

```json
{
  "overall_score": 85,
  "ats_score": 78,
  "job_match_score": 90,
  "summary": "string",
  "sections": [],
  "strengths": [],
  "weaknesses": [],
  "missing_skills": [],
  "missing_keywords": [],
  "recommendations": [],
  "improvements": []
}
```

Spring Boot is responsible for translating between external frontend DTO naming conventions and the Python-service contract if required.

---

# 41. Python API

## Analyze

```http
POST /analyze
```

## Health

```http
GET /health
```

Potential future endpoints:

```text
GET /ready
GET /metrics
POST /interview/analyze
POST /career/advice
```

These should be added as separate modules rather than mixing all AI logic into one file.

---

# 42. Authentication Between Services

The frontend authenticates with Spring Boot using the existing authentication system and JWT.

The Python AI service should not rely on frontend authentication directly.

Spring Boot should authenticate the user first and then securely authenticate requests to the Python service using a service-to-service credential/API key or another internal authentication mechanism.

The Python service should never receive or need the user's raw login credentials.

---

# 43. Security Requirements

## Authentication

All resume APIs require authenticated users.

## Authorization

All report operations must enforce ownership.

## API Keys

LLM credentials must remain server-side.

Never expose:

```text
GEMINI_API_KEY
GROQ_API_KEY
LANGGRAPH_API_KEY
```

to React.

## File Security

Validate:

- Content type.
- File extension.
- File size.
- Storage path.
- Filename.

## Input Security

Validate:

- Resume text.
- Role.
- Experience level.
- Job description.
- Report title.

---

# 44. Data Privacy

Resume data can contain sensitive professional and personal information.

The system should therefore:

- Restrict access to the owner.
- Avoid exposing resume content in logs.
- Avoid logging API keys.
- Avoid logging full AI prompts containing resumes.
- Support deletion.
- Consider encryption at rest in production.
- Define data retention policies.
- Minimize unnecessary data copies.

---

# 45. Error Handling

## Spring Boot Errors

Expected categories:

```text
VALIDATION_ERROR
UNAUTHORIZED
FORBIDDEN
REPORT_NOT_FOUND
FILE_NOT_FOUND
FILE_VALIDATION_ERROR
ANALYSIS_ERROR
AI_SERVICE_UNAVAILABLE
INTERNAL_ERROR
```

Example:

```json
{
  "code": "ANALYSIS_ERROR",
  "message": "Resume analysis failed",
  "timestamp": "ISO timestamp"
}
```

## Python Errors

Handle:

- Invalid request.
- Provider authentication failure.
- Provider rate limit.
- Provider timeout.
- Malformed structured output.
- Internal workflow failure.

Do not return raw stack traces to clients.

---

# 46. AI Provider Failure Strategy

The AI layer should support controlled failure handling.

Possible strategy:

```text
Request
   │
   ▼
Primary LLM
   │
   ├── Success → Continue
   │
   └── Failure
          │
          ▼
       Retry
          │
          └── Failure
                 │
                 ▼
          Optional fallback provider
```

Provider fallback should be configurable.

---

# 47. Performance Requirements

The system should be designed for efficient AI processing.

Important optimizations:

- Async LLM calls where possible.
- Parallel independent analysis nodes.
- Result caching.
- Request throttling.
- Timeouts.
- Connection pooling.
- Pagination.
- Efficient database queries.
- Avoid unnecessary large payloads.
- Avoid repeatedly sending identical resume content to the LLM.

The initial implementation can use sequential workflow execution for simplicity, but the graph should be designed so independent analyses can later execute in parallel.

---

# 48. Caching

Potential cache key:

```text
hash(
    resumeText +
    targetRole +
    experienceLevel +
    jobDescription
)
```

Identical analysis requests may reuse a cached result.

Caching must not accidentally expose one user's report to another user.

A cache hit should still respect user/report ownership rules.

---

# 49. Timeout Requirements

Spring Boot → Python:

```text
approximately 2 minutes initial timeout
```

Python → LLM:

Use provider-appropriate timeouts.

Timeouts must be configurable using environment variables.

---

# 50. Rate Limiting

The analysis endpoint is an expensive AI operation.

The system should eventually enforce:

- Per-user limits.
- Per-IP limits where appropriate.
- Provider-aware throttling.
- Concurrent analysis limits.

The Python service should also protect itself from excessive concurrent LLM calls.

---

# 51. Logging and Monitoring

Use structured logging.

Log:

- Request ID.
- User/report identifier where appropriate.
- Analysis start/end.
- Processing duration.
- Provider used.
- Success/failure.
- Error category.

Do NOT log:

- Full resume text.
- Full job descriptions.
- API keys.
- Sensitive user content.

Spring Boot Actuator can provide health and operational endpoints.

---

# 52. Frontend Migration

The existing frontend currently uses client-side storage.

Current storage:

```text
LocalStorage
IndexedDB
```

Target storage:

```text
Spring Boot API
PostgreSQL
Filesystem / S3
```

---

# 53. LocalStorage Migration

Replace:

```text
loadReports()
saveReport()
deleteReport()
getReport()
```

with API requests.

Target:

```text
GET    /api/resume/reports
GET    /api/resume/reports/{id}
DELETE /api/resume/reports/{id}
PUT    /api/resume/reports/{id}
```

---

# 54. IndexedDB Migration

Replace client-side PDF storage with backend storage.

Target:

```text
POST /api/resume/upload
GET  /api/resume/download/{id}
```

The frontend should no longer be responsible for permanent PDF persistence.

---

# 55. Analysis Migration

Current:

```text
React
   ↓
Lovable AI Gateway
```

Target:

```text
React
   ↓
Spring Boot
   ↓
Python LangGraph
   ↓
Gemini / Groq
```

The frontend must no longer contain the LLM provider API key.

---

# 56. Current Client-Side Flow

```text
User uploads PDF
        ↓
PDF.js extracts text
        ↓
Select target role
        ↓
Select experience level
        ↓
Optional job description
        ↓
Call AI gateway
        ↓
Receive AnalysisResult
        ↓
Save metadata to LocalStorage
        ↓
Save PDF to IndexedDB
        ↓
Open report
```

---

# 57. Target Production Flow

```text
User uploads PDF
        ↓
Frontend validates file
        ↓
Frontend uploads PDF
        ↓
Spring Boot validates and stores PDF
        ↓
Frontend sends analysis request
        ↓
Spring Boot authenticates user
        ↓
Spring Boot validates request
        ↓
Spring Boot calls Python AI service
        ↓
Python validates request
        ↓
LangGraph executes analysis
        ↓
LLM provider generates structured output
        ↓
Python validates final output
        ↓
Python returns AnalysisResult
        ↓
Spring Boot persists report
        ↓
Spring Boot returns result
        ↓
Frontend displays report
```

---

# 58. Complete Component Interaction

```text
┌──────────────┐
│    User      │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ React Frontend   │
│ Resume Analyzer  │
└────────┬─────────┘
         │
         │ JWT
         ▼
┌──────────────────┐
│ Spring Security  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ ResumeController │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Resume Service   │
└──────┬─────┬─────┘
       │     │
       │     └──────────────────┐
       │                        ▼
       │                ┌───────────────┐
       │                │ File Storage  │
       │                └───────────────┘
       │
       ▼
┌──────────────────┐
│ LangGraph Service│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Python FastAPI   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ LangGraph Graph  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ LLM Service      │
└───────┬─────┬────┘
        │     │
        ▼     ▼
     Gemini  Groq
```

---

# 59. Spring Boot Service Layer

Recommended services:

```text
ResumeService
AnalysisService
FileStorageService
LangGraphService
```

Responsibilities:

### ResumeService

- Report CRUD.
- Search.
- Filtering.
- Sorting.
- Pagination.
- Ownership checks.

### AnalysisService

- Build AI request.
- Call AI service.
- Persist analysis result.
- Build report.

### FileStorageService

- Upload.
- Validate.
- Store.
- Download.
- Delete.

### LangGraphService

- Communicate with Python.
- Handle timeout.
- Handle service errors.
- Map requests/responses.

---

# 60. Repository Layer

Suggested repositories:

```text
ResumeReportRepository
UserRepository
```

Resume queries must support:

- User filtering.
- Role filtering.
- Experience-level filtering.
- Search.
- Pagination.
- Sorting.

Database indexes should eventually be added for frequently queried fields.

---

# 61. DTO Layer

Request DTOs:

```text
AnalyzeResumeRequest
UpdateReportRequest
```

Response DTOs:

```text
AnalysisResultResponse
ResumeReportResponse
FileUploadResponse
DeleteResponse
ErrorResponse
```

Internal Python contract models:

```text
LangGraphRequest
LangGraphResponse
```

Do not expose persistence entities directly through the API.

---

# 62. Entity Layer

Main entity:

```text
ResumeReport
```

Existing:

```text
User
```

Relationship:

```text
User
  │
  └── resumeReports
          ├── Report 1
          ├── Report 2
          └── Report N
```

---

# 63. Configuration

Spring Boot environment:

```properties
SPRING_DATASOURCE_URL=
SPRING_DATASOURCE_USERNAME=
SPRING_DATASOURCE_PASSWORD=

LANGGRAPH_API_URL=
LANGGRAPH_API_KEY=
LANGGRAPH_API_TIMEOUT=

FILE_STORAGE_LOCATION=
FILE_STORAGE_MAX_SIZE=

JWT_SECRET=
JWT_EXPIRATION=

SERVER_PORT=
```

Python environment:

```properties
HOST=
PORT=

LLM_PROVIDER=
LLM_MODEL=
LLM_TEMPERATURE=

GEMINI_API_KEY=
GROQ_API_KEY=

AI_SERVICE_API_KEY=
AI_REQUEST_TIMEOUT=
```

Never commit `.env` files containing secrets.

Provide:

```text
.env.example
```

instead.

---

# 64. Python Requirements

The Python service should include at minimum the relevant packages for:

```text
FastAPI
Uvicorn
Pydantic
Pydantic Settings
LangChain
LangGraph
Gemini integration
Groq integration
HTTP client
pytest
```

Exact package versions should be pinned to tested compatible versions in `requirements.txt`.

---

# 65. Python Configuration

Configuration should be centralized.

Example conceptual model:

```text
Settings
├── server
├── AI provider
├── model
├── temperature
├── API keys
├── timeout
└── service authentication
```

The application must load configuration from environment variables.

---

# 66. Python Module Design

Recommended:

```text
app/
├── main.py
│
├── config/
│   └── settings.py
│
├── api/
│   └── routes/
│       ├── health.py
│       └── resume.py
│
├── models/
│   ├── requests.py
│   ├── responses.py
│   └── analysis.py
│
├── workflows/
│   └── resume_analysis/
│       ├── graph.py
│       ├── state.py
│       └── nodes/
│           ├── overall.py
│           ├── ats.py
│           ├── job_match.py
│           ├── sections.py
│           ├── strengths.py
│           ├── missing.py
│           ├── recommendations.py
│           └── improvements.py
│
├── services/
│   ├── llm_service.py
│   ├── provider_service.py
│   └── analysis_service.py
│
├── prompts/
│   └── resume/
│
├── exceptions/
│
└── utils/
```

This structure is intentionally modular so future modules can be added.

---

# 67. Future Interview Module

The platform is expected to add an Interview feature.

The architecture should therefore support:

```text
app/
├── resume/
├── interview/
├── career/
└── common/
```

Future interview capabilities may include:

- Interview question generation.
- Mock interviews.
- Answer evaluation.
- Technical interview analysis.
- Behavioral interview analysis.
- Interview feedback.
- Personalized question generation from resumes.

The current resume module must not make assumptions that prevent these features.

---

# 68. Future Career Mentor Module

A future AI Career Mentor may provide:

- Resume advice.
- Interview guidance.
- Skill-roadmap recommendations.
- Career decisions.
- Job-search guidance.
- Personalized learning suggestions.

This should become a separate workflow/module rather than being hard-coded into the resume workflow.

---

# 69. Testing Strategy

## Spring Boot Unit Tests

Test:

- ResumeService.
- AnalysisService.
- FileStorageService.
- LangGraphService.
- Validation.
- Ownership checks.
- Exception handling.

Mock external services.

## Repository Tests

Test:

- User filtering.
- Search.
- Role filtering.
- Experience-level filtering.
- Pagination.
- Sorting.

## Controller Tests

Test:

```text
POST /api/resume/analyze
POST /api/resume/upload
GET /api/resume/reports
GET /api/resume/reports/{id}
GET /api/resume/download/{id}
DELETE /api/resume/reports/{id}
PUT /api/resume/reports/{id}
```

Test authentication and authorization failures.

---

# 70. Python Tests

Test:

- Request validation.
- Response validation.
- Workflow nodes.
- Full LangGraph workflow.
- Provider abstraction.
- Malformed LLM responses.
- Timeout handling.
- Retry handling.
- Missing job description.
- Job matching.
- Score validation.

LLM calls should be mocked in unit tests.

---

# 71. Integration Tests

Important integration scenarios:

### Successful Analysis

```text
Frontend
 → Spring Boot
 → Python
 → Mock LLM
 → Database
```

### Invalid PDF

Should return validation error.

### Oversized PDF

Should be rejected.

### Unauthorized Report

Should return:

```text
403 Forbidden
```

or an appropriate not-found response according to the security policy.

### Python Unavailable

Spring Boot should return a controlled AI-service error.

### AI Provider Failure

Python should retry/fail gracefully.

---

# 72. End-to-End Test

Complete scenario:

```text
Register/Login
   ↓
Upload resume
   ↓
Select Backend Engineer
   ↓
Select Junior
   ↓
Add optional job description
   ↓
Analyze
   ↓
Receive report
   ↓
Report persisted
   ↓
Refresh page
   ↓
Report still available
   ↓
Download resume
   ↓
Update title
   ↓
Delete report
```

---

# 73. Acceptance Criteria

The project is considered functionally complete when:

- An authenticated user can upload a valid PDF.
- Files above 10 MB are rejected.
- Non-PDF files are rejected.
- Users can select target role.
- Users can select experience level.
- Users can optionally provide a job description.
- Resume text is successfully analyzed.
- Python AI service returns validated structured analysis.
- Spring Boot persists the report.
- Users can retrieve their reports.
- Users cannot access another user's reports.
- Users can search reports.
- Users can filter reports.
- Users can sort reports.
- Users can paginate reports.
- Users can view individual reports.
- Users can download original resumes.
- Users can update report titles.
- Users can delete reports.
- Associated files are cleaned up.
- LLM API keys are not exposed to the frontend.
- AI failures are handled gracefully.
- Backend tests cover the core workflow.
- Python workflow tests cover the core analysis.
- The architecture allows future Interview/Career modules.

---

# 74. Non-Functional Requirements

## Security

Strong authentication and authorization.

## Reliability

Controlled failures and timeouts.

## Maintainability

Clear module boundaries.

## Scalability

AI service must be independently scalable.

## Extensibility

Future modules must be easy to add.

## Observability

Health checks and structured logs.

## Performance

Efficient pagination, caching opportunities, and asynchronous AI processing.

## Privacy

Resume data must be protected.

---

# 75. Architectural Principles

The implementation should follow:

### Separation of Concerns

Frontend:

```text
Presentation + API consumption
```

Spring Boot:

```text
Application/business orchestration + persistence + security
```

Python:

```text
AI orchestration + LLM workflows
```

LLM providers:

```text
AI generation
```

### Single Responsibility

Each service/class/module should have a focused responsibility.

### Dependency Inversion

Business logic should depend on abstractions where practical, especially for LLM providers and storage.

### Configuration Over Hard-Coding

Provider, URLs, keys, timeouts, and storage settings must be configurable.

### API Contract First

Spring Boot and Python must share a clearly defined request/response contract.

---

# 76. Important Architectural Correction

The initial client-side implementation used:

```text
LocalStorage
IndexedDB
Lovable AI Gateway
```

These are appropriate for a frontend prototype but are not the target production architecture.

The production architecture must move persistence and AI processing to the backend:

```text
LocalStorage → PostgreSQL
IndexedDB → Backend File Storage / S3
Lovable AI → Python AI Service
Frontend AI calls → Spring Boot
```

---

# 77. Target State

The final system should look like:

```text
                         APEXHIRE
                            │
             ┌──────────────┴──────────────┐
             │                             │
        React Frontend               Spring Boot
             │                             │
             │                       ┌─────┴─────┐
             │                       │           │
             │                    PostgreSQL   Storage
             │
             │                             │
             └─────────────────────────────┘
                                           │
                                           ▼
                                  Python AI Service
                                           │
                                      LangGraph
                                           │
                                      LangChain
                                           │
                              ┌────────────┴────────────┐
                              │                         │
                           Gemini                    Groq
```

---

# 78. Future Evolution

The architecture should eventually support:

```text
ApexHire
│
├── Authentication
│
├── Resume
│   ├── Upload
│   ├── Analysis
│   ├── Reports
│   ├── Resume Improvement
│   └── Resume Comparison
│
├── Interview
│   ├── Question Generation
│   ├── Mock Interview
│   ├── Answer Evaluation
│   └── Feedback
│
├── Career Mentor
│   ├── Chat
│   ├── Career Advice
│   ├── Skill Roadmap
│   └── Job Guidance
│
└── Jobs
    ├── Job Search
    ├── Matching
    └── Application Tracking
```

The resume module is therefore the first AI workflow, not the entire AI architecture.

---

# 79. Development Priority

Recommended implementation order:

## Phase 1 — Backend Foundation

1. Create resume module.
2. Create entities.
3. Create repositories.
4. Create DTOs.
5. Configure validation.
6. Connect PostgreSQL.
7. Integrate existing JWT security.

## Phase 2 — Resume File Management

1. PDF validation.
2. Upload endpoint.
3. File storage.
4. Download endpoint.
5. Delete cleanup.

## Phase 3 — Python AI Service

1. Create FastAPI application.
2. Create Pydantic contracts.
3. Configure Gemini/Groq.
4. Create LangChain LLM abstraction.
5. Create LangGraph state.
6. Create analysis nodes.
7. Implement structured output validation.
8. Add health endpoint.

## Phase 4 — Spring Boot ↔ Python Integration

1. Create WebClient.
2. Create Python request DTO.
3. Create Python response DTO.
4. Add service authentication.
5. Add timeout handling.
6. Add error handling.
7. Persist successful analyses.

## Phase 5 — Report Management

1. Get reports.
2. Search.
3. Filters.
4. Sorting.
5. Pagination.
6. Get individual report.
7. Update title.
8. Delete report.

## Phase 6 — Frontend Migration

1. Remove LocalStorage report persistence.
2. Remove IndexedDB permanent storage.
3. Replace direct AI calls.
4. Integrate Spring Boot APIs.
5. Add authentication headers.
6. Handle token refresh.
7. Handle API errors.

## Phase 7 — Testing

1. Unit tests.
2. Repository tests.
3. Controller tests.
4. Python workflow tests.
5. Integration tests.
6. End-to-end tests.

## Phase 8 — Optimization

1. Caching.
2. Parallel LangGraph nodes.
3. Rate limiting.
4. Monitoring.
5. S3 storage.
6. Async job processing.

---

# 80. Definition of the Project

**ApexResume is an AI-powered resume intelligence system within ApexHire that securely transforms a candidate's resume into a persistent, structured, explainable, and actionable analysis report.**

The system combines:

```text
React
+
Spring Boot
+
PostgreSQL
+
Secure File Storage
+
FastAPI
+
LangGraph
+
LangChain
+
Gemini / Groq
```

The key architectural goal is to keep the system modular:

```text
Frontend
    ↓
Spring Boot
    ↓
Domain Modules
    ↓
Python AI Workflows
    ↓
LLM Providers
```

This allows ApexResume to become the foundation for additional AI-powered career features such as Interview Preparation and Career Mentorship without requiring a fundamental redesign of the platform.
