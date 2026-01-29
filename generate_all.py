#!/usr/bin/env python3
"""
Master script to generate all resume formats.

Generates both full and brief versions of:
- Plain text (.txt) - for copying into online forms
- Markdown (.md) - with shields.io technology badges
- HTML (.html) - static with embedded CSS
- PDF (.pdf) - converted from HTML via WeasyPrint

Usage:
    python generate_all.py
"""

import sys
from pathlib import Path

# Add Scripts directory to path so we can import the generator modules
SCRIPTS_DIR = Path(__file__).parent / "Scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

# Import generator modules
from generate_text import main as generate_text
from generate_markdown import main as generate_markdown
from generate_html import main as generate_html
from generate_pdf import main as generate_pdf


#───────────────────────────────────────────────────────────────────────────────
# Main Entry Point
#───────────────────────────────────────────────────────────────────────────────


def main() -> None:
    """Generate all resume formats (full and brief versions)."""
    # Print header
    print("═" * 80)
    print("Generating all resume formats...")
    print("═" * 80)
    print()

    # Define generators: (display name, generator function)
    generators = [
        ("plain text", generate_text),
        ("Markdown", generate_markdown),
        ("HTML", generate_html),
        ("PDF", generate_pdf),
    ]

    # Generate each format (full and brief versions)
    for name, generate_fn in generators:
        print(f"Generating {name} resumes...")
        for is_brief in [False, True]:
            generate_fn(is_brief=is_brief)
        print()

    # Print footer
    print("═" * 80)
    print("All resume formats generated successfully!")
    print("═" * 80)


if __name__ == "__main__":
    main()
