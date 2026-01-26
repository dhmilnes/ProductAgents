# Notion Formatting Guide

Reference for agents writing content to Notion. Notion uses a flavor of Markdown with important differences.

## Critical Differences from Standard Markdown

### Tables: Use XML, Not Pipes

**WRONG (standard Markdown):**
```markdown
| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |
```

**CORRECT (Notion XML):**
```xml
<table>
  <tr>
    <th>Column 1</th>
    <th>Column 2</th>
  </tr>
  <tr>
    <td>Cell 1</td>
    <td>Cell 2</td>
  </tr>
</table>
```

### Supported Markdown

These work as expected:
- `# Heading 1`, `## Heading 2`, `### Heading 3`
- `**bold**` and `*italic*`
- `- bullet lists` and `1. numbered lists`
- `> blockquotes`
- `` `inline code` `` and ``` code blocks ```
- `[link text](url)`
- `---` horizontal rule

### Notion-Specific Blocks

**Callouts:**
```
> [!NOTE]
> This is a callout block
```

**Toggle blocks:**
```
<details>
<summary>Click to expand</summary>
Hidden content here
</details>
```

**Checkboxes:**
```
- [ ] Unchecked item
- [x] Checked item
```

## Formatting Best Practices for Notion

1. **Use headers liberally** — Notion's outline/TOC uses headers
2. **Keep paragraphs short** — Notion renders wide; long paragraphs are hard to read
3. **Use callouts for key points** — They stand out visually
4. **Tables for structured data** — But remember XML syntax
5. **Avoid deeply nested lists** — Notion handles 2-3 levels well, beyond gets messy

## Page Structure

Notion pages work best with:
- Clear title
- Brief intro paragraph (no header)
- Logical header hierarchy (H1 → H2 → H3)
- Callouts for important warnings or key takeaways
- Tables for comparisons or structured data

## Common Gotchas

1. **Pipe tables won't render** — Always use XML table syntax
2. **HTML mostly doesn't work** — Except for tables and details/summary
3. **Nested toggles** — Work but can be confusing; use sparingly
4. **Images** — Must be URLs or uploaded separately; can't embed from local paths
5. **Code blocks** — Specify language for syntax highlighting: ```python
