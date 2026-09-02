# ApexHire AI Service (Python AI Backend)

An enterprise-grade, high-performance Python AI microservice for the **ApexHire / ApexResume** platform.  
Orchestrates resume analysis workflows using **LangGraph**, **LangChain**, **Google Gemini**, and **Groq** to return strongly-typed, schema-validated candidate assessments.

---

## 1. System Architecture

```text
                     React Frontend (Port 5173)
                                │
                                │ HTTPS / REST
                                ▼
                   Spring Boot Backend (Port 9000)
                                │
                                │ Internal REST (Bearer Auth)
                                ▼
               Python AI Backend / FastAPI (Port 8000)
                                │
                                ▼
                  AnalysisService & LangGraph Workflow
                                │
                ┌───────────────┴───────────────┐
                ▼                               ▼
       Gemini Provider                   Groq Provider
   (gemini-flash-latest / 3.7-flash)    (qwen/qwen3.8-27b)
```

### Separation of Concerns
- **Spring Boot Backend (`localhost:9000`)**: User authentication, JWT sessions, MongoDB persistence, PDF file storage, applicant tracking, and report management.
- **Python AI Backend (`localhost:8000`)**: Stateless AI processing, prompt engineering, LangGraph workflow execution, LLM provider abstraction, structured JSON response validation, and resilient AI error recovery.

---

## 2. LangGraph Workflow

The resume analysis executes as a high-performance, low-latency state machine graph:

```text
START ──► Comprehensive Analysis Node ──► Final Validation Node ──► END
```

1. **Comprehensive Analysis Node**:
   - **Overall Quality & Alignment**: Generates `overall_score` (0-100) and comprehensive candidate summary.
   - **ATS Compatibility**: Generates `ats_score` (0-100) assessing machine readability, layout, and keywords.
   - **Job Match Assessment**: Evaluates match against provided `job_description`; automatically returns `job_match_score = null` when no JD is provided.
   - **7-Section Analysis**: Evaluates `skills`, `keywords`, `experience`, `education`, `projects`, `content`, and `formatting`.
   - **Strengths & Weaknesses**: Extracts grounded, evidence-based strengths and gaps.
   - **Missing Elements**: Identifies missing competencies and high-signal keywords.
   - **Prioritized Recommendations**: Generates actionable recommendations with `high`, `medium`, and `low` priorities.
   - **Actionable Improvements**: Produces concrete bullet rewrites and quantifiable metric guidance.
2. **Final Validation Node**:
   - Validates all scores (0-100), required sections, recommendation priorities, and non-empty summaries before responding.

---

## 3. Directory Structure

```text
ApexHire_PythonBackend/
│
├── app/
│   ├── main.py                     # FastAPI application factory, middleware, CORS, lifecycle
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py             # Pydantic Settings management (.env loader)
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                 # Service-to-service Bearer authentication dependency (HTTPBearer)
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── health.py           # Health and readiness endpoints (/health, /ready)
│   │       └── resume.py           # Primary endpoint: POST /api/resume/analyze
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py             # ResumeAnalysisRequest with camelCase/snake_case aliases
│   │   ├── responses.py            # AnalysisResultResponse matching Spring Boot Jackson models
│   │   └── analysis.py             # AnalysisSection, Recommendation, and node output schemas
│   │
│   ├── workflows/
│   │   ├── __init__.py
│   │   └── resume_analysis/
│   │       ├── __init__.py
│   │       ├── state.py            # Strongly-typed ResumeAnalysisState
│   │       ├── graph.py            # LangGraph StateGraph builder
│   │       └── nodes/
│   │           ├── __init__.py
│   │           ├── comprehensive.py# Unified high-speed analysis node
│   │           ├── overall.py      # Overall score & summary node
│   │           ├── ats.py          # ATS evaluation node
│   │           ├── job_match.py    # Job match analysis node
│   │           ├── sections.py     # 7-section analysis node
│   │           ├── strengths.py    # Strengths and weaknesses node
│   │           ├── missing.py      # Missing skills & keywords node
│   │           ├── recommendations.py # Prioritized recommendations node
│   │           ├── improvements.py # Improvement action items node
│   │           └── validation.py   # Final output validation node
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── provider_service.py     # Gemini and Groq model factory & fallback manager
│   │   ├── llm_service.py          # Structured output execution, retries & backoff
│   │   └── analysis_service.py     # High-level domain service orchestrating the workflow
│   │
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── resume/
│   │       ├── __init__.py
│   │       ├── comprehensive.py   # High-density evaluation prompt
│   │       ├── overall.py
│   │       ├── ats.py
│   │       ├── job_match.py
│   │       ├── sections.py
│   │       ├── strengths.py
│   │       ├── missing.py
│   │       ├── recommendations.py
│   │       └── improvements.py
│   │
│   ├── exceptions/
│   │   ├── __init__.py
│   │   ├── ai_exceptions.py        # AIServiceException hierarchy
│   │   └── handlers.py             # FastAPI global exception handlers
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logging.py              # Structured logging & X-Request-ID context
│       └── validation.py           # Domain validation rules & list sanitizers
│
├── tests/
│   ├── __init__.py
│   ├── fixtures/                   # Synthetic resumes & JDs
│   ├── unit/                       # Unit tests (models, validation, prompts, nodes)
│   └── integration/                # Integration tests (/health, /api/resume/analyze)
│
├── pytest.ini                      # Pytest configuration
├── requirements.txt                # Pinned dependencies
├── .env.example                    # Environment template
└── README.md                       # Complete documentation
```

