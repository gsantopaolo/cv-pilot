# CV-Pilot Architecture Documentation

## Overview

CV-Pilot is an AI-powered resume and motivation letter tailoring system that leverages multi-agent orchestration (CrewAI) to optimize job applications for Applicant Tracking Systems (ATS). The system achieves 85%+ keyword matching by iteratively refining documents using LLM-powered agents.

---

## System Architecture

### High-Level Components

```mermaid
graph TB
    subgraph "User Interface"
        CLI[Command Line Interface]
    end
    
    subgraph "Entry Points"
        GA[gen_application.py]
        GM[gen_motivation.py]
        AN[analyze.py]
    end
    
    subgraph "Crew Orchestration"
        JAC[JobApplicationCrew]
        MLC[MotivationLetterCrew]
    end
    
    subgraph "Agents"
        RES[Researcher Agent]
        STRAT[Resume Strategist Agent]
        PM[Project Manager Agent]
        MLE[Motivation Letter Editor]
    end
    
    subgraph "Tools"
        FRT[FileReadTool]
        KAT[KeywordsAnalyzerTool]
        SWT[ScrapeWebsiteTool]
        SDT[SerperDevTool]
        FWT[FileWriterTool]
        MDX[MDXSearchTool]
    end
    
    subgraph "LLM Providers"
        OAI[OpenAI]
        ANT[Anthropic]
        GEM[Gemini]
    end
    
    subgraph "External Services"
        LT[LangTrace SDK]
        WEB[Web/Company Sites]
    end
    
    subgraph "Outputs"
        NR[new_resume.md]
        ML[motivation_letter.md]
        AS[application_state.json]
    end
    
    CLI --> GA
    CLI --> GM
    CLI --> AN
    
    GA --> JAC
    GM --> MLC
    AN --> KAT
    
    JAC --> RES
    JAC --> STRAT
    MLC --> PM
    MLC --> MLE
    
    RES --> FRT
    RES --> KAT
    RES --> MDX
    
    STRAT --> FRT
    STRAT --> KAT
    STRAT --> MDX
    
    MLE --> FRT
    MLE --> FWT
    MLE --> SWT
    MLE --> SDT
    
    RES --> OAI
    RES --> ANT
    RES --> GEM
    
    STRAT --> OAI
    STRAT --> ANT
    STRAT --> GEM
    
    MLE --> OAI
    MLE --> ANT
    MLE --> GEM
    
    SWT --> WEB
    SDT --> WEB
    
    GA --> LT
    GM --> LT
    
    JAC --> NR
    JAC --> AS
    MLC --> ML
    MLC --> AS
```

---

## Component Details

### 1. Entry Points

| Component | Purpose | Inputs | Outputs |
|-----------|---------|--------|---------|
| `gen_application.py` | Resume tailoring orchestrator | Resume file, Job description | `new_resume.md`, `application_state.json` |
| `gen_motivation.py` | Motivation letter generator | Company URL, Job posting URL | `motivation_letter.md`, `application_state.json` |
| `analyze.py` | Keyword analyzer | Resume file, Job description | Console output (keyword stats, similarity) |

### 2. Crews (Multi-Agent Orchestration)

#### JobApplicationCrew
- **Process**: Sequential
- **Agents**: Researcher, Resume Strategist
- **Goal**: Generate ATS-optimized resume with 85%+ matching score
- **Iteration**: Continues until 85% threshold achieved

#### MotivationLetterCrew
- **Process**: Hierarchical (with Project Manager)
- **Agents**: Project Manager, Motivation Letter Editor
- **Goal**: Generate personalized motivation letter aligned with company values
- **Features**: Company research, value mapping, narrative crafting

### 3. AI Agents

