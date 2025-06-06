````markdown
🚀 **CV-Pilot**

Have you ever felt the sting of sending out dozens of applications only to hear crickets? 😖 You polish your resume, click “Send,” and… nothing. No calls. No next steps. Frustrating, right? Ever wondered why some people seem to get straight to the first HR screening while others don’t even get a glance? The answer often lies in **automated resume processing**—the infamous Applicant Tracking Systems (ATS) that parse your CV for keywords before a human even sees it. If your resume doesn’t speak ATS’s language, it might never make it to a recruiter’s desk. 😱

**CV-Pilot** swoops in to solve this problem. It reads your raw resume 📄, compares it against a job advertisement 📋, and crafts a **tailored CV** that maximizes your chances of passing the ATS hurdle and landing that coveted first interview. 🎯✨

---

## 📋 Table of Contents

* [✨ Why CV-Pilot?](#✨-why-cv-pilot)
* [🌟 Features](#🌟-features)
* [🔧 Requirements](#🔧-requirements)
* [🚀 Installation](#🚀-installation)
* [🎬 Usage](#🎬-usage)
  * [1. Generate a Tailored Resume (`gen_application.py`)](#1-generate-a-tailored-resume-gen_applicationpy)
  * [2. Generate a Motivation Letter (`gen_motivation.py`)](#2-generate-a-motivation-letter-gen_motivationpy)
  * [3. Analyze Keyword Matching & Similarity (`analyze.py`)](#3-analyze-keyword-matching--similarity-analyzepy)
* [🔄 Process Overview](#🔄-process-overview)
* [📝 Human-in-the-Loop Feedback](#📝-human-in-the-loop-feedback)
* [⚠️ Known Issues & Troubleshooting](#⚠️-known-issues--troubleshooting)
* [🚧 Next Steps](#🚧-next-steps)
* [📚 References](#📚-references)

---

## ✨ Why CV-Pilot?

😩 Tired of hearing nothing back? CV-Pilot is here to change your luck.  
ATS software scans resumes for relevancy: keywords, skills, experiences. If your resume doesn’t align perfectly with the job description, it’s filtered out—long before a human sets eyes on it. 😤 CV-Pilot **automates** this alignment:

1. **Reads** your raw resume (Markdown, TXT, or PDF).  
2. **Parses** the job advertisement (Markdown or URL).  
3. **Extracts** the crucial keywords and requirements.  
4. **Generates** a new, ATS-friendly resume that highlights your expertise and matches the job’s language.

Result? Your resume has a much higher probability of making it past the bots and into the hands of a recruiter. 🚀🎉

---

## 🌟 Features

* **Automated Resume Tailoring**  
  - **Script**: `gen_application.py`  
  - Reads your raw CV and the job description.  
  - Uses a multi-agent Crew AI workflow to extract keywords, match your skills/experiences, and draft a job-specific CV.  
  - Outputs:  
    - `docs/new_resume.md` (tailored resume)  
    - `docs/application_state.json` (audit trail of every step)  

* **Personalized Motivation Letter**  
  - **Script**: `gen_motivation.py`  
  - Scrapes the target company’s website for mission, values, culture.  
  - Reads the job posting (Markdown file or URL).  
  - Drafts a structured cover letter: introduction, body, conclusion.  
  - Outputs:  
    - `docs/motivation_letter.md` (tailored motivation letter)  
    - Updates `docs/application_state.json` (appends new state)  

* **Keyword Matching & Similarity Analysis**  
  - **Script**: `analyze.py`  
  - Compares your resume and the job description.  
  - Computes:  
    - Word-matching statistics (frequency of key terms).  
    - Cosine similarity score (0–1) to quantify document overlap.  
  - Outputs results to stdout (JSON-like format).  

* **Traceability & Audit Trail**  
  - Every run produces `docs/application_state.json`, capturing:  
    - Inputs (resume text, job ad text)  
    - Intermediate LLM calls (keyword extraction, drafting)  
    - Final outputs  

* **Human-in-the-Loop Checkpoints**  
  - After generating each draft (CV or motivation letter), CV-Pilot pauses so you can:  
    - Review AI suggestions.  
    - Edit for tone, clarity, or additional examples.  

---

## 🔧 Requirements

1. **Python ≥ 3.11.7** 🐍  
2. **Crew AI & Tools**  
   - `crewai`, `crewai-tools` (provides `JobApplicationCrew`, `MotivationLetterCrew`)  
3. **Langtrace SDK** (optional) 🔍  
   - `langtrace-python-sdk` (for detailed tracing)  
4. **LLM Provider** (e.g., OpenAI, Anthropic)  
   - Environment variable `LLM_PROVIDER` (e.g., `"openai"`, `"anthropic"`)  
   - Corresponding API key set in environment (e.g., `OPENAI_API_KEY`)  
5. **Network Access** 🌐  
   - Required for scraping public company websites and remote job postings  

---

## 🚀 Installation

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/gsantopaolo/cv-pilot.git
   cd cv-pilot
````

2. **Create & Activate a Virtual Environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**

   ```bash
   export LANGTRACE_API_KEY="your_langtrace_key"       # Optional, for tracing
   export LLM_PROVIDER="openai"                        # Or "anthropic", etc.
   export OPENAI_API_KEY="your_openai_key"             # If using OpenAI
   # If using Anthropic:
   # export ANTHROPIC_API_KEY="your_anthropic_key"
   ```

   * Make sure these variables are set before running any scripts.
   * If you skip `LANGTRACE_API_KEY`, tracing is disabled but functionality remains.

---

## 🎬 Usage

Before running, prepare:

* A **raw resume** file (e.g., `dcos/fake_resume.md`).
* A **job description** file (e.g., `docs/job_advertise.md`).
* For the motivation letter, a **company URL** and/or local job ad file.

Below are examples using our sample files:

* **Resume**: `dcos/fake_resume.md`
* **Job Ad**: `docs/job_advertise.md`

You can replace these with your own files or URLs.

---

### 1. Generate a Tailored Resume (`gen_application.py`)

This pipeline runs a `JobApplicationCrew` that:

1. **Loads** and parses your **raw resume**.
2. **Loads** and parses the **job description**.
3. **Extracts** keywords and matches your skills/achievements.
4. **Drafts** a tailored resume (`docs/new_resume.md`).
5. **Writes** an audit trail (`docs/application_state.json`).

**Example Command**

```bash
python3 src/gen_application.py \
  --resume dcos/fake_resume.md \
  --job_desc docs/job_advertise.md
```

* **Arguments**:

  * `--resume   <path>` : Path to your raw resume (Markdown, TXT, or PDF).
  * `--job_desc <path>` : Path to the job description file (plain text or Markdown).

* **Outputs** (in `docs/`):

  * `new_resume.md` : Your new, tailored resume.
  * `application_state.json` : Detailed JSON state capturing all steps.

👉 **Tip**: After running, open `docs/new_resume.md`, review AI edits, and tweak as needed. Then inspect `docs/application_state.json` to see how each piece was generated.

---

### 2. Generate a Motivation Letter (`gen_motivation.py`)

This pipeline runs a `MotivationLetterCrew` that:

1. **Scrapes** your **company’s URL** for mission, values, and culture.
2. **Reads** the **job posting** (via a local Markdown file or remote URL).
3. **Drafts** a 3-section motivation letter (`docs/motivation_letter.md`).
4. **Appends** to `docs/application_state.json`.

**Example Command (using local job ad)**

```bash
python3 src/gen_motivation.py \
  --company_url "https://example-company.com" \
  --doc_path docs
```

**Example Command (using remote job URL)**

```bash
python3 src/gen_motivation.py \
  --company_url "https://example-company.com" \
  --job_posting_url "https://jobs.example.com/12345" \
  --doc_path docs
```

* **Arguments**:

  * `--company_url      <URL>`   : Company website to scrape (HTML).
  * `--job_posting_url  <URL>`   : (Optional) Remote job ad URL.
  * `--doc_path         <dir>`   : Directory for reading/writing files (default `docs/`).

* **Outputs** (in `docs/`):

  * `motivation_letter.md` : AI-drafted cover letter.
  * `application_state.json` : Updated JSON state (appended).

👉 **Tip**: Review `docs/motivation_letter.md` and ensure company details are accurate. Edit tone or examples to match your voice before sending.

---

### 3. Analyze Keyword Matching & Similarity (`analyze.py`)

This tool runs a `KeywordsAnalyzerTool` that:

1. **Loads** your **resume** and **job description**.
2. **Computes** word-matching statistics (how often each key term appears).
3. **Computes** cosine similarity (score between 0 and 1).
4. **Prints** a JSON-like summary to stdout (no files written).

**Example Command**

```bash
python3 src/analyze.py \
  --resume dcos/fake_resume.md \
  --job_desc docs/job_advertise.md
```

* **Arguments**:

  * `--resume   <path>` : Path to resume file (Markdown or plain text).
  * `--job_desc <path>` : Path to job description file (Markdown or plain text).

* **Example Output (stdout)**

  ```json
  {
    "matched_keywords": {
      "python": { "freq_in_resume": 5, "freq_in_job": 3 },
      "docker": { "freq_in_resume": 2, "freq_in_job": 2 },
      ...
    },
    "cosine_similarity": 0.72
  }
  ```

👉 **Tip**: Use this to gauge how well your existing resume aligns. If similarity is low (< 0.5), tailoring is strongly recommended.

---

## 🔄 Process Overview

### 1. Resume Generation (`gen_application.py`)

1. **Load & Parse**

   * Reads your resume (Markdown, TXT, or PDF-to-text).
   * Reads the job description (Markdown or URL scrape).

2. **Keyword Extraction**

   * Identifies required skills, technologies, and responsibilities from the job ad.

3. **Skill Matching & Tailoring**

   * Finds relevant experiences, projects, and accomplishments in your raw CV.
   * Reorders or rephrases bullet points to echo job-ad keywords.

4. **Draft Output**

   * Writes `docs/new_resume.md` (tailored CV).
   * Saves full state in `docs/application_state.json`.

---

### 2. Motivation Letter Generation (`gen_motivation.py`)

1. **Company Research**

   * Scrapes the target company’s homepage for mission/values/culture.

2. **Job Posting Parsing**

   * Reads job ad (local Markdown or remote URL).

3. **Drafting**

   * Generates a structured letter:

     * **Introduction**: Why you’re excited about this company and role.
     * **Body**: Align your most relevant achievements & skills to their needs.
     * **Conclusion**: Call to action and enthusiasm for next steps.

4. **Output**

   * Writes `docs/motivation_letter.md`.
   * Appends new state to `docs/application_state.json`.

---

### 3. Keyword Matching & Similarity Analysis (`analyze.py`)

1. **Load Texts**

   * Reads resume and job description as plain text.

2. **Compute Statistics**

   * Counts occurrences of each required keyword in both docs.

3. **Compute Cosine Similarity**

   * Transforms texts into vector embeddings (TF-IDF or similar).
   * Calculates similarity score (0.0 worst → 1.0 perfect match).

4. **Output**

   * Prints a JSON-like summary for quick review.

---

## 📝 Human-in-the-Loop Feedback

1. **After Resume Generation**

   * Inspect `docs/new_resume.md`.
   * Edit tone, reorder sections, or add missing details.
   * Remove any tags like `<!-- REVIEW: ... -->` once you’re happy.

2. **After Motivation Letter Generation**

   * Check `docs/motivation_letter.md`.
   * Ensure company research snippets are accurate.
   * Personalize any placeholders (e.g., recruiter name, specific metrics).

---

## ⚠️ Known Issues & Troubleshooting

* **File Paths & Naming**

  * Ensure `dcos/fake_resume.md` and `docs/job_advertise.md` exist, or update `--resume` / `--job_desc` flags.
  * If `docs/` or `dcos/` doesn’t exist, create them or pass correct paths.

* **Environment Variables**

  * ❌ Missing `LLM_PROVIDER`:

    ```bash
    export LLM_PROVIDER="openai"
    ```
  * ❌ Missing API key:

    ```bash
    export OPENAI_API_KEY="your_key_here"
    ```

* **Scraping Blocks**

  * If `gen_motivation.py` fails when scraping, the website might be blocking bots. Provide a local `docs/job_advertise.md` instead of a URL, or use a different URL.

* **Inconsistent AI Outputs**

  * AI drafts may vary each run. Pin your model version:

    ```bash
    export OPENAI_MODEL="gpt-4-0613"
    ```

* **PDF Resumes**

  * If you pass a PDF and see parsing errors, convert to Markdown or plain text first (e.g., `pdftotext resume.pdf resume.txt`).

* **Large `application_state.json`**

  * This file grows with each run. If it becomes unwieldy, delete or archive it before re-running for a fresh start.

---

## 🚧 Next Steps

* **Support Additional Resume Formats**

  * Add native `.pdf`/`.docx` parsing in `gen_application.py` so you can pass PDFs directly.
* **Parallelize Crew Workflows**

  * Speed up multi-agent tasks by running keyword extraction and tailoring in parallel.
* **Enhanced Analysis**

  * In `analyze.py`, generate a bar chart of keyword frequencies or a word cloud.
* **Dashboard & Visualization**

  * Build a simple web dashboard (React or Streamlit) to visualize `application_state.json` over multiple applications.
* **Integrate Tone/Sentiment Analysis**

  * Add a step in `gen_motivation.py` to analyze sentiment/tone, ensuring your cover letter feels warm and genuine.

---

✨ **Happy job hunting!** ✨


