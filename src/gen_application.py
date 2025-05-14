#!/usr/bin/env python3
import sys
import os
import json
import logging
from langtrace_python_sdk import langtrace

from crews.job_application.job_application_crew import JobApplicationCrew

# Initialize LangTrace
langtrace.init(api_key=os.getenv("LANGTRACE_API_KEY"))

# Default docs directory
DOC_PATH = "docs"

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force = True
)
logger = logging.getLogger(__name__)

def main():
    # Pick up doc_path from argv if provided, otherwise use default
    if len(sys.argv) > 1:
        doc_path = sys.argv[1]
    else:
        doc_path = DOC_PATH

    # Convert doc_path to absolute path
    doc_path = os.path.abspath(doc_path)

    # Ensure the directory exists
    if not os.path.exists(doc_path):
        logger.error("❌ Doc path `%s` does not exist.", doc_path)
        raise FileNotFoundError(f"Doc path `{doc_path}` does not exist.")

    logger.info("📄 Docs path: %s", doc_path)

    llm = os.getenv("LLM_PROVIDER", "").upper()
    logger.info("🧠 GenAI provider in use: %s", llm or "not set")

    try:
        # Initialize and run the crew
        crew = JobApplicationCrew(doc_path).crew()
        state = crew.kickoff({
            "doc_path": os.path.abspath(doc_path),
        })

        # Write out the application state
        out_file = os.path.join(doc_path, "application_state.json")
        with open(out_file, "w") as f:
            json.dump(
                state.model_dump() if hasattr(state, "model_dump") else dict(state),
                f,
                indent=2
            )

        logger.info("✅ Done. Docs in `%s`.", doc_path)
    except Exception as e:
        logger.exception("💥 An unexpected error occurred:")
        sys.exit(1)

if __name__ == "__main__":
    main()
