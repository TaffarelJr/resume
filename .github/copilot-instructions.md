# Resume Generator - Copilot Instructions

Python-based system that converts structured YAML data into multiple resume formats.

## Regenerating Resumes

After changes to templates, data, or scripts:

```powershell
.\.venv\Scripts\python.exe generate_all.py
```

Run **once** per request. Do not run multiple times unless the first fails.

## Project Structure

| Path                    | Purpose                                                                            |
| ----------------------- | ---------------------------------------------------------------------------------- |
| `resume_data.yml`       | Single source of truth for resume content                                          |
| `Scripts/common.py`     | Shared constants, utilities, badge colors (`TechClass` enum)                       |
| `Scripts/generate_*.py` | Format-specific generators                                                         |
| `Templates/*.jinja2`    | Jinja2 templates                                                                   |
| `Templates/styles.css`  | CSS for HTML/PDF (use classes, not element selectors for context-specific styling) |
| `Resumes/`              | Generated output (do not edit manually)                                            |

## Key Patterns

- **Dates**: Use `{year, month}` object format in YAML, not strings
- **Brief resumes**: Exclude positions before `BRIEF_CUTOFF_YEAR` and certifications
- **Badge colors**: Determined by `TechClass` enum and `TECH_CLASS_LOOKUP` in `common.py`
- **Page breaks**: Use `newPage: true` on positions to force PDF page breaks
- **Shared logic**: Keep in `common.py`; format-specific logic stays in generators
- **URL encoding**: Use `url_encode()` from `common.py` (wraps `urllib.parse.quote`)

## Generator Script Pattern

```python
def main(is_brief: bool = False) -> None:
    # --brief CLI flag via argparse
    # Import shared utilities from common.py
```

## Virtual Environment

```powershell
# Windows
.\.venv\Scripts\python.exe <script>

# Linux/macOS
.venv/bin/python <script>
```