| Agent | Role | Tools | Max Iterations |
|-------|------|-------|----------------|
| **Researcher** | Job market analyst, extracts requirements from job descriptions | FileReadTool, KeywordsAnalyzerTool, MDXSearchTool | 50 |
| **Resume Strategist** | Tailors resume content to job requirements | FileReadTool, KeywordsAnalyzerTool, MDXSearchTool | 60 |
| **Project Manager** | Coordinates motivation letter workflow | N/A (delegation only) | Default |
| **Motivation Letter Editor** | Drafts motivation letters with company research | FileReadTool, FileWriterTool, ScrapeWebsiteTool, DirectoryReadTool | 70 |

### 4. Tools

| Tool | Purpose | Technology |
|------|---------|------------|
| **KeywordsAnalyzerTool** | NLP keyword extraction, cosine similarity calculation | spaCy, NLTK, scikit-learn |
| **FileReadTool** | Read local files (MD, TXT, PDF) | CrewAI Tools |
| **ScrapeWebsiteTool** | Extract company information from websites | CrewAI Tools |
| **SerperDevTool** | Web search for additional context | CrewAI Tools |
| **FileWriterTool** | Write output files | CrewAI Tools |
| **MDXSearchTool** | Search MDX/Markdown documents | CrewAI Tools |

### 5. LLM Integration

- **Supported Providers**: OpenAI, Anthropic, Gemini
- **Configuration**: Environment variables (`LLM_PROVIDER`, `{PROVIDER}_API_KEY`)
- **Default Models**:
  - OpenAI: `gpt-4.1-2025-04-14`
  - Anthropic: `claude-3-7-sonnet-20250219`
  - Gemini: `gemini-2.5-pro-exp-03-25`
- **Tracing**: LangTrace SDK integration (optional)

---

## Sequence Diagrams

### Resume Generation Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI as gen_application.py
    participant JAC as JobApplicationCrew
    participant RES as Researcher Agent
    participant STRAT as Resume Strategist
    participant KAT as KeywordsAnalyzerTool
    participant LLM as LLM Provider
    participant FS as File System
    
    User->>CLI: Execute with --resume & --job_desc
    CLI->>CLI: Validate env vars (LLM_PROVIDER, API_KEY)
    CLI->>JAC: Initialize crew(resume_path, job_desc_path)
    CLI->>JAC: kickoff({resume_path, job_desc_path})
    
    JAC->>RES: Task: extract_job_requirements
    RES->>FS: Read job_desc_path via FileReadTool
    RES->>FS: Read resume_path via FileReadTool
    RES->>KAT: Analyze keywords (resume vs job_desc)
    KAT->>KAT: Extract keywords with spaCy
    KAT->>KAT: Calculate cosine similarity
    KAT-->>RES: Return keyword table & similarity score
    RES->>LLM: Identify missing keywords & strategy
    LLM-->>RES: Missing keywords + integration strategy
    RES-->>JAC: Return structured requirements
    
    JAC->>STRAT: Task: tailor_resume
    STRAT->>FS: Read job_desc_path via FileReadTool
    STRAT->>FS: Read resume_path via FileReadTool
    STRAT->>LLM: Generate tailored resume draft
    LLM-->>STRAT: Resume draft v1
    
    loop Until matching >= 85%
        STRAT->>KAT: Analyze new_resume vs job_desc
        KAT-->>STRAT: Matching score (e.g., 72%)
        alt Score < 85%
            STRAT->>LLM: Refine resume with missing keywords
            LLM-->>STRAT: Resume draft v(n+1)
        else Score >= 85%
            STRAT->>STRAT: Exit loop
        end
    end
    
    STRAT->>FS: Write new_resume.md
    STRAT->>User: Request human feedback
    User->>STRAT: Approve/Edit
    STRAT-->>JAC: Return final resume + analysis
    
    JAC->>FS: Write application_state.json
    JAC-->>CLI: Return state
    CLI-->>User: ✅ Done. Output in docs/
