#!/usr/bin/env python3
"""
Generate sample data for the demo MCP server.

Creates a SQLite database with realistic LearnFlow metrics:
- 2 years of daily data (for YoY comparisons)
- Multiple channels and products
- Support tickets showing the cancel/pause reputation problem

Demo is set in Week 1 of the LearnFlow story — problems are surfacing.

Run this script to regenerate sample_data.db.
"""

import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "sample_data.db"

# Date range: 2 years of data ending Jan 26, 2026 (Week 1 of demo)
END_DATE = datetime(2026, 1, 26)
START_DATE = END_DATE - timedelta(days=730)  # ~2 years

# Products
PRODUCTS = [
    ("core_curriculum", "Core Curriculum", 29.99),
    ("professional_cert", "Professional Certification", 149.99),
    ("pathway_bundle", "Pathway Bundle", 89.99),
    ("enterprise", "Enterprise License", 499.99),
]

# Channels — advisor is at 30% (current state, not yet grown)
CHANNELS = [
    ("organic", "Organic Search", 0.32),
    ("paid_search", "Paid Search", 0.23),
    ("advisor", "Advisor Referral", 0.20),  # ~30% of direct (excl. partner)
    ("partner", "Partner/Institution", 0.15),
    ("direct", "Direct", 0.10),
]

# Support ticket categories
TICKET_CATEGORIES = {
    "cancellation": [
        ("cancel_process_unclear", 0.35),
        ("cant_find_cancel_button", 0.30),
        ("unexpected_charge_after_cancel", 0.20),
        ("cancel_confirmation_missing", 0.15),
    ],
    "billing": [
        ("unexpected_charge", 0.40),
        ("refund_request", 0.35),
        ("payment_failed", 0.25),
    ],
    "technical": [
        ("video_not_loading", 0.30),
        ("login_issues", 0.25),
        ("mobile_app_crash", 0.25),
        ("certificate_not_generated", 0.20),
    ],
    "account": [
        ("password_reset", 0.40),
        ("email_change", 0.30),
        ("merge_accounts", 0.30),
    ],
    "content": [
        ("course_quality", 0.50),
        ("missing_materials", 0.30),
        ("outdated_content", 0.20),
    ],
}

# Channels where tickets come from — public channels are the reputation risk
TICKET_CHANNELS = [
    ("email", 0.35),
    ("chat", 0.25),
    ("app_review", 0.20),      # Public — LLMs scrape these
    ("social", 0.12),          # Public — LLMs scrape these
    ("partner_escalation", 0.08),
]


