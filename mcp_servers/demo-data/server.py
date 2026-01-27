#!/usr/bin/env python3
"""
Demo Data MCP Server

A lightweight SQLite MCP server for demoing the ProductAIFlows analyze skill.
Ships with sample LearnFlow metrics data. Swap in your own database by replacing sample_data.db.
"""

import sqlite3
import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("demo-data")

# Database path (same directory as this script)
DB_PATH = Path(__file__).parent / "sample_data.db"


def get_connection():
    """Get a database connection."""
    return sqlite3.connect(DB_PATH)


@mcp.tool()
def query(sql: str) -> str:
    """
    Execute a SQL query against the demo database.

    Args:
        sql: The SQL query to execute (SELECT only for safety)

    Returns:
        Query results as a formatted table, or error message
    """
    # Safety check - only allow SELECT queries
    sql_upper = sql.strip().upper()
    if not sql_upper.startswith("SELECT") and not sql_upper.startswith("WITH"):
        return "Error: Only SELECT queries are allowed for safety."

    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()

        if not rows:
            return "Query returned no results."

        # Get column names
        columns = [description[0] for description in cursor.description]

        # Format as CSV for easy parsing
        result_lines = [",".join(columns)]
        for row in rows:
            result_lines.append(",".join(str(val) if val is not None else "" for val in row))

        conn.close()
        return "\n".join(result_lines)

    except Exception as e:
        return f"Error executing query: {str(e)}"


@mcp.tool()
def list_tables() -> str:
    """
    List all tables in the demo database.

    Returns:
        List of table names with row counts
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()

        result = []
        for (table_name,) in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            result.append(f"- {table_name} ({count:,} rows)")

        conn.close()
        return "Tables in database:\n" + "\n".join(result)

    except Exception as e:
        return f"Error listing tables: {str(e)}"


@mcp.tool()
def describe_table(table_name: str) -> str:
    """
    Show the schema for a specific table.

    Args:
        table_name: Name of the table to describe

    Returns:
        Column names, types, and sample values
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Get column info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        if not columns:
            return f"Table '{table_name}' not found."

        # Get sample row
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
        sample = cursor.fetchone()

        result = [f"Schema for {table_name}:", ""]
        result.append("| Column | Type | Sample |")
        result.append("|--------|------|--------|")

        for col in columns:
            col_name = col[1]
            col_type = col[2]
            sample_val = sample[col[0]] if sample else "NULL"
            result.append(f"| {col_name} | {col_type} | {sample_val} |")

        conn.close()
        return "\n".join(result)

    except Exception as e:
        return f"Error describing table: {str(e)}"


@mcp.tool()
def get_date_range(table_name: str, date_column: str = "date") -> str:
    """
    Get the date range available in a table.

    Args:
        table_name: Name of the table
        date_column: Name of the date column (default: 'date')

    Returns:
        Min and max dates in the table
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(f"SELECT MIN({date_column}), MAX({date_column}) FROM {table_name}")
        min_date, max_date = cursor.fetchone()

        conn.close()
        return f"Date range in {table_name}: {min_date} to {max_date}"

    except Exception as e:
        return f"Error getting date range: {str(e)}"


if __name__ == "__main__":
    mcp.run()
