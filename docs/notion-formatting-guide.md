# Notion Formatting Guide

Reference for agents writing content to Notion.

## Table Handling

**Pipe tables work when copy/pasted** into Notion, but can't be typed directly in the editor. The `/table-inline` command is the native way to create tables.

When using the Notion API (via MCP tools), tables require the API's block format—not markdown. The MCP tool handles this conversion.

**In markdown drafts:** Use standard pipe tables. The notion-writer agent will handle conversion for the API.

```markdown
| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |
```

## Supported Markdown

These work as expected:
- `# Heading 1`, `## Heading 2`, `### Heading 3`
- `**bold**` and `*italic*`
- `- bullet lists` and `1. numbered lists`
- `> blockquotes`
- `` `inline code` `` and code blocks
- `[link text](url)`
- `---` horizontal rule
- `- [ ]` checkboxes

## What Doesn't Work

- Footnotes
- Nested tables
- LaTeX/math notation (gets stripped)
- Complex HTML (gets flattened)
- Markdown images with local paths

## Best Practices

1. **Use headers liberally** — Notion's outline/TOC uses headers
2. **Keep paragraphs short** — Notion renders wide
3. **Avoid deeply nested lists** — 2-3 levels max
4. **Tables for structured data** — Keep them simple

## Page Structure

Notion pages work best with:
- Clear title
- Brief intro paragraph (no header needed)
- Logical header hierarchy (H1 → H2 → H3)
- Simple tables for comparisons

## Verification Needed

This guide should be updated with specifics about:
- Exact MCP tool behavior for table conversion
- Callout/toggle block syntax if supported
- Any workspace-specific formatting conventions

Sources: [Notion Markdown Guide](https://super.so/blog/notion-markdown-guide-the-complete-cheat-sheet-2024), [Markdown Guide - Notion](https://www.markdownguide.org/tools/notion/)
