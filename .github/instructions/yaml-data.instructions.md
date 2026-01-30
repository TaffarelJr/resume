---
applyTo: "resume_data.yml"
---

# Resume Data (YAML) Guidelines

## Dates

```yaml
start: { year: 2020, month: 1 }
end: { year: 2023, month: 12 } # Omit for current positions
```

## Multi-line Strings

Use block scalar (`|`). Relative indentation is preserved:

```yaml
description: |
  First line
  - Bullet point
    Continuation (indented)
```

## Technologies

```yaml
technologies:
  - item: "C#"
    isPrimary: true # Gets color from TechClass
  - item: "Docker" # isPrimary defaults to false (gray badge)
```

Add new primary technologies to `TECH_CLASS_LOOKUP` in `common.py`.

## Page Breaks (PDF)

```yaml
- company: "Example Corp"
  newPage: true # Forces page break before this position
```

## Certifications

Logo path built as: `../Certifications/{issuer}/{category.name}/{cert.name}/{cert.logo}`
