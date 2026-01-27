# Demo Data MCP Server

A lightweight SQLite MCP server for demoing the ProductAIFlows `analyze` skill.

## What's Included

**Sample data for LearnFlow Technologies** (fictional ed-tech company):
- 2 years of daily metrics (sessions, conversions, revenue)
- Channel breakdown (organic, paid, advisor, partner, direct)
- Product breakdown (Core Curriculum, Professional Cert, Pathway Bundle, Enterprise)
- Support tickets with categories and sentiment
- Weekly funnel metrics

**Baked-in story:** The cancel/pause reputation problem
- Cancellation complaints have risen from ~15% to ~35% of tickets over 6 months
- Public channels (app reviews, social) are over-indexed for cancellation issues
- Partner escalations started appearing in Jan 2026 (ASU legal concern)

## Setup

### 1. Install dependencies

```bash
pip install mcp
```

### 2. Generate sample data (optional — already included)

```bash
python setup_sample_data.py
```

### 3. Add to Claude Code MCP config

Add to your `.claude/mcp.json`:

```json
{
  "mcpServers": {
    "demo-data": {
      "command": "python",
      "args": ["mcp_servers/demo-data/server.py"]
    }
  }
}
```

## Available Tools

| Tool | Purpose |
|------|---------|
| `query` | Execute SELECT queries against the database |
| `list_tables` | Show all tables with row counts |
| `describe_table` | Show schema and sample values for a table |
| `get_date_range` | Get min/max dates in a table |

## Tables

### `daily_metrics`
Aggregate daily metrics (731 rows, 2 years)

| Column | Type | Description |
|--------|------|-------------|
| date | TEXT | YYYY-MM-DD |
| sessions | INTEGER | Daily sessions |
| new_users | INTEGER | New user count |
| signups | INTEGER | Account signups |
| trials_started | INTEGER | Trial activations |
| conversions | INTEGER | Purchases |
| revenue | REAL | Daily revenue |
| avg_order_value | REAL | AOV |

### `channel_metrics`
Daily metrics by acquisition channel

| Column | Type | Description |
|--------|------|-------------|
| date | TEXT | YYYY-MM-DD |
| channel_id | TEXT | organic, paid_search, advisor, partner, direct |
| channel_name | TEXT | Display name |
| sessions, signups, conversions, revenue | | Metrics |

### `product_metrics`
Daily metrics by product

| Column | Type | Description |
|--------|------|-------------|
| date | TEXT | YYYY-MM-DD |
| product_id | TEXT | core_curriculum, professional_cert, pathway_bundle, enterprise |
| product_name | TEXT | Display name |
| units_sold | INTEGER | Units |
| revenue | REAL | Revenue |
| refunds | INTEGER | Refund count |
| refund_amount | REAL | Refund $ |

### `support_tickets`
Individual support tickets (~20k rows)

| Column | Type | Description |
|--------|------|-------------|
| ticket_id | INTEGER | Unique ID |
| created_date | TEXT | YYYY-MM-DD |
| category | TEXT | cancellation, billing, technical, account, content |
| subcategory | TEXT | Specific issue type |
| channel | TEXT | email, chat, app_review, social, partner_escalation |
| sentiment_score | REAL | -1.0 to 0 (all negative) |
| resolution_hours | REAL | Time to resolve |
| escalated | INTEGER | 0 or 1 |

### `weekly_funnel`
Weekly conversion funnel

| Column | Type |
|--------|------|
| week_start | TEXT |
| visitors, product_views, add_to_cart, checkout_started, checkout_completed | INTEGER |
| conversion_rate | REAL |

## Demo Queries

**Cancellation trend by month:**
```sql
SELECT
    strftime('%Y-%m', created_date) as month,
    COUNT(*) as total_tickets,
    SUM(CASE WHEN category = 'cancellation' THEN 1 ELSE 0 END) as cancel_tickets,
    ROUND(100.0 * SUM(CASE WHEN category = 'cancellation' THEN 1 ELSE 0 END) / COUNT(*), 1) as cancel_pct
FROM support_tickets
WHERE created_date >= '2025-07-01'
GROUP BY month
ORDER BY month
```

**Cancellation issues by channel:**
```sql
SELECT
    channel,
    COUNT(*) as tickets,
    ROUND(AVG(sentiment_score), 2) as avg_sentiment
FROM support_tickets
WHERE category = 'cancellation'
  AND created_date >= '2025-10-01'
GROUP BY channel
ORDER BY tickets DESC
```

**YoY revenue comparison:**
```sql
SELECT
    strftime('%Y-%W', date) as year_week,
    SUM(revenue) as revenue
FROM daily_metrics
WHERE date >= date('2026-01-26', '-14 days')
   OR date >= date('2025-01-26', '-14 days') AND date < '2025-02-10'
GROUP BY year_week
ORDER BY year_week
```

## Swapping in Real Data

To use your own data:

1. Replace `sample_data.db` with your SQLite database
2. Or modify `server.py` to connect to a different database (Postgres, BigQuery, etc.)

The MCP tools (`query`, `list_tables`, etc.) will work with any SQL database.
