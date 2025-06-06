#!/usr/bin/env python3
import argparse
from pathlib import Path

# Adjust this import to match wherever you put your KeywordsAnalyzerTool class.
# For example, if you saved the code above into a file named "keywords_analyzer_tool.py",
# then this line should be:
#
#     from keywords_analyzer_tool import KeywordsAnalyzerTool
#
# If it’s in the same file, you can simply do:
#     from <filename> import KeywordsAnalyzerTool
#
from tools.keywords_analyzer_tool import KeywordsAnalyzerTool


def main():
    parser = argparse.ArgumentParser(description="Test KeywordsAnalyzerTool")
    parser.add_argument(
        "--resume",
        type=Path,
        required=True,
        help="Path to the resume file (plain text)."
    )
    parser.add_argument(
        "--job_desc",
        type=Path,
        required=True,
        help="Path to the job description file (plain text)."
    )
    args = parser.parse_args()

    # Read the contents of each file as UTF-8 text
    try:
        resume_text = args.resume.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading resume file '{args.resume}': {e}")
        return

    try:
        jd_text = args.job_desc.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading job description file '{args.job_desc}': {e}")
        return

    # Instantiate the tool and run it
    tool = KeywordsAnalyzerTool()
    result = tool._run(resume=resume_text, job_description=jd_text)

    # Print the output
    print(result)


if __name__ == "__main__":
    main()
