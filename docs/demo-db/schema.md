# Demo Database Schema

LearnFlow Technologies sample data for analysis demos.

## Tables

### daily_metrics
Aggregate daily metrics. Use for top-level trends.

| Column | Type | Notes |
|--------|------|-------|
| date | TEXT | Primary key, YYYY-MM-DD |
| sessions | INTEGER | Total site sessions |
| new_users | INTEGER | First-time visitors |
| signups | INTEGER | Account creations |
| trials_started | INTEGER | Trial activations |
| conversions | INTEGER | Completed purchases |
| revenue | REAL | Total revenue (USD) |
| avg_order_value | REAL | Revenue / conversions |

**Date range:** 2024-01-27 to 2026-01-26 (2 years)

---

### channel_metrics
Daily metrics broken down by acquisition channel.

| Column | Type | Notes |
|--------|------|-------|
| date | TEXT | YYYY-MM-DD |
| channel_id | TEXT | organic, paid_search, advisor, partner, direct |
| channel_name | TEXT | Human-readable name |
| sessions | INTEGER | |
| signups | INTEGER | |
| conversions | INTEGER | |
| revenue | REAL | |

**Channels:**
- `organic` — Organic Search
- `paid_search` — Paid Search
- `advisor` — Advisor Referral (~20% of traffic, 30% of direct revenue)
- `partner` — Partner/Institution
- `direct` — Direct traffic

---

### product_metrics
Daily metrics by product line.

| Column | Type | Notes |
|--------|------|-------|
| date | TEXT | YYYY-MM-DD |
| product_id | TEXT | core_curriculum, professional_cert, pathway_bundle, enterprise |
| product_name | TEXT | Human-readable name |
| units_sold | INTEGER | Units purchased |
| revenue | REAL | Product revenue |
| refunds | INTEGER | Refund count |
| refund_amount | REAL | Refund dollars |

**Products:**
- `core_curriculum` — Core Curriculum ($29.99)
- `professional_cert` — Professional Certification ($149.99)
- `pathway_bundle` — Pathway Bundle ($89.99)
- `enterprise` — Enterprise License ($499.99)

---

### support_tickets
Individual support tickets. **Key table for cancel/pause analysis.**

| Column | Type | Notes |
|--------|------|-------|
| ticket_id | INTEGER | Primary key |
| created_date | TEXT | YYYY-MM-DD |
| category | TEXT | cancellation, billing, technical, account, content |
| subcategory | TEXT | Specific issue type |
| channel | TEXT | Where ticket originated |
| sentiment_score | REAL | -1.0 to 0 (all complaints) |
| resolution_hours | REAL | Time to resolve |
| escalated | INTEGER | 0 or 1 |

**Categories:**
- `cancellation` — Cancel/pause issues (THE PROBLEM)
- `billing` — Charges, refunds, payment failures
- `technical` — Video, login, app issues
- `account` — Password, email changes
- `content` — Course quality issues

**Subcategories for cancellation:**
- `cancel_process_unclear`
- `cant_find_cancel_button`
- `unexpected_charge_after_cancel`
- `cancel_confirmation_missing`

**Channels:**
- `email` — Direct email support
- `chat` — Live chat
- `app_review` — App store reviews (PUBLIC - LLMs scrape)
- `social` — Social media mentions (PUBLIC - LLMs scrape)
- `partner_escalation` — Partner-reported issues (recent)

---

### weekly_funnel
Weekly conversion funnel metrics.

| Column | Type | Notes |
|--------|------|-------|
| week_start | TEXT | Monday of the week, YYYY-MM-DD |
| visitors | INTEGER | Unique visitors |
| product_views | INTEGER | Product page views |
| add_to_cart | INTEGER | Cart additions |
| checkout_started | INTEGER | Checkout initiations |
| checkout_completed | INTEGER | Completed purchases |
| conversion_rate | REAL | checkout_completed / visitors |

---

## Analysis Hints

### YoY Comparisons
Use 364-day lookback to align day-of-week:
```sql
date(date, '-364 days')
```

### The Cancel/Pause Story
Cancellation tickets have risen from ~15% to ~35% of all tickets since July 2025. The issue is concentrated in:
- Public channels (app_review, social) — what LLMs surface
- Billing cycle days (1st and 15th of month)
- Subcategory: `cant_find_cancel_button` is the top complaint

### Channel Performance
Advisor channel represents ~20% of sessions but ~30% of direct revenue (higher conversion rate). Partner channel is institutional deals (ASU, consortium).
