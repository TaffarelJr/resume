#!/usr/bin/env python3
"""
Generate plain text resume for copying/pasting into online forms.

This script produces .txt files suitable for pasting into application
forms that don't support rich formatting.

Usage:
    python generate_text.py          # Generate full resume
    python generate_text.py --brief   # Generate brief resume
"""

import argparse
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from common import (
    # Configuration
    CAREER_START_YEAR,
    TEMPLATES_DIR,
    # Data loading
    load_resume_data,
    # Output functions
    get_output_path,
    ensure_output_dir,
    write_text_file,
    # Formatting functions
    filter_experience_for_brief,
    format_date_range,
    format_text_block,
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
        trim_blocks=True,      # Remove first newline after block tags
        lstrip_blocks=True,    # Strip leading whitespace from block tags
    )

    # Register custom filters (used with | syntax in templates)
    env.filters["format_text_block"] = format_text_block

    # Register global functions (called directly in templates)
    env.globals["format_date_range"] = format_date_range

    return env


#───────────────────────────────────────────────────────────────────────────────
# Helper Methods
#───────────────────────────────────────────────────────────────────────────────


def group_certifications_by_issuer(certifications: dict) -> list:
    """
    Group certifications by issuer for text display.

    When issuer differs from category name, creates a two-level hierarchy.
    When issuer is not specified (or same as name), creates a single-level list.

    Args:
        certifications: The certifications dict from YAML with 'categories' list

    Returns:
        List of dicts with 'header', 'subcategories' (optional), and 'items' keys
    """
    categories = certifications.get("categories", [])
    groups = {}  # Maps group key -> group dict
    order = []   # Preserves insertion order

    for category in categories:
        issuer = category.get("issuer")
        cat_name = category.get("name", "")
        items = category.get("items", [])

        # Use issuer as group key if available, otherwise category name
        group_key = issuer if issuer else cat_name

        # Find or create the group
        if group_key not in groups:
            groups[group_key] = {
                "header": group_key,
                "subcategories": [],
                "items": [],
            }
            order.append(group_key)

        group = groups[group_key]

        # Two-level hierarchy when issuer differs from category name
        if issuer and issuer != cat_name:
            # Look for existing subcategory
            existing = next(
                (s for s in group["subcategories"] if s["name"] == cat_name),
                None
            )
            if existing:
                existing["items"].extend(items)
            else:
                group["subcategories"].append({
                    "name": cat_name,
                    "items": list(items),
                })
        else:
            # Single-level — add directly to items
            group["items"].extend(items)

    # Return groups in insertion order
    return [groups[key] for key in order]


#───────────────────────────────────────────────────────────────────────────────
# Resume Generation
#───────────────────────────────────────────────────────────────────────────────


def generate_resume(data: dict, is_brief: bool = False) -> str:
    """
    Generate plain text resume content from data.

    Args:
        data: Resume data dictionary loaded from YAML
        is_brief: If True, generate shortened version for recent experience only

    Returns:
        Plain text resume content as a string
    """
    # Set up template environment
    env = create_jinja_env()
    template = env.get_template("resume.txt.jinja2")

    # Filter experience for brief version
    experience = data.get("experience", [])
    if is_brief:
        experience = filter_experience_for_brief(experience)

    # Group certifications by issuer for hierarchical display
    cert_groups = group_certifications_by_issuer(data.get("certifications", {}))

    # Render the template with all data
    return template.render(
        personal=data.get("personal", {}),
        summary=data.get("summary", ""),
        highlights=data.get("highlights", []),
        skills=data.get("skills", []),
        education=data.get("education", []),
        experience=experience,
        certifications=data.get("certifications", {}),
        cert_groups=cert_groups,
        is_brief=is_brief,
        career_start_year=CAREER_START_YEAR,
    )


def write_resume(content: str, name: str, is_brief: bool = False) -> Path:
    """
    Write the generated resume to a text file.

    Args:
        content: The resume content to write
        name: Person's name (used for filename)
        is_brief: Whether this is the brief version

    Returns:
        Path to the written file
    """
    output_path = get_output_path(name, "txt", is_brief)
    write_text_file(output_path, content)
    return output_path


#───────────────────────────────────────────────────────────────────────────────
# Main Entry Point
#───────────────────────────────────────────────────────────────────────────────


def main(is_brief: bool = False) -> None:
    """
    Generate a plain text resume.

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
    parser = argparse.ArgumentParser(description="Generate plain text resume")
    parser.add_argument(
        "--brief",
        action="store_true",
        help="Generate brief version (recent experience only)",
    )
    args = parser.parse_args()
    main(is_brief=args.brief)
