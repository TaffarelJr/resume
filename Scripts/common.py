"""
Common configuration and helper functions for resume generation scripts.

This module provides shared constants, paths, and utility functions used
across all resume format generators (text, markdown, HTML, PDF).
"""

import re
from pathlib import Path
from typing import Optional

import yaml


#───────────────────────────────────────────────────────────────────────────────
# Configuration Constants
#───────────────────────────────────────────────────────────────────────────────

# First year of professional experience (for "additional experience" notes)
CAREER_START_YEAR = 1999

# Year cutoff for brief resume versions.
# Positions ending before this year will be excluded from brief resumes.
BRIEF_CUTOFF_YEAR = 2013

# Date format for display. Use {month} and {year} placeholders.
# Examples: "{month}/{year}" -> "3/2023", "{year}-{month:02d}" -> "2023-03"
DATE_FORMAT = "{month}/{year}"

# Label for current/ongoing positions (no end date)
DATE_PRESENT_LABEL = "Present"


#───────────────────────────────────────────────────────────────────────────────
# Path Constants
#───────────────────────────────────────────────────────────────────────────────

# Root of the repository (parent of Scripts folder)
REPO_ROOT = Path(__file__).parent.parent

# Path to the resume data file
DATA_FILE = REPO_ROOT / "resume_data.yml"

# Output directory for generated resumes
OUTPUT_DIR = REPO_ROOT / "Resumes"

# Templates directory (at repo root)
TEMPLATES_DIR = REPO_ROOT / "Templates"

# CSS file for HTML/PDF output
CSS_FILE = TEMPLATES_DIR / "styles.css"


#───────────────────────────────────────────────────────────────────────────────
# Data Loading Functions
#───────────────────────────────────────────────────────────────────────────────


def load_resume_data() -> dict:
    """
    Load and parse the resume YAML data file.

    Returns:
        Dictionary containing all resume data sections
    """
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_css() -> str:
    """
    Load the CSS stylesheet for HTML/PDF output.

    Returns:
        CSS content as a string
    """
    return CSS_FILE.read_text(encoding="utf-8")


#───────────────────────────────────────────────────────────────────────────────
# Output File Functions
#───────────────────────────────────────────────────────────────────────────────


def sanitize_filename(name: str) -> str:
    """
    Sanitize a string for use in filenames.

    Replaces spaces with underscores and replaces characters that are
    problematic in filenames or URLs with dashes.

    Args:
        name: The string to sanitize (typically a person's name)

    Returns:
        Sanitized string safe for use in filenames
    """
    # Replace spaces with underscores
    result = name.replace(" ", "_")

    # Replace characters forbidden in Windows filenames with dashes
    result = re.sub(r'[\\/:*?"<>|]', "-", result)

    # Collapse multiple underscores into one
    result = re.sub(r"_+", "_", result)

    # Collapse multiple dashes into one
    result = re.sub(r"-+", "-", result)

    # Remove leading/trailing underscores and dashes
    result = result.strip("_-")

    return result


def get_output_path(name: str, extension: str, is_brief: bool = False) -> Path:
    """
    Generate the output file path based on the person's name.

    Args:
        name: The person's name from the YAML data
        extension: File extension without dot (e.g., 'pdf', 'md', 'html', 'txt')
        is_brief: Whether this is the brief version

    Returns:
        Path object for the output file
    """
    safe_name = sanitize_filename(name)
    suffix = "_brief" if is_brief else ""
    filename = f"{safe_name}_resume{suffix}.{extension}"
    return OUTPUT_DIR / filename


