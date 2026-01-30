#!/usr/bin/env python3
"""
Generate PDF resume from HTML using WeasyPrint.

This script converts the HTML resume to PDF format. It requires WeasyPrint
and its dependencies (GTK/Pango libraries), which are available on Linux
but require additional setup on Windows.

Usage:
    python generate_pdf.py          # Generate full resume
    python generate_pdf.py --brief   # Generate brief resume
"""

import argparse
from pathlib import Path

from common import (
    # Data loading
    load_resume_data,
    # Output functions
    get_output_path,
    ensure_output_dir,
    write_binary_file,
)

# Import the HTML generator since PDF is built from HTML
from generate_html import generate_resume as generate_html_resume


#───────────────────────────────────────────────────────────────────────────────
# WeasyPrint Availability Check
#───────────────────────────────────────────────────────────────────────────────

# Try to import WeasyPrint. This may fail on Windows without GTK libraries
# installed. We handle this gracefully so the script can still be imported
# even when WeasyPrint isn't available.
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
    WEASYPRINT_ERROR = None
except OSError as e:
    WEASYPRINT_AVAILABLE = False
    WEASYPRINT_ERROR = str(e)


#───────────────────────────────────────────────────────────────────────────────
# Resume Generation
#───────────────────────────────────────────────────────────────────────────────


def generate_resume(html_content: str) -> bytes:
    """
    Generate PDF content from HTML using WeasyPrint.

    Args:
        html_content: The HTML resume content to convert

    Returns:
        PDF content as bytes

    Raises:
        RuntimeError: If WeasyPrint is not available
    """
    if not WEASYPRINT_AVAILABLE:
        raise RuntimeError(
            "WeasyPrint is not available. "
            "On Windows, GTK libraries are required. "
            f"Original error: {WEASYPRINT_ERROR}"
        )

    # Convert HTML string to PDF bytes
    html_doc = HTML(string=html_content)
    return html_doc.write_pdf()


def write_resume(content: bytes, name: str, is_brief: bool = False) -> Path:
    """
    Write the generated resume to a PDF file.

    Args:
        content: The PDF content to write (as bytes)
        name: Person's name (used for filename)
        is_brief: Whether this is the brief version

    Returns:
        Path to the written file
    """
    output_path = get_output_path(name, "pdf", is_brief)
    write_binary_file(output_path, content)
    return output_path


#───────────────────────────────────────────────────────────────────────────────
# Main Entry Point
#───────────────────────────────────────────────────────────────────────────────


def main(is_brief: bool = False) -> None:
    """
    Generate a PDF resume.

    Args:
        is_brief: If True, generate the brief version; otherwise generate full
    """
    # Skip if WeasyPrint is not available
    if not WEASYPRINT_AVAILABLE:
        print("  Skipping PDF generation: WeasyPrint not available")
        print("  (GTK libraries required - install on Linux or use MSYS2 on Windows)")
        return

    # Ensure output directory exists
    ensure_output_dir()

    # Load resume data from YAML
    data = load_resume_data()
    name = data["personal"]["name"]

    # Generate the resume (HTML -> PDF)
    html_content = generate_html_resume(data, is_brief=is_brief)
    pdf_content = generate_resume(html_content)
    output_path = write_resume(pdf_content, name, is_brief=is_brief)
    print(f"  Created: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate PDF resume")
    parser.add_argument(
        "--brief",
        action="store_true",
        help="Generate brief version (recent experience only)",
    )
    args = parser.parse_args()
    main(is_brief=args.brief)