```

---

### Motivation Letter Generation Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI as gen_motivation.py
    participant MLC as MotivationLetterCrew
    participant PM as Project Manager
    participant MLE as Motivation Letter Editor
    participant SWT as ScrapeWebsiteTool
    participant FRT as FileReadTool
    participant LLM as LLM Provider
    participant FS as File System
    
    User->>CLI: Execute with --company_url & --job_posting_url
    CLI->>CLI: Validate doc_path exists
    CLI->>MLC: Initialize crew(doc_path, company_url)
    CLI->>MLC: kickoff({company_url, job_posting_url})
    
    MLC->>PM: Delegate: generate_motivation_letter
    PM->>MLE: Task: generate_motivation_letter
    
    MLE->>SWT: Scrape company_url
    SWT-->>MLE: Company info (mission, values, news)
    
    alt Job posting URL provided
        MLE->>SWT: Scrape job_posting_url
        SWT-->>MLE: Job posting content
    else Use local file
        MLE->>FRT: Read job_advertise.md
        FRT-->>MLE: Job posting content
    end
    
    MLE->>FRT: Read new_resume.md
    FRT-->>MLE: Candidate background
    
    MLE->>LLM: Synthesize motivation letter
    Note over MLE,LLM: Map company values to<br/>candidate experiences
    LLM-->>MLE: Motivation letter draft
    
    MLE->>FS: Write motivation_letter.md via FileWriterTool
    MLE->>User: Request human feedback
    User->>MLE: Approve/Edit
    MLE-->>PM: Task complete
    
    PM-->>MLC: Workflow complete
    MLC->>FS: Write application_state.json
    MLC-->>CLI: Return state
    CLI-->>User: ✅ Done. Output in docs/
```

---

### Keyword Analysis Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI as analyze.py
    participant KAT as KeywordsAnalyzerTool
    participant NLP as spaCy/NLTK
    participant ML as scikit-learn
    
    User->>CLI: Execute with --resume & --job_desc
    CLI->>CLI: Read resume file (UTF-8)
    CLI->>CLI: Read job_desc file (UTF-8)
    CLI->>KAT: _run(resume_text, job_desc_text)
    
    KAT->>NLP: Extract keywords from job_desc
    NLP->>NLP: Tokenize, POS tag, filter stopwords
    NLP-->>KAT: job_desc_keywords[]
    
    KAT->>NLP: Extract keywords from resume
    NLP->>NLP: Tokenize, POS tag, filter stopwords
    NLP-->>KAT: resume_keywords[]
    
    KAT->>KAT: Match keywords
    loop For each job_desc keyword
        alt Keyword in resume
            KAT->>KAT: Mark as "Match"
        else Keyword not in resume
            KAT->>KAT: Mark as "No Match"
        end
    end
    
    KAT->>KAT: Calculate match percentage
    Note over KAT: (matched_count / total_jd_keywords) * 100
    
    KAT->>ML: Calculate cosine similarity
    ML->>ML: Vectorize texts (CountVectorizer)
    ML->>ML: Compute cosine_similarity(vectors)
    ML-->>KAT: Similarity score (0-1)
    
    KAT->>KAT: Format output table (tabulate)
    KAT-->>CLI: Return analysis results
    CLI-->>User: Print table + statistics to console