def create_tables(conn):
    """Create the database schema."""
    cursor = conn.cursor()

    # Daily aggregate metrics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_metrics (
            date TEXT PRIMARY KEY,
            sessions INTEGER,
            new_users INTEGER,
            signups INTEGER,
            trials_started INTEGER,
            conversions INTEGER,
            revenue REAL,
            avg_order_value REAL
        )
    """)

    # Channel breakdown
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS channel_metrics (
            date TEXT,
            channel_id TEXT,
            channel_name TEXT,
            sessions INTEGER,
            signups INTEGER,
            conversions INTEGER,
            revenue REAL,
            PRIMARY KEY (date, channel_id)
        )
    """)

    # Product breakdown
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_metrics (
            date TEXT,
            product_id TEXT,
            product_name TEXT,
            units_sold INTEGER,
            revenue REAL,
            refunds INTEGER,
            refund_amount REAL,
            PRIMARY KEY (date, product_id)
        )
    """)

    # Support tickets — the cancel/pause reputation problem
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS support_tickets (
            ticket_id INTEGER PRIMARY KEY,
            created_date TEXT,
            category TEXT,
            subcategory TEXT,
            channel TEXT,
            sentiment_score REAL,
            resolution_hours REAL,
            escalated INTEGER
        )
    """)

    # Weekly funnel metrics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weekly_funnel (
            week_start TEXT PRIMARY KEY,
            visitors INTEGER,
            product_views INTEGER,
            add_to_cart INTEGER,
            checkout_started INTEGER,
            checkout_completed INTEGER,
            conversion_rate REAL
        )
    """)

    conn.commit()


def day_of_week_factor(date):
    """Traffic varies by day of week."""
    dow = date.weekday()
    factors = [1.0, 1.05, 1.08, 1.06, 0.95, 0.75, 0.70]  # Mon-Sun
    return factors[dow]


def seasonality_factor(date):
    """Seasonal patterns - higher in Jan, Sep; lower in summer."""
    month = date.month
    factors = {
        1: 1.25,   # New year resolution bump
        2: 1.10,
        3: 1.05,
        4: 1.00,
        5: 0.95,
        6: 0.85,   # Summer slowdown
        7: 0.80,
        8: 0.85,
        9: 1.15,   # Back to school
        10: 1.10,
        11: 1.00,
        12: 0.90,  # Holiday slowdown
    }
    return factors[month]


def growth_factor(date, start_date):
    """Year-over-year growth trend (~15% annually)."""
    days_elapsed = (date - start_date).days
    annual_growth = 0.15
    daily_growth = (1 + annual_growth) ** (1/365)
    return daily_growth ** days_elapsed


def generate_daily_metrics(conn):
    """Generate daily aggregate metrics."""
    cursor = conn.cursor()
    current = START_DATE

    base_sessions = 8000
    base_conversion_rate = 0.025

    while current <= END_DATE:
        # Apply factors
        dow = day_of_week_factor(current)
        season = seasonality_factor(current)
        growth = growth_factor(current, START_DATE)

        # Add some random noise
        noise = random.gauss(1.0, 0.08)

        # Calculate metrics
        sessions = int(base_sessions * dow * season * growth * noise)
        new_users = int(sessions * random.uniform(0.55, 0.65))
        signups = int(sessions * random.uniform(0.08, 0.12))
        trials = int(signups * random.uniform(0.40, 0.50))

        # Conversion rate with some variation
        conv_rate = base_conversion_rate * random.uniform(0.85, 1.15)
        # Slight improvement over time
        conv_rate *= (1 + 0.0001 * (current - START_DATE).days)

        conversions = int(sessions * conv_rate)
        aov = random.gauss(85, 15)
        revenue = conversions * aov

        cursor.execute("""
            INSERT INTO daily_metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            current.strftime("%Y-%m-%d"),
            sessions,
            new_users,
            signups,
            trials,
            conversions,
            round(revenue, 2),
            round(aov, 2)
        ))

        current += timedelta(days=1)

    conn.commit()


def generate_channel_metrics(conn):
    """Generate channel-level breakdown."""
    cursor = conn.cursor()

    # Get daily totals
    cursor.execute("SELECT date, sessions, signups, conversions, revenue FROM daily_metrics")
    daily_data = cursor.fetchall()

    for date, sessions, signups, conversions, revenue in daily_data:
        remaining_sessions = sessions
        remaining_signups = signups
        remaining_conversions = conversions
        remaining_revenue = revenue

        for i, (channel_id, channel_name, share) in enumerate(CHANNELS):
            is_last = (i == len(CHANNELS) - 1)

            if is_last:
                ch_sessions = remaining_sessions
                ch_signups = remaining_signups
                ch_conversions = remaining_conversions
                ch_revenue = remaining_revenue
            else:
                # Add some variance to share
                actual_share = share * random.uniform(0.85, 1.15)
                ch_sessions = int(sessions * actual_share)
                ch_signups = int(signups * actual_share)
                ch_conversions = int(conversions * actual_share)
                ch_revenue = revenue * actual_share

                remaining_sessions -= ch_sessions
                remaining_signups -= ch_signups
                remaining_conversions -= ch_conversions
                remaining_revenue -= ch_revenue

            cursor.execute("""
                INSERT INTO channel_metrics VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                date,
                channel_id,
                channel_name,
                ch_sessions,
                ch_signups,
                ch_conversions,
                round(ch_revenue, 2)
            ))

    conn.commit()


def generate_product_metrics(conn):
    """Generate product-level breakdown."""
    cursor = conn.cursor()

    # Get daily totals
    cursor.execute("SELECT date, conversions, revenue FROM daily_metrics")
    daily_data = cursor.fetchall()

    # Product mix
    for date_str, total_conversions, total_revenue in daily_data:
        date = datetime.strptime(date_str, "%Y-%m-%d")

        shares = {
            "core_curriculum": 0.45,
            "professional_cert": 0.25,
            "pathway_bundle": 0.20,
            "enterprise": 0.10,
        }

        remaining_units = total_conversions
        remaining_revenue = total_revenue

        for i, (product_id, product_name, base_price) in enumerate(PRODUCTS):
            is_last = (i == len(PRODUCTS) - 1)

            if is_last:
                units = remaining_units
                revenue = remaining_revenue
            else:
                share = shares[product_id] * random.uniform(0.9, 1.1)
                units = int(total_conversions * share)
                price_paid = base_price * random.uniform(0.85, 1.0)
                revenue = units * price_paid

                remaining_units -= units
                remaining_revenue -= revenue

            # Refunds (2-4% rate)
            refund_rate = random.uniform(0.02, 0.04)
            refunds = int(units * refund_rate)
            refund_amount = refunds * base_price * 0.9

            cursor.execute("""
                INSERT INTO product_metrics VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                date_str,
                product_id,
                product_name,
                units,
                round(revenue, 2),
                refunds,
                round(refund_amount, 2)
            ))

    conn.commit()