---

## 4. Getting Started

### 4.1 Virtual Environment Setup

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4.2 Install Dependencies
```bash
pip install -r requirements.txt
```

### 4.3 Configure Environment Variables
Copy `.env.example` to `.env`:
```env
APP_NAME=ApexHire AI Service
APP_ENV=development
HOST=0.0.0.0
PORT=8000

# Primary Provider (gemini or groq)
AI_PROVIDER=gemini
AI_MODEL=gemini-flash-latest
AI_TEMPERATURE=0.2

# Fallback Provider
ENABLE_PROVIDER_FALLBACK=true
AI_FALLBACK_PROVIDER=groq
AI_FALLBACK_MODEL=qwen/qwen3.8-27b

# Provider Keys
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-flash-latest

GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=qwen/qwen3.8-27b

# Security
AI_SERVICE_API_KEY=apexhire-ai-service-secret-key-2026
PYTHON_SERVICE_API_KEY=apexhire-ai-service-secret-key-2026

# Resilience
AI_REQUEST_TIMEOUT=120
AI_MAX_RETRIES=2

# CORS
CORS_ORIGINS=http://localhost:9000,http://localhost:5173,http://localhost:3000

LOG_LEVEL=INFO
```

---

## 5. Running the Application

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The service will be accessible at:
- **API Base URL**: `http://localhost:8000`
- **Interactive Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 6. API Reference & Swagger UI Testing

### 6.1 Testing in Swagger UI (`/docs`)
1. Open [http://localhost:8000/docs](http://localhost:8000/docs).
2. Click the green **Authorize 🔓** button at the top right.
3. Under `HTTPBearer`, enter:
   ```text
   apexhire-ai-service-secret-key-2026
   ```
4. Click **Authorize** → **Close**.
5. Expand `POST /api/resume/analyze`, click **Try it out**, paste the JSON payload, and click **Execute**.

### 6.2 Endpoint Details
- **Endpoint**: `POST /api/resume/analyze`
- **Headers**:
  - `Authorization: Bearer apexhire-ai-service-secret-key-2026`
  - `Content-Type: application/json`

#### Request Body
```json
{
  "resume_text": "Alex Morgan\nSenior Backend Engineer with 5+ years of experience in Java, Spring Boot, Kafka, and PostgreSQL.",
  "target_role": "Backend Engineer",
  "experience_level": "Senior (5+ years)",
  "job_description": "We are seeking a Senior Backend Engineer proficient in Java, Spring Boot, and Kafka."
}
```

#### Response Body (200 OK)
```json
{
  "overallScore": 85,
  "atsScore": 80,
  "jobMatchScore": 90,
  "summary": "Alex Morgan presents a strong technical background in Java, Spring Boot, and microservices...",
  "sections": [
    {
      "key": "skills",
      "title": "Technical Skills",
      "score": 90,
      "summary": "Strong modern backend stack coverage.",
      "points": [
        "Java 17/21 and Spring Boot are prominently featured",
        "Kafka and distributed messaging patterns are well demonstrated"
      ]
    }
  ],
  "strengths": [
    "Demonstrated expertise in distributed messaging with Kafka",
    "Deep core Java and Spring Boot experience"
  ],
  "weaknesses": [
    "Lack of measurable latency or throughput metrics in bullet points"
  ],
  "missingSkills": [
    "Kubernetes Helm charts"
  ],
  "missingKeywords": [
    "CI/CD pipeline",
    "OpenTelemetry"
  ],
  "recommendations": [
    {
      "title": "Quantify Latency Improvements",
      "detail": "Add precise metric reductions to database and caching achievements.",
      "priority": "high"
    }
  ],
  "improvements": [
    "Incorporate metrics in the Redis caching achievement bullet."
  ]
}
```

---

## 7. Running Tests

```powershell
pytest -v
```
