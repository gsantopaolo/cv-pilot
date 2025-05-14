#!/usr/bin/env python3
import sys
import os
import json
import logging
import argparse
from langtrace_python_sdk import langtrace

from crews.motivation_letter.motivation_letter_crew import MotivationLetterCrew

# Initialize LangTrace
langtrace.init(api_key=os.getenv("LANGTRACE_API_KEY"))

# Default docs directory
DOC_PATH = "docs"
DEFAULT_JOB_POSTING_URL = "N/A"
DEFAULT_JOB_POSTING_FILE = "job_advertise.md"

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force = True
)
logger = logging.getLogger(__name__)

def main():
    # # Pick up doc_path from argv if provided, otherwise use default
    # if len(sys.argv) > 1:
    #     doc_path = sys.argv[1]
    # else:
    #     doc_path = DOC_PATH

    parser = argparse.ArgumentParser(
        description="Generate a tailored motivation letter"
    )
    parser.add_argument(
        "--company_url",
        required=True,
        help="Public URL of the company (fills {company_url})"
    )
    parser.add_argument(
        "--job_posting_url",
        # required=True,
        default=DEFAULT_JOB_POSTING_URL,
        help="URL of the job posting (fills {job_posting_url})"
    )
    parser.add_argument(
        "--doc_path",
        default=DOC_PATH,
        help="Directory to write output files"
    )
    args = parser.parse_args()

    # Convert doc_path to absolute path
    doc_path = os.path.abspath(args.doc_path)

    # Ensure the directory exists
    if not os.path.exists(doc_path):
        logger.error(f"❌ Doc path {doc_path} does not exist.")
        raise FileNotFoundError(f"❌ Doc path `{doc_path}` does not exist.")

    # Ensure the job posting is provided or job_advertise.md exists
    if not os.path.exists(os.path.join(doc_path, DEFAULT_JOB_POSTING_FILE) and args.job_posting_url == DEFAULT_JOB_POSTING_URL):
        error_message = (f"❌ Job posting URL not provided and {DEFAULT_JOB_POSTING_URL} does not exists \n "
                         f"You need to pass a job advertise url or save it in the doc folder")
        logger.error(error_message)
        raise FileNotFoundError(error_message)

    logger.info(f"📄 Docs path: {doc_path}")
    logger.info(f"📄 Job advertise: {args.job_posting_url}")
    logger.info(f"📄 Company URL: {args.job_posting_url}")

    llm = os.getenv("LLM_PROVIDER", "").upper()
    logger.info("🧠 GenAI provider in use: %s", llm or "not set")

    try:
        # Initialize and run the crew
        crew = MotivationLetterCrew(doc_path, args.company_url).crew()
        state = crew.kickoff(
                inputs={
                "company_url": args.company_url,
                "job_posting_url": args.job_posting_url
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
