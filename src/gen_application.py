#!/usr/bin/env python3
import sys
import os
import json
import logging
import argparse
from pathlib import Path
from crews.job_application.job_application_crew import JobApplicationCrew
import sys, os, shutil, subprocess, json
from langtrace_python_sdk import langtrace
langtrace.init(api_key = os.getenv("LANGTRACE_API_KEY"))

# Default output directory to write CrewAI state
OUTPUT_DIR = "docs/"

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Run the JobApplicationCrew with a resume and job description.")
    parser.add_argument(
        "--resume",
        type=Path,
        required=True,
        help="Path to the resume file (plain text or PDF)."
    )
    parser.add_argument(
        "--job_desc",
        type=Path,
        required=True,
        help="Path to the job description file (plain text)."
    )
    args = parser.parse_args()

    # Resolve to absolute paths
    resume_path = args.resume.expanduser().resolve()
    job_desc_path = args.job_desc.expanduser().resolve()

    # Verify that both files exist
    if not resume_path.exists():
        logger.error("❌ Resume file `%s` does not exist.", resume_path)
        raise FileNotFoundError(f"Resume file `{resume_path}` does not exist.")
    if not job_desc_path.exists():
        logger.error("❌ Job description file `%s` does not exist.", job_desc_path)
        raise FileNotFoundError(f"Job description file `{job_desc_path}` does not exist.")

    logger.info("📄 Resume path: %s", resume_path)
    logger.info("📄 Job description path: %s", job_desc_path)

    # Ensure an LLM provider is set, and that its API key is present
    llm = os.getenv("LLM_PROVIDER", "").upper().strip()
    if not llm:
        logger.error(
            "❌ LLM_PROVIDER is not set. You must set an LLM provider in the environment, e.g. export LLM_PROVIDER=openai, "
            "and also set the corresponding API key (e.g. export OPENAI_API_KEY=...)."
        )
        raise EnvironmentError(
            "LLM_PROVIDER must be set in the environment — for example, `export LLM_PROVIDER=openai` — "
            "and you must also export the matching API key (e.g. `export OPENAI_API_KEY=<your_key>`)."
        )

    api_key_env = f"{llm}_API_KEY"
    api_key = os.getenv(api_key_env, "").strip()
    if not api_key:
        logger.error(
            "❌ API key for `%s` is not set. Please export `%s` in your environment.",
            llm, api_key_env
        )
        raise EnvironmentError(
            f"The environment variable `{api_key_env}` is not set. You must export your {llm} API key, "
            f"for example: `export {api_key_env}=<your_api_key>`."
        )

    logger.info("🧠 GenAI provider in use: %s", llm)

    out_dir = Path(OUTPUT_DIR).expanduser().resolve()
    if not out_dir.exists():
        out_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Initialize and run the crew, passing both resume and job description
        crew = JobApplicationCrew(resume_path, job_desc_path).crew()
        state = crew.kickoff({
            "resume_path": str(resume_path),
            "job_desc_path": str(job_desc_path),
        })

        # Write out the application state
        out_file = out_dir / "application_state.json"
        with open(out_file, "w") as f:
            json.dump(
                state.model_dump() if hasattr(state, "model_dump") else dict(state),
                f,
                indent=2
            )

        logger.info("✅ Done. Application state written to `%s`.", out_file)
    except Exception:
        logger.exception("💥 An unexpected error occurred:")
        sys.exit(1)

if __name__ == "__main__":
    main()
