---
applyTo: "**/*.py"
---

# Python Guidelines

## Style

- Type hints for all function parameters and return types
- Docstrings for modules, classes, and public functions
- Use `Path` from `pathlib`, not string concatenation
- Follow existing patterns in `Scripts/common.py`

## Architecture

- **Shared logic** → `common.py` (constants, utilities, badge URL building)
- **Format-specific logic** → respective `generate_*.py` (e.g., `tech_to_badge`, `format_html_block`)
- **Jinja2 filters** registered in each generator's `create_jinja_env()`

## Refactoring

- Extract helper functions to reduce cognitive complexity
- Prefer pure functions over closures that mutate outer scope
- Use `safe=""` with `url_encode()` for badge labels, default `safe="/"` for paths
