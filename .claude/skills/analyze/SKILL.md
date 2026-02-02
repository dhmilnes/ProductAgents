---
name: analyze
description: Rigorous data investigation with hypotheses, YoY context, and audit trail.
---

# Analyze

You investigate data questions with rigor. Be autonomous, be skeptical, be transparent.

## Rules

1. **Hypotheses first.** Before querying, brainstorm hypotheses thinking about differential diagnosis.

2. **Expected vs. unexpected.** Context is not a finding. Ask: "Is this in line with the established trend, or is something new happening?" Compare to recent trend, not just raw YoY.

3. **YoY always.** Raw numbers mean nothing without year-over-year context. Use 364-day lookback to align day-of-week. When using the 364 look back, don't forget holidays that can shift weekdays (New Years) or weeks (Easter).

4. **Segment when things move.** When a metric changes, break by relevant dimensions (product, channel, platform, region). Check for mix shift (Simpson's Paradox).

5. **Show your work.** Every SQL query, python script file path you run goes in the response. Reproducibility is non-negotiable.

6. **State limitations.** What the data can't tell you is as important as what it can.

7. **Check prior work first.** Before starting analysis on a specific entity, check `scratch/` for prior related work. Don't reinvent queries that already exist.

## Method

1. **Frame** - What metric, time period, segments? What's the baseline?
2. **Establish trend** - Query trailing 8-12 weeks to see the recent pattern. This is your "expected" baseline.
3. **Hypothesize** - List competing explanations before touching data
4. **Research schema FIRST** - If using query tools, identify correct tables/fields before writing SQL. Don't assume field names match their apparent meaning.
5. **Query** - Test each hypothesis. Use available data discovery tools if needed
6. **Compare to trend** - Is latest data in line with recent trajectory, or is something new happening?
7. **Deliver** - Lead with what's *different*, not what's *known*

**CRITICAL:** If results contradict other known metrics (e.g., conversions down but downstream activity up), treat this as a red flag that you may have the wrong fields. Re-check schema before reporting.

## Analytical Reflexes

**Decompose rates vs. volume:**
- Conversions = Sessions × Conversion Rate
- Revenue = Customers × Average Order Value

**Work the funnel top-down:**
- Awareness → Interest → Trial → Purchase → Retention
- Find the bottleneck before diagnosing everywhere

**Distinguish time series patterns:**
- Trend (sustained) vs. level shift (step change) vs. spike (noise)

**For A/B tests, check:**
- Sample ratio mismatch
- Enough runtime (7+ days)
- Practical significance, not just statistical

## Tools

- **Query tools** - If available, use data discovery tools to verify schema and field semantics before writing queries. Don't guess field meanings - verify first.
- **py-visualization-writer agent** - Use when a chart would clarify the story. Titles state the insight factually, not dramatically. Avoid meaningless magnitude words ("collapsed", "soared", "exploded") - use specific numbers instead ("Share Down to 11%" not "Share Collapsed").

## Working with Query Results in Python

Each analysis gets a dedicated folder: `scratch/{topic}_{date}/`. All artifacts live together — CSVs, scripts, visualizations.

1. **Create analysis folder** - e.g. `scratch/support_tickets_2026-01-31/`
2. **Run query** - The query tool auto-saves CSVs and SQL to `tmp/csv/` with timestamped names
3. **Copy to analysis folder** - Give the file a descriptive name: `cp tmp/csv/query_20260128_213925.csv scratch/support_tickets_2026-01-31/support_monthly_trend_2026-01-31.csv`
4. **All scripts and charts save to the same folder**

**Naming convention:** `{topic}_{date}.{ext}`
- `weekly_conversion_rates_2026-01-28.csv`
- `support_ticket_trend_2026-01-31.py`
- `support_ticket_trend_2026-01-31.png`

**Why:** Temp CSVs in `tmp/` auto-delete. Keeping everything in one folder makes analysis reproducible and easy to find later.

**Pattern:**
```python
# In scratch/support_tickets_2026-01-31/support_ticket_trend_2026-01-31.py
df = pd.read_csv('scratch/support_tickets_2026-01-31/support_monthly_trend_2026-01-31.csv')
```

## Flexible Data Input

This skill works with:
- **Pre-provided data** - User shares CSV/data file directly
- **Sequential workflow** - User runs query tool separately, then invokes analyze
- **Integrated workflow** - Skill calls query tools during analysis

Adapt method based on available data sources.

## Output Format

### Findings
[One sentence answer focused on what's *new or different*—not known patterns.]

**What's new:** [Changes from recent trend that warrant attention]

**What's expected:** [Known patterns that are continuing—context, not findings]

### Data
Show the actual data so the user can see the story:

| Period | Metric | YoY Change | Rate |
|--------|--------|------------|------|
| This Week | 12,450 | -8.2% | 2.1% |
| Last Week | 13,100 | +2.1% | 2.3% |
| Same Week LY | 13,560 | — | 2.4% |

[Add as many tables as needed to support each hypothesis tested.]

### Hypotheses
| Hypothesis | What We Checked | Verdict |
|------------|-----------------|---------|
| Volume dropped | Traffic down 5% YoY | Partial - not enough to explain |
| Conversion dropped | Rate down 12% YoY | **Supported** - main driver |
| Seasonal effect | Same week LY was +3% | Refuted |

### Queries
```sql
-- What this tests
SELECT ...
```

### Limitations
- [What this can't tell you]
- [Assumptions made]

### Next Steps
- [Recommendations if applicable]
