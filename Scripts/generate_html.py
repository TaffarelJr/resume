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
    build_badge_url,
    url_encode,
)


#───────────────────────────────────────────────────────────────────────────────
# HTML Formatting
#───────────────────────────────────────────────────────────────────────────────


def _render_paragraph(lines: list[str]) -> str:
    """Render paragraph lines as a <p> element."""
    return f"<p>{' '.join(lines)}</p>"


def _render_bullets(bullets: list[str], badges: list[str] | None = None) -> list[str]:
    """Render bullet lines as a <ul> element, optionally with badges as final <li>."""
    result = ["  <ul>"]
    for bullet in bullets:
        result.append(f"    <li>{bullet}</li>")
    if badges:
        result.append("    <li>")
        for badge in badges:
            result.append(f"      {badge}")
        result.append("    </li>")
    result.append("  </ul>")
    return result


def _classify_line(line: str, has_pending_bullets: bool) -> tuple[str, str]:
    """
    Classify a line and extract its content.

    Returns:
        Tuple of (line_type, content) where line_type is one of:
        'bullet', 'continuation', 'paragraph', or 'empty'
    """
    stripped = line.lstrip()
    if not stripped:
        return ("empty", "")
    if stripped.startswith("- "):
        return ("bullet", stripped[2:].strip())
    leading_spaces = len(line) - len(stripped)
    if leading_spaces > 0 and has_pending_bullets:
        return ("continuation", stripped)
    return ("paragraph", stripped)


def format_html_block(text: str, badges: list[str] | None = None) -> str:
    """
    Format a text block for HTML output, optionally with technology badges.

    Converts text with bullet points into proper HTML structure:
    - Non-bullet lines become <p> elements
    - Consecutive bullet lines are wrapped in <ul><li> elements
    - Continuation lines (indented non-bullets) are joined to previous line
    - If badges are provided, they become the final <li> in a <ul>, each on its own line

    Args:
        text: The text to format (may contain newlines and bullet points)
        badges: List of badge HTML strings (e.g., '<img src="...">')

    Returns:
        HTML-formatted string with proper <p> and <ul>/<li> tags
    """
    if badges is None:
        badges = []
    lines = text.strip().split("\n") if text else []
    result: list[str] = []
    current_bullets: list[str] = []
    current_paragraph: list[str] = []

    for line in lines:
        line_type, content = _classify_line(line, bool(current_bullets))

        if line_type == "bullet":
            if current_paragraph:
                result.append(_render_paragraph(current_paragraph))
                current_paragraph.clear()
            current_bullets.append(content)

        elif line_type == "continuation":
            current_bullets[-1] += " " + content

        elif line_type == "paragraph":
            if current_bullets:
                result.extend(_render_bullets(current_bullets))
                current_bullets.clear()
            current_paragraph.append(content)

    # Flush remaining content
    if current_paragraph:
        result.append(_render_paragraph(current_paragraph))
    if current_bullets or badges:
        result.extend(_render_bullets(current_bullets, badges))

    return "\n".join(result)


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
    env.filters["format_html_block"] = format_html_block
    env.filters["tech_to_badge"] = tech_to_badge
    env.filters["url_encode"] = url_encode

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
    url = build_badge_url(name, is_primary)
    return f'<img src="{url}" alt="{name}">'


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