def ensure_output_dir() -> None:
    """Create the output directory if it doesn't exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def write_text_file(path: Path, content: str) -> None:
    """
    Write text content to a file, creating parent directories as needed.

    Args:
        path: The file path to write to
        content: The text content to write
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_binary_file(path: Path, content: bytes) -> None:
    """
    Write binary content to a file, creating parent directories as needed.

    Args:
        path: The file path to write to
        content: The binary content to write
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


#───────────────────────────────────────────────────────────────────────────────
# Date Formatting Functions
#───────────────────────────────────────────────────────────────────────────────


def format_date(date_obj: Optional[dict]) -> str:
    """
    Format a date object for display.

    Args:
        date_obj: Date dict with 'year' and optional 'month', or None for current

    Returns:
        Formatted date string (e.g., "3/2023" or "Present")
    """
    # None means current/ongoing
    if date_obj is None:
        return DATE_PRESENT_LABEL

    year = date_obj.get("year")
    month = date_obj.get("month")

    # No year means current
    if year is None:
        return DATE_PRESENT_LABEL

    # Year only (no month)
    if month is None:
        return str(year)

    # Full date with month and year
    return DATE_FORMAT.format(month=month, year=year)


def format_date_range(dates: dict) -> str:
    """
    Format a date range for display.

    Args:
        dates: Dictionary with 'start' and optionally 'end' keys,
               each containing 'year' and optional 'month'

    Returns:
        Formatted string like "3/2023 - Present" or "7/2021 - 3/2023"
    """
    start = format_date(dates.get("start"))
    end = format_date(dates.get("end"))
    return f"{start} - {end}"


#───────────────────────────────────────────────────────────────────────────────
# Experience Filtering
#───────────────────────────────────────────────────────────────────────────────


def filter_experience_for_brief(experience: list) -> list:
    """
    Filter experience entries for the brief resume version.

    Excludes positions that ended before BRIEF_CUTOFF_YEAR.

    Args:
        experience: List of experience entries from YAML data

    Returns:
        Filtered list of experience entries
    """
    filtered = []

    for position in experience:
        end_date = position.get("dates", {}).get("end")

        # No end date means position is current — always include
        if end_date is None:
            filtered.append(position)
            continue

        # Get the end year from the date structure
        end_year = end_date.get("year")

        # If we can't determine the year, include it to be safe
        if end_year is None:
            filtered.append(position)
            continue

        # Include if ended on or after the cutoff year
        if end_year >= BRIEF_CUTOFF_YEAR:
            filtered.append(position)

    return filtered


#───────────────────────────────────────────────────────────────────────────────
# Technology Badge Helpers
#───────────────────────────────────────────────────────────────────────────────

from enum import Enum


class TechClass(Enum):
    """Technology classification for badge coloring."""
    LANGUAGE = "language"
    DATABASE = "database"
    UI = "ui"
    AI = "ai"
    SDLC = "sdlc"


# Map technology class to badge color (using color names for shields.io)
TECH_CLASS_COLORS: dict[TechClass, str] = {
    TechClass.LANGUAGE: "forestgreen",
    TechClass.DATABASE: "blue",
    TechClass.UI: "blueviolet",
    TechClass.AI: "red",
    TechClass.SDLC: "orange",
}

# Map technology names to their class (case-insensitive lookup)
# Only technologies that should be colored need to be listed here
TECH_CLASS_LOOKUP: dict[str, TechClass] = {
    # Languages
    ".net": TechClass.LANGUAGE,
    "c#": TechClass.LANGUAGE,
    "vb.net": TechClass.LANGUAGE,
    "vb6": TechClass.LANGUAGE,
    "vba": TechClass.LANGUAGE,
    "java": TechClass.LANGUAGE,
    "python": TechClass.LANGUAGE,
    "javascript": TechClass.LANGUAGE,
    "typescript": TechClass.LANGUAGE,

    # Databases
    "sql server": TechClass.DATABASE,
    "cosmosdb": TechClass.DATABASE,
    "mongodb": TechClass.DATABASE,
    "postgresql": TechClass.DATABASE,
    "ravendb": TechClass.DATABASE,
    "sqlite": TechClass.DATABASE,
    "oracle": TechClass.DATABASE,
    "mysql": TechClass.DATABASE,
    "snowflake": TechClass.DATABASE,
    "ms access": TechClass.DATABASE,

    # UI Frameworks
    "angular": TechClass.UI,
    "angularjs": TechClass.UI,
    "angular 2": TechClass.UI,
    "react": TechClass.UI,
    "vue": TechClass.UI,
    "blazor": TechClass.UI,
    "winforms": TechClass.UI,
    "wpf": TechClass.UI,

    # AI/ML
    "ai": TechClass.AI,
    "llm": TechClass.AI,
    "agents": TechClass.AI,
    "semantic kernel": TechClass.AI,
    "kernel memory": TechClass.AI,
    "prompt engineering": TechClass.AI,

    # SDLC (Source control, CI/CD, DevOps)
    "git": TechClass.SDLC,
    "github enterprise": TechClass.SDLC,
    "azure devops": TechClass.SDLC,
    "tfs": TechClass.SDLC,
    "teamcity": TechClass.SDLC,
    "jira": TechClass.SDLC,
    "mercurial": TechClass.SDLC,
    "vss": TechClass.SDLC,
    "terraform": TechClass.SDLC,
}


def get_badge_color(name: str, is_primary: bool = False) -> str:
    """
    Determine badge color based on technology name and primary status.

    Primary technologies are colored by their technology class.
    Secondary technologies are always lightgray.

    Args:
        name: Technology name (e.g., "C#", "SQL Server")
        is_primary: Whether this is a primary/featured technology

    Returns:
        Color name for shields.io badge (e.g., "forestgreen", "lightgray")
    """
    # Secondary technologies are always lightgray
    if not is_primary:
        return "lightgray"

    # Look up the technology class (case-insensitive)
    name_lower = name.lower()
    tech_class = TECH_CLASS_LOOKUP.get(name_lower)

    # If we found a class, return its color; otherwise default to lightgray
    if tech_class:
        return TECH_CLASS_COLORS[tech_class]

    return "lightgray"


def url_encode_badge_text(text: str) -> str:
    """
    URL-encode text for use in shields.io badge URLs.

    Args:
        text: The text to encode (e.g., "C#", "ASP.NET Core")

    Returns:
        URL-encoded string safe for use in badge URLs
    """
    return text.replace(" ", "%20").replace("#", "%23").replace("+", "%2B")


def build_badge_url(name: str, is_primary: bool = False) -> str:
    """
    Build a shields.io badge URL for a technology.

    Handles all shields.io escaping conventions:
    - Dashes become double-dash (--)
    - Underscores become double-underscore (__)
    - Spaces and special characters are URL-encoded

    Args:
        name: Technology name (e.g., "C#", "SQL Server")
        is_primary: Whether this is a primary/featured technology

    Returns:
        Complete shields.io badge URL
    """
    # Escape shields.io special characters first
    label = name.replace("-", "--").replace("_", "__")
    # Then URL-encode for the URL
    label = url_encode_badge_text(label)
    color = get_badge_color(name, is_primary)
    return f"https://img.shields.io/badge/{label}-{color}"
