---
applyTo: "Templates/**/*.jinja2"
---

# Jinja2 Template Guidelines

## Multi-line Text

Preserve indentation for continuation lines in Markdown lists:

```jinja
{{ item.description | trim | indent(2, first=False) }}
```

## Whitespace Control

- Use `{%-` and `-%}` to control blank lines where formatting matters
- Be intentional: blank lines affect Markdown rendering

## Filters

| Filter              | Purpose                                                       |
| ------------------- | ------------------------------------------------------------- |
| `format_date_range` | Format date objects as "M/YYYY - M/YYYY"                      |
| `tech_to_badge`     | Convert technology dict to badge HTML/Markdown                |
| `url_encode`        | URL-encode paths (preserves `/` by default)                   |
| `format_html_block` | Convert text with bullets to `<p>` and `<ul><li>` (HTML only) |

## HTML-specific

- Use CSS classes from `styles.css` instead of inline styles
- Pass badge lists (not joined strings) to `format_html_block` for proper indentation