def generate_support_tickets(conn):
    """
    Generate support tickets showing the cancel/pause reputation problem.

    Key patterns:
    1. Cancellation complaints rising steadily over past 6 months
    2. Public channels (app_review, social) have worst cancellation sentiment
    3. Spikes around billing dates (1st and 15th)
    4. Partner escalations appear in recent weeks (ASU legal concern)
    """
    cursor = conn.cursor()

    ticket_id = 1
    current = START_DATE

    # Base daily ticket volume (grows with business)
    base_daily_tickets = 25

    while current <= END_DATE:
        growth = growth_factor(current, START_DATE)
        dow = day_of_week_factor(current)

        # Calculate base tickets for the day
        daily_tickets = int(base_daily_tickets * growth * dow * random.uniform(0.8, 1.2))

        # --- THE KEY PATTERN: Cancellation complaints rising ---
        # Calculate how far into the "problem period" we are
        # Problem started accelerating ~6 months ago (mid-July 2025)
        problem_start = datetime(2025, 7, 15)
        if current >= problem_start:
            days_into_problem = (current - problem_start).days
            # Cancellation share grows from 15% to 35% over 6 months
            cancel_share_boost = min(days_into_problem / 180, 1.0) * 0.20
        else:
            cancel_share_boost = 0

        # Spike around billing dates (1st and 15th)
        is_billing_day = current.day in [1, 2, 15, 16]
        if is_billing_day:
            daily_tickets = int(daily_tickets * 1.4)
            cancel_share_boost += 0.10

        # Category distribution (cancellation gets boosted)
        category_weights = {
            "cancellation": 0.15 + cancel_share_boost,  # Grows over time
            "billing": 0.25,
            "technical": 0.30,
            "account": 0.15,
            "content": 0.15 - cancel_share_boost,  # Shrinks proportionally
        }

        # Normalize weights
        total_weight = sum(category_weights.values())
        category_weights = {k: v/total_weight for k, v in category_weights.items()}

        for _ in range(daily_tickets):
            # Pick category
            rand = random.random()
            cumulative = 0
            category = "technical"
            for cat, weight in category_weights.items():
                cumulative += weight
                if rand <= cumulative:
                    category = cat
                    break

            # Pick subcategory
            subcats = TICKET_CATEGORIES[category]
            subcat_rand = random.random()
            cumulative = 0
            subcategory = subcats[0][0]
            for subcat, weight in subcats:
                cumulative += weight
                if subcat_rand <= cumulative:
                    subcategory = subcat
                    break

            # Pick channel — cancellation issues more likely on public channels
            if category == "cancellation":
                # Cancellation complaints disproportionately show up in public channels
                channel_weights = [
                    ("email", 0.25),
                    ("chat", 0.15),
                    ("app_review", 0.30),    # Over-indexed
                    ("social", 0.20),        # Over-indexed
                    ("partner_escalation", 0.10),
                ]
            else:
                channel_weights = TICKET_CHANNELS

            chan_rand = random.random()
            cumulative = 0
            channel = "email"
            for chan, weight in channel_weights:
                cumulative += weight
                if chan_rand <= cumulative:
                    channel = chan
                    break

            # Partner escalations only appear recently (past 2 weeks)
            # This is the ASU legal concern surfacing
            if channel == "partner_escalation":
                if current < datetime(2026, 1, 10):
                    channel = "email"  # Fall back to email for older tickets

            # Sentiment score (-1.0 to 0, all are complaints)
            # Cancellation issues have worse sentiment, especially on public channels
            base_sentiment = random.uniform(-0.7, -0.3)
            if category == "cancellation":
                base_sentiment -= 0.2
            if channel in ["app_review", "social"]:
                base_sentiment -= 0.1
            sentiment = max(-1.0, min(0, base_sentiment))

            # Resolution time (hours)
            base_resolution = random.gauss(24, 12)
            if category == "cancellation":
                base_resolution *= 1.5  # Cancellation takes longer to resolve
            if channel == "partner_escalation":
                base_resolution *= 0.5  # Partner issues get prioritized
            resolution_hours = max(1, base_resolution)

            # Escalation flag
            escalated = 0
            if channel == "partner_escalation":
                escalated = 1
            elif sentiment < -0.8 and random.random() < 0.3:
                escalated = 1

            cursor.execute("""
                INSERT INTO support_tickets VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ticket_id,
                current.strftime("%Y-%m-%d"),
                category,
                subcategory,
                channel,
                round(sentiment, 2),
                round(resolution_hours, 1),
                escalated
            ))

            ticket_id += 1

        current += timedelta(days=1)

    conn.commit()


def generate_weekly_funnel(conn):
    """Generate weekly funnel metrics."""
    cursor = conn.cursor()

    current = START_DATE
    # Align to Monday
    while current.weekday() != 0:
        current += timedelta(days=1)

    while current <= END_DATE - timedelta(days=6):
        week_end = current + timedelta(days=6)

        cursor.execute("""
            SELECT SUM(sessions), SUM(conversions)
            FROM daily_metrics
            WHERE date >= ? AND date <= ?
        """, (current.strftime("%Y-%m-%d"), week_end.strftime("%Y-%m-%d")))

        sessions, conversions = cursor.fetchone()

        if sessions:
            visitors = sessions
            product_views = int(visitors * random.uniform(0.35, 0.45))
            add_to_cart = int(product_views * random.uniform(0.25, 0.35))
            checkout_started = int(add_to_cart * random.uniform(0.55, 0.65))
            checkout_completed = conversions or 0
            conv_rate = checkout_completed / visitors if visitors > 0 else 0

            cursor.execute("""
                INSERT INTO weekly_funnel VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                current.strftime("%Y-%m-%d"),
                visitors,
                product_views,
                add_to_cart,
                checkout_started,
                checkout_completed,
                round(conv_rate, 4)
            ))

        current += timedelta(days=7)

    conn.commit()


