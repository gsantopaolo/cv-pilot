🚀 **CV-Pilot**

CV-Pilot is an AI-powered toolkit composed of two distinct pipelines—**gen\_resume** and 
**gen\_motivation**—that automate the creation of a tailored CV and a personalized motivation letter. 
Each pipeline runs independently: first, **gen\_resume** analyzes your raw resume and the 
job posting to produce a data-driven CV; then, **gen\_motivation** scrapes company 
information and structures a compelling cover letter. 
Human-in-the-loop checkpoints ensure accuracy and alignment at every stage. ✨🤖

---

## 📋 Table of Contents

* [✨ Features](#✨-features)
* [🔧 Requirements](#🔧-requirements)
* [🚀 Installation](#🚀-installation)
* [🎬 Usage](#🎬-usage)
* [🔄 Process Overview](#🔄-process-overview)
* [📝 Human-in-the-Loop Feedback](#📝-human-in-the-loop-feedback)
* [⚠️ Known Issues & Troubleshooting](#⚠️-known-issues--troubleshooting)
* [🚧 Next Steps](#🚧-next-steps)
* [📚 References](#📚-references)

---

## ✨ Features

* **Separate Pipelines**:

  * **gen\_resume** crafts a tailored CV based on your raw resume and job specifications. 📄
  * **gen\_motivation** generates a personalized motivation letter using company and posting details. ✉️
* **Automated Research**: Scrapes company website and parses job postings (URL or `job_advertise.md`). 🌐🔍
* **Agentic Orchestration**: Multi-agent workflows in each pipeline handle extraction, profiling, drafting, and tailoring. 🤖
* **Traceability**: Produces `application_state.json` with full audit trail of sources, inputs, and outputs. 📑
* **Human Checkpoints**: Pauses for your review after each pipeline completes its draft. 👥
* **File Outputs**:

  * **gen\_resume** → `docs/new_resume.md`
  * **gen\_motivation** → `docs/motivation_letter.md`
  * Both pipelines → `docs/application_state.json`

---

## 🔧 Requirements

1. **Python** ≥3.11.7 🐍
2. **Crew AI & Tools**

   * `crewai`, `crewai-tools`
3. **Langtrace SDK** (optional) for tracing 🔍
4. **LLM Provider** (e.g., OpenAI, Anthropic)

   * Set `LLM_PROVIDER` and provider API key env vars
5. **Network Access** for scraping & API calls 🌐

---

## 🚀 Installation

1. **Clone the Repo**

   ```bash
   git clone https://github.com/your-org/cv-pilot.git
   cd cv-pilot
   ```
2. **Create & Activate Python Env**

   ```bash
# Create a Conda environment named "cv-pilot" with Python 3.9
conda create --name cv-pilot python=3.9 -y 

# Activate the environment
conda activate cv-pilot 

# Install dependencies from requirements.txt
pip install -r requirements.txt 

   ```
3. **Configure Environment**

   ```bash
   export LANGTRACE_API_KEY="your_langtrace_key"
   export LLM_PROVIDER="openai"
   export OPENAI_API_KEY="your_openai_key"
   ```

---

## 🎬 Usage

1. **Prepare Your `docs/` Folder**

   * Place your resume as `cv_.md`.
   * (Optional) Place the job ad as `job_advertise.md` if not using a URL.
2. **Run the Resume Pipeline**

   ```bash
   python3 gen_resume.py --doc_path ./docs \
     [--job_posting_url "https://jobs.example.com/123"]
   ```

   *Generates `docs/new_resume.md` & updates `application_state.json`.*
3. **Review & Approve CV**
   *Edit and confirm your tailored CV before proceeding.*
4. **Run the Motivation Pipeline**

   ```bash
   python3 gen_motivation.py \
     --company_url "https://example.com" \
     --job_posting_url "https://jobs.example.com/123" \
     --doc_path ./docs
   ```

   *Generates `docs/motivation_letter.md` & updates `application_state.json`.*
5. **Final Review**
   *Inspect and refine your motivation letter.*

---

## 🔄 Process Overview

### 1. Resume Generation (`gen_resume.py`)

* **Extraction**: Gleans requirements from job posting.
* **Profiling**: Matches your skills, achievements, and keywords.
* **Tailoring**: Produces `new_resume.md`.

### 2. Motivation Letter Generation (`gen_motivation.py`)

* **Research**: Scrapes company site for mission, values, culture.
* **Parsing**: Reads job ad (URL or Markdown).
* **Drafting**: Writes intro, body, conclusion in `motivation_letter.md`.

---

## 📝 Human-in-the-Loop Feedback

* **Step 1**: After `gen_resume`, review and edit `new_resume.md`.
* **Step 2**: After `gen_motivation`, review and edit `motivation_letter.md`.
* **Feedback Tags**: Inline prompts (e.g., `<!-- REVIEW: ... -->`) guide your edits.

---

## ⚠️ Known Issues & Troubleshooting

* **Filename Sensitivity**: Ensure `job_advertise.md` matches exactly or supply `--job_posting_url`.
* **API Rate Limits**: Monitor usage to avoid LLM throttling.
* **Scraping Blocks**: If company site blocks bots, provide a direct job posting URL.
* **Inconsistent Outputs**: Pin `MODEL_NAME` env var for stable results.
* **Cleanup**: Manually delete temporary files if needed.

---

## 🚧 Next Steps

* Support PDF/DOCX resume inputs for `gen_resume`.
* Parallelize agent tasks within each pipeline for faster runs.
* Integrate sentiment/tone analysis in motivation drafts.
* Add a dashboard to visualize pipeline progress and state.

---

## 📚 References

* [Crew AI Documentation](https://docs.crewai.ai)
* [Langtrace Python SDK](https://github.com/langtrace/langtrace-python)
* [Agentic Workflow Patterns](https://crewai.ai/blog/agentic-workflows)


---