```

---

## Data Flow

### Input Files
- **Resume**: Markdown, TXT, or PDF (candidate's original resume)
- **Job Description**: Markdown or plain text (target job posting)
- **Company URL**: Public website for motivation letter research

### Output Files
- **new_resume.md**: Tailored resume optimized for ATS (85%+ matching)
- **motivation_letter.md**: Personalized cover letter aligned with company values
- **application_state.json**: Complete audit trail of agent interactions and decisions

### State Management
```json
{
  "tasks_outputs": [
    {
      "task": "extract_job_requirements",
      "agent": "researcher",
      "output": "...",
      "raw": "..."
    },
    {
      "task": "tailor_resume",
      "agent": "resume_strategist",
      "output": "...",
      "raw": "..."
    }
  ],
  "metadata": {
    "timestamp": "...",
    "model_used": "..."
  }
}
```

---

## Key Design Patterns

### 1. Multi-Agent Orchestration
- **Pattern**: Agent-based workflow with specialized roles
- **Implementation**: CrewAI framework with YAML-driven configuration
- **Benefits**: Separation of concerns, parallel processing capabilities

### 2. Iterative Refinement
- **Pattern**: Feedback loop with quality gates
- **Threshold**: 85% ATS matching score
- **Mechanism**: KeywordsAnalyzerTool provides objective metrics for iteration decision

### 3. Human-in-the-Loop
- **Checkpoints**: After resume generation and motivation letter drafting
- **Purpose**: Quality assurance, tone adjustment, accuracy verification
- **Implementation**: `human_input: true` in task configuration

### 4. Tool-Based Architecture
- **Pattern**: Composable tools injected into agents
- **Caching**: Lambda-based caching for expensive operations (web scraping, searches)
- **Extensibility**: New tools can be added without modifying agent logic

---

## Configuration

### Environment Variables
```bash
# Required
LLM_PROVIDER=openai              # openai | anthropic | gemini
OPENAI_API_KEY=sk-...           # Provider-specific API key

# Optional
LANGTRACE_API_KEY=...           # For detailed tracing
MODEL_NAME=gpt-4.1-2025-04-14   # Override default model
```

### YAML Configuration
- **agents.yaml**: Defines agent roles, goals, backstories, max iterations
- **tasks.yaml**: Defines task descriptions, expected outputs, file paths, human input flags

---

## Performance Characteristics

### Iteration Limits
- Researcher: Max 50 iterations
- Resume Strategist: Max 60 iterations  
- Motivation Letter Editor: Max 70 iterations

### Caching Strategy
- Web scraping results cached via lambda function
- Search results cached to reduce API calls
- File reads not cached (to ensure fresh data)

### Quality Gates
- **ATS Score**: ≥ 85% keyword matching and cosine similarity
- **Verification**: KeywordsAnalyzerTool run after each resume draft
- **Audit**: Complete state logged to `application_state.json`

---

## Technology Stack

| Layer | Technologies |
|-------|-------------|
| **Orchestration** | CrewAI, Python 3.11+ |
| **LLM Integration** | OpenAI, Anthropic, Gemini APIs |
| **NLP/ML** | spaCy, NLTK, scikit-learn |
| **Tools** | crewai-tools (file I/O, web scraping, search) |
| **Observability** | LangTrace SDK |
| **Configuration** | YAML, environment variables |
| **Data Formats** | Markdown, JSON, TXT, PDF |

---

## Extension Points

### Adding New LLM Providers
1. Add model name to `_default_models` dict in crew files
2. Set `LLM_PROVIDER` and corresponding API key
3. No code changes required

### Adding New Tools
1. Create tool class extending `BaseTool` from CrewAI
2. Implement `_run()` method
3. Inject into agent via `tools=[...]` parameter

### Adding New Agents
1. Define agent in `agents.yaml` (role, goal, backstory)
2. Create `@agent` method in crew class
3. Reference in task assignments

### Adding New Tasks
1. Define task in `tasks.yaml` (description, expected_output, agent)
2. Create `@task` method in crew class
3. Add to crew task sequence

---

## Security Considerations

- **API Keys**: Stored in environment variables (never hardcoded)
- **File Access**: Limited to specified paths (no arbitrary file access)
- **Web Scraping**: Respects public data only (no authentication bypass)
- **Data Privacy**: Resume data processed locally, only LLM calls external
- **Output Sanitization**: Human review before submission

---

## Future Enhancements

1. **Native PDF/DOCX Parsing**: Direct support for binary resume formats
2. **Parallel Workflows**: Run keyword extraction and tailoring concurrently
3. **Dashboard**: Web UI for visualizing `application_state.json` over time
4. **Enhanced Analysis**: Word clouds, trend charts for keyword frequencies
5. **Sentiment Analysis**: Tone optimization for motivation letters
6. **A/B Testing**: Multiple resume variants with comparative ATS scoring
