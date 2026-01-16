# CLAUDE.md

ProductAgents is an AI-powered workflow automation toolkit. It connects analytics data with documentation systems to automate research, writing, and reporting tasks.

## Meta: How to Evolve Prompts

**To trigger learning:** When I make a mistake, tell me:
> "Reflect on this. Abstract the pattern."

**Where does the rule belong?**

| Scope | Location | Example |
|-------|----------|---------|
| Global (applies everywhere) | CLAUDE.md | Windows Python `-c` fix |
| Skill-specific workflow | `.claude/skills/*/SKILL.md` | "Avoid magnitude words" in analyze |
| Agent behavior | `.claude/agents/*.md` | Tufte styling in py-visualization-writer |
| Reference docs | `docs/*.md` | Notion table syntax in formatting guide |

**Is it a new rule or an edit?** Often the right fix is clarifying an existing rule, not adding a new one. Check if related guidance already exists.

**Rule format (when adding new):**
- Lead with WHY before the rule — context prevents misapplication
- Use NEVER/ALWAYS for hard constraints, "prefer" for soft guidance
- Keep rules under 2 sentences
- Add examples only when the antipattern is subtle

**What belongs in CLAUDE.md specifically:** Cross-cutting patterns that affect multiple workflows, repo-wide conventions, integration quirks.

## Learned Patterns

Rules added through reflection on recurring mistakes.

- **Failing to read the personal folder leads to missed context.** ALWAYS check for an `personal/aboutme.md` for user-specific context and saved queries before starting work.

- **Duplicating source docs bloats skill files and creates maintenance burden.** NEVER repeat what a template or external doc already explains. Link to the source for "what to include," only add supplementary value: format specifics, length limits, examples, gotchas.

- **Writing without reading the source leads to drift and rework.** ALWAYS fetch and verify source documents before writing content that depends on them - but only what the current task requires, not "just in case."

- **Skills require exact file structure to be discoverable.** Entry file MUST be named `SKILL.md` (not `prompt.md`). MUST include YAML frontmatter with `name` and `description` fields. Without these, Claude Code won't recognize the skill.

- **Skill instructions specify architecture, not suggestions.** When a skill says "use X agent for Y task" or lists Critical Rules, those define the workflow - not optional guidance. Read the Critical Rules section FIRST and treat agent delegation as constraints. Default behavior is to "just do the work" which violates orchestration patterns.

## Notion Formatting

Before writing to Notion, read `docs/notion-formatting-guide.md`. Key gotcha: tables require XML syntax, not Markdown pipes.

## Available Workflows
Always check skills for use cases.

**Skills** (`.claude/skills/`) — Auto-discovered via YAML frontmatter. Claude uses these automatically when user needs apply.

| Skill | Purpose | Invoked By |
|-------|---------|------------|
| `analyze` | Rigorous data investigation | User asks data questions |
| `uxr-synthesize` | Interview transcript synthesis | User has transcripts to analyze |
| `test-thinking` | A/B test variation design | User designing test variations |

## Personal Query Library

Users can save SQL queries they run repeatedly in `personal/queries/`. Check there before invoking full data discovery.

**When user asks for data:**
1. Check if `personal/queries/` has a matching query (by name or description)
2. If found: read the file, parse YAML frontmatter for params, substitute values, run directly
3. If not found: proceed with data analysis skills for full field/table discovery

**Query file format:**
```sql
---
name: Weekly Metrics Report
description: 7-day metrics for specific segment
params:
  period_start: "2025-01-01"
  segment: "enterprise"
---
SELECT ... WHERE date >= @period_start AND segment = @segment
```

**Saving new queries:**
When a query works well and seems reusable, offer to save it:
1. Ask: "Want me to save this query for reuse?"
2. If yes: create file in `personal/queries/` with descriptive name (lowercase, underscores)
3. Extract variable parts as params (dates, segments, products)
4. Add YAML frontmatter with name, description, and param defaults


### Key Patterns

**tmp/ has 24-hour TTL.** Use tmp/ for intra-conversation context (e.g., advisors writing files for query agents to read). Files survive overnight for next-morning work, but treat as ephemeral - don't rely on them persisting long-term.

**Copy to output/ before Python analysis.** When a CSV path in `tmp/`, copy it to `output/` immediately if you'll need it for visualization or further analysis. Temp CSVs auto-delete.

**Check for prior work before starting analysis.** Time-saving pattern for data analysis tasks:
1. Ask user: "Is there prior work on [topic] I should reference?"
2. If user indicates yes, check `scratch/`, `output/`, `research_briefs/` for relevant files
3. Reuse queries, data, or analysis structure when applicable

**File naming conventions:**
- Include topic and date: `feature_timeline_2025-01-11.py`
- Use underscores, lowercase
- Version when iterating: `timeline_v2.py`, `timeline_v3.py`

### Subdirectory Standards

| Path | Contents |
|------|----------|
| `output/visualizations/` | PNG charts from py-visualization-writer |
| `scratch/uxr-[project]/` | UXR coding aggregation files |
| `personal/queries/` | Saved reusable SQL queries |

All folders are tracked in git but contents are gitignored (except personal/README.md and templates).

### Key Files
- @docs/notion-formatting-guide.md — Full Notion syntax reference


## Agent Orchestration Principles

When workflows spawn sub-agents:
1. **User gates critical actions** - Always get approval before updating Notion or making significant changes
2. **Separation of concerns** - Research agents don't write, writing agents don't search
3. **Parallel execution** - Spawn independent agents simultaneously when possible
4. **Clear handoffs** - Agents return focused briefs, orchestrator decides what to commit

## Boundaries

**Never:**
- Commit secrets, credentials, or API keys
- Modify production data or configs without explicit approval
- Include PII (names, emails, user IDs) in outputs shared externally
- Push to main/master without PR review
- Run destructive commands (DROP, DELETE, rm -rf) without confirmation

**Always ask first:**
- Before making changes that affect multiple files
- Before running commands that cost money (large database queries)
- When uncertain about user intent

## Troubleshooting

**Notion update fails silently**: Verify page ID is correct and you have edit access. Use `notion-fetch` first to confirm.

## Repository Structure

```
ProductAgents/
├── .claude/
│   ├── skills/          # Auto-used by Claude when user needs apply
│   ├── commands/        # User-invokable via /command
│   ├── agents/          # Specialized sub-agents (called by skills/commands)
│   └── settings.local.json
├── docs/
│   ├── db/          # Schema docs, example queries, hints
│   └── notion-formatting-guide.md
├── mcp_servers/         # homebrewed mcps
├── scripts/             # Python utilities
├── tmp/                 # Session-only ephemeral files (fully gitignored)
│   ├── context/         # Advisor outputs for query agents
│   ├── csv/       # Query result CSVs (auto-cleaned)
│   └── uxr/             # UXR coding intermediate files
├── personal/            # User-specific context and queries (contents gitignored)
│   └── queries/         # Saved SQL queries for quick reuse
├── research_briefs/     # Agent research outputs (contents gitignored)
├── scratch/             # Active working files (contents gitignored)
├── drafts/              # WIP documents (contents gitignored)
├── output/              # Stable outputs (contents gitignored)
│   └── visualizations/  # Charts from py-visualization-writer
└── CLAUDE.md            # This file
```