def main():
    # Remove existing database
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)

    print("Creating tables...")
    create_tables(conn)

    print("Generating daily metrics...")
    generate_daily_metrics(conn)

    print("Generating channel metrics...")
    generate_channel_metrics(conn)

    print("Generating product metrics...")
    generate_product_metrics(conn)

    print("Generating support tickets...")
    generate_support_tickets(conn)

    print("Generating weekly funnel...")
    generate_weekly_funnel(conn)

    # Verify
    cursor = conn.cursor()

    print("\n--- Data Summary ---")

    cursor.execute("SELECT COUNT(*) FROM daily_metrics")
    print(f"daily_metrics: {cursor.fetchone()[0]} rows")

    cursor.execute("SELECT MIN(date), MAX(date) FROM daily_metrics")
    min_date, max_date = cursor.fetchone()
    print(f"Date range: {min_date} to {max_date}")

    cursor.execute("SELECT COUNT(*) FROM support_tickets")
    print(f"support_tickets: {cursor.fetchone()[0]} rows")

    # Show the cancel/pause trend
    print("\n--- Cancellation Ticket Trend (Monthly) ---")
    cursor.execute("""
        SELECT
            strftime('%Y-%m', created_date) as month,
            COUNT(*) as total_tickets,
            SUM(CASE WHEN category = 'cancellation' THEN 1 ELSE 0 END) as cancel_tickets,
            ROUND(100.0 * SUM(CASE WHEN category = 'cancellation' THEN 1 ELSE 0 END) / COUNT(*), 1) as cancel_pct
        FROM support_tickets
        WHERE created_date >= '2025-07-01'
        GROUP BY month
        ORDER BY month
    """)
    print("Month      | Total | Cancel | Cancel %")
    print("-----------|-------|--------|----------")
    for row in cursor.fetchall():
        print(f"{row[0]}  | {row[1]:5} | {row[2]:6} | {row[3]:6}%")

    conn.close()
    print(f"\nDatabase saved to: {DB_PATH}")


if __name__ == "__main__":
    random.seed(42)  # Reproducible data
    main()
