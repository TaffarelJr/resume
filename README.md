# Resume Generator

This repository contains my professional resume as structured YAML data,
with Python scripts to generate multiple output formats.

**🌐 [View my resume online](https://taffareljr.github.io/resume)**

---

## Overview

Rather than maintaining multiple resume files manually, this project:

1. Stores all resume content in a single YAML file ([resume_data.yml](resume_data.yml))
2. Uses Jinja2 templates to generate formatted output
3. Produces multiple formats: HTML, PDF, Markdown, and plain text
4. Automatically regenerates files via GitHub Actions when changes are pushed

## Output Formats

| Format         | Use Case                              |
| -------------- | ------------------------------------- |
| **HTML**       | Web viewing, GitHub Pages             |
| **PDF**        | Printing, email attachments           |
| **Markdown**   | GitHub display, easy editing          |
| **Plain Text** | Pasting into online application forms |

Each format has both a **full** version and a **brief** version
(which only includes recent experience,
to limit the size to ~3 pages).

---

## Development Setup

### Prerequisites

- Python 3.12+
- (Optional) GTK libraries for PDF generation via WeasyPrint

### Installation

```bash
# Create virtual environment
python -m venv .venv

# Activate it (Windows)
.venv\Scripts\activate

# Activate it (Linux/macOS)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Generate Resumes

```bash
# Generate all formats (full and brief versions)
python generate_all.py

# Or generate individual formats
python Scripts/generate_text.py          # Full text resume
python Scripts/generate_text.py --brief  # Brief text resume
python Scripts/generate_html.py
python Scripts/generate_markdown.py
python Scripts/generate_pdf.py
```

> **Note:** PDF generation requires GTK libraries.
> On Windows, it will skip gracefully. The GitHub Actions workflow
> runs on Linux where these are available.

---

## Project Structure

```
├── resume_data.yml          # Source data (single source of truth)
├── generate_all.py          # Master script to generate all formats
├── Scripts/
│   ├── common.py            # Shared utilities and configuration
│   ├── generate_text.py     # Plain text generator
│   ├── generate_markdown.py # Markdown generator
│   ├── generate_html.py     # HTML generator
│   └── generate_pdf.py      # PDF generator (via WeasyPrint)
├── Templates/
│   ├── resume.txt.jinja2    # Plain text template
│   ├── resume.md.jinja2     # Markdown template
│   ├── resume.html.jinja2   # HTML template (also used for PDF)
│   └── styles.css           # Styles for HTML/PDF
├── Resumes/                 # Generated output files
├── Certifications/          # Certification logos and documents
├── index.md                 # GitHub Pages landing page
└── .github/workflows/       # GitHub Actions automation
```

---

## GitHub Actions

The workflow in [generate-resumes.yml](.github/workflows/generate-resumes.yml) automatically:

1. Triggers on pull requests to `main`
2. Installs Python and system dependencies
3. Runs [generate_all.py](generate_all.py)
4. Commits any changed resume files back to the PR branch

This ensures the generated resumes are always in sync with the source data.

---

## License

The scripts, templates, and project structure are released
under the [MIT License](LICENSE).

The resume content ([resume_data.yml](resume_data.yml)) and certification images
are my personal data and not covered by this license.
