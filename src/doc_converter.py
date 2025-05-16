#!/usr/bin/env python3
"""
doc_converter.py

Convert various document formats into multiple output formats using Docling.
Supports PDF, DOCX, HTML, Markdown, CSV, and image inputs; exports to MD, HTML, JSON, text, or doctags.
Added optional SmolDocling support via --smol flag.
"""

import argparse
import sys
import logging
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    VlmPipelineOptions,
    smoldocling_vlm_mlx_conversion_options
)
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    WordFormatOption,
    HTMLFormatOption,
    MarkdownFormatOption,
    CsvFormatOption,
    ImageFormatOption
)
from docling.pipeline.base_pipeline import PaginatedPipeline
from docling.pipeline.vlm_pipeline import VlmPipeline

# ── ASCII Logo ─────────────────────────────────────────────────────────────────
ASCII_LOGO = r"""
  ____            __  __ _           _       _
 / ___| ___ _ __ |  \/  (_)_ __   __| |  ___| |__
| |  _ / _ \ '_ \| |\/| | | '_ \ / _` | / __| '_ \
| |_| |  __/ | | | |  | | | | | | (_| || (__| | | |
 \____|\___|_| |_|_|  |_|_|_| |_|\__,_(_)___|_| |_|
"""

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def print_logo():
    """Print the ASCII logo to stdout."""
    print(ASCII_LOGO)


def convert_document(source, output, fmt, do_ocr=False, do_table_structure=False, use_smol=False):
    """
    Use Docling to convert various document types to desired output format.
    If use_smol is True, uses SmolDocling VLM for PDF OCR and layout extraction.
    Returns the serialized string for the chosen format.
    """
    logger.info(
        "🔧 Preparing conversion: %s ➡️ %s (format: %s, OCR: %s, Table: %s, Smol: %s)",
        source, output, fmt, do_ocr, do_table_structure, use_smol
    )

    # Build format_options for supported inputs
    pdf_opts = PdfPipelineOptions(do_ocr=do_ocr, do_table_structure=do_table_structure)
    format_options = {
        InputFormat.PDF: PdfFormatOption(pipeline_options=pdf_opts),
        InputFormat.DOCX: WordFormatOption(),
        InputFormat.MD: MarkdownFormatOption(),
        InputFormat.HTML: HTMLFormatOption(),
        InputFormat.ASCIIDOC: MarkdownFormatOption(),
        InputFormat.CSV: CsvFormatOption(),
        # Use IMAGE for all image types
        InputFormat.IMAGE: ImageFormatOption(pipeline_options=pdf_opts),
    }
    allowed = list(format_options.keys())

    # If SmolDocling is requested, override PDF pipeline
    if use_smol:
        logger.info("🤖 Activating SmolDocling VLM pipeline for PDF OCR & layout")

        # 1. Build VLM pipeline options from the SmolDocling preset
        #    (MLX version is optimized for Apple Silicon; drop "mlx" if you want the CPU‐only variant)
        pipeline_options = VlmPipelineOptions(
            **smoldocling_vlm_mlx_conversion_options.model_dump()
        )

        # 2. Tell Docling to use VlmPipeline for PDFs and images
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_cls=VlmPipeline,
                    pipeline_options=pipeline_options,
                ),
                InputFormat.IMAGE: PdfFormatOption(
                    pipeline_cls=VlmPipeline,
                    pipeline_options=pipeline_options,
                ),
            }
        )

    # Initialize converter
    converter = DocumentConverter(
        allowed_formats=allowed,
        format_options=format_options
    )

    # Perform conversion
    result = converter.convert(source)
    doc = result.document

    # Serialize document
    if fmt == 'md':
        serialized = doc.export_to_markdown()
    elif fmt == 'html':
        serialized = doc.export_to_html()
    elif fmt == 'json':
        serialized = doc.export_to_json()
    elif fmt == 'text':
        serialized = doc.export_to_text()
    elif fmt == 'doctags':
        serialized = doc.export_to_doctags()
    else:
        raise ValueError(f"Unsupported output format: {fmt}")

    # Write output
    try:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(serialized)
        logger.info("✅ Wrote %s [%s]", output, fmt)
    except Exception as e:
        logger.error("❌ Failed writing output: %s", e)
        raise

    return serialized


def main():
    parser = argparse.ArgumentParser(
        description="Convert docs to MD, HTML, JSON, text, or doctags via Docling (with SmolDocling option)."
    )
    parser.add_argument("source", help="Path or URL to the source document.")
    parser.add_argument("output", help="Output file path (ext dictates format).")
    parser.add_argument(
        "--format", choices=["md","html","json","text","doctags"],
        default="md",
        help="Output format: md, html, json, text, doctags."
    )
    parser.add_argument("--ocr", action="store_true", help="Enable OCR on images/PDFs.")
    parser.add_argument(
        "--table-structure",
        action="store_true",
        help="Recover tables from structured formats."
    )
    parser.add_argument(
        "--smol", action="store_true",
        help="Use SmolDocling VLM for PDF OCR and layout extraction"
    )
    args = parser.parse_args()

    print_logo()
    logger.info("🚀 Starting conversion job")
    try:
        convert_document(
            source=args.source,
            output=args.output,
            fmt=args.format,
            do_ocr=args.ocr,
            do_table_structure=args.table_structure,
            use_smol=args.smol
        )
        logger.info("🎉 Conversion completed successfully.")
    except Exception:
        logger.exception("💥 Conversion failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
