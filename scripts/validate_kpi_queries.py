from pathlib import Path

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "customer_support.duckdb"
KPI_PATH = PROJECT_ROOT / "sql" / "kpi_queries.sql"


def main():
    """Run and preview KPI queries."""
    queries = [
        "Resolution Rate",
        "Observed Dissatisfaction Rate",
        "Predicted Dissatisfaction Rate",
        "Sentiment Distribution",
        "Emerging Themes",
    ]

    sql_statements = [
        statement.strip()
        for statement in KPI_PATH.read_text(
            encoding="utf-8"
        ).split(";")
        if statement.strip()
    ]

    if len(sql_statements) != len(queries):
        raise ValueError(
            f"Expected {len(queries)} SQL queries, "
            f"but found {len(sql_statements)}."
        )

    conn = duckdb.connect(str(DATABASE_PATH))

    try:
        for name, query in zip(queries, sql_statements):
            print(f"\n{'=' * 60}")
            print(name)
            print("=" * 60)

            result = conn.execute(query).fetchdf()
            print(result.head(10).to_string(index=False))

            print(f"\nRows returned: {len(result)}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()