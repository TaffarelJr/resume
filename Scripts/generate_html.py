#!/usr/bin/env python3
"""
Generate static HTML resume with embedded CSS.

This script produces standalone .html files with all CSS embedded inline,
suitable for viewing in any browser without external dependencies.

Usage:
    python generate_html.py          # Generate full resume
    python generate_html.py --brief   # Generate brief resume
"""

import argparse
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from common import (
    # Configuration
    CAREER_START_YEAR,
    TEMPLATES_DIR,
    # Data loading
    load_resume_data,
    load_css,
    # Output functions
    get_output_path,
    ensure_output_dir,
    write_text_file,
    # Formatting functions
    filter_experience_for_brief,
    format_date_range,
    get_badge_color,
)


#───────────────────────────────────────────────────────────────────────────────
# Jinja2 Environment Setup
#───────────────────────────────────────────────────────────────────────────────


def create_jinja_env() -> Environment:
    """
    Create and configure the Jinja2 template environment.

    Returns:
        Configured Jinja2 Environment with custom filters and globals
    """
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html", "xml"]),  # Escape HTML entities
        trim_blocks=True,      # Remove first newline after block tags
        lstrip_blocks=True,    # Strip leading whitespace from block tags
    )

    # Register custom filters (used with | syntax in templates)
    env.filters["format_date_range"] = format_date_range
    env.filters["tech_to_badge"] = tech_to_badge

    return env


#───────────────────────────────────────────────────────────────────────────────
# Helper Methods
#───────────────────────────────────────────────────────────────────────────────


def tech_to_badge(tech: dict) -> str:
    """
    Convert a technology dict to a shields.io badge in HTML format.

    Args:
        tech: Dict with 'item' key and optional 'isPrimary' key

    Returns:
        HTML img tag for the badge
    """
    name = tech.get("item", "")
    is_primary = tech.get("isPrimary", False)

    # Format for shields.io URL (dashes become double-dash, spaces become underscore)
    label = name.replace("-", "--").replace(" ", "_")
    color = get_badge_color(name, is_primary)

    return f'<img src="https://img.shields.io/badge/{label}-{color}" alt="{name}">'


#───────────────────────────────────────────────────────────────────────────────
# Resume Generation
#───────────────────────────────────────────────────────────────────────────────


def generate_resume(data: dict, is_brief: bool = False) -> str:
    """
    Generate HTML resume content from data.

    Args:
        data: Resume data dictionary loaded from YAML
        is_brief: If True, generate shortened version for recent experience only

    Returns:
        HTML resume content as a string
    """
    # Set up template environment
    env = create_jinja_env()
    template = env.get_template("resume.html.jinja2")

    # Filter experience for brief version
    experience = data.get("experience", [])
    if is_brief:
        experience = filter_experience_for_brief(experience)

    # Render the template with all data
    return template.render(
        personal=data.get("personal", {}),
        summary=data.get("summary", ""),
        highlights=data.get("highlights", []),
        skills=data.get("skills", []),
        education=data.get("education", []),
        experience=experience,
        certifications=data.get("certifications", {}),
        css=load_css(),
        is_brief=is_brief,
        career_start_year=CAREER_START_YEAR,
    )


def write_resume(content: str, name: str, is_brief: bool = False) -> Path:
    """
    Write the generated resume to an HTML file.

    Args:
        content: The resume content to write
        name: Person's name (used for filename)
        is_brief: Whether this is the brief version

    Returns:
        Path to the written file
    """
    output_path = get_output_path(name, "html", is_brief)
    write_text_file(output_path, content)
    return output_path


#───────────────────────────────────────────────────────────────────────────────
# Main Entry Point
#───────────────────────────────────────────────────────────────────────────────


def main(is_brief: bool = False) -> None:
    """
    Generate an HTML resume.

    Args:
        is_brief: If True, generate the brief version; otherwise generate full
    """
    # Ensure output directory exists
    ensure_output_dir()

    # Load resume data from YAML
    data = load_resume_data()
    name = data["personal"]["name"]

    # Generate the resume
    content = generate_resume(data, is_brief=is_brief)
    output_path = write_resume(content, name, is_brief=is_brief)
    print(f"  Created: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate HTML resume")
    parser.add_argument(
        "--brief",
        action="store_true",
        help="Generate brief version (recent experience only)",
    )
    args = parser.parse_args()
    main(is_brief=args.brief)
