from pathlib import Path

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "customer_support.duckdb"


def main():
    """Independently recompute core dashboard metrics."""

    conn = duckdb.connect(str(DATABASE_PATH))

    try:
        query = """
        SELECT
            COUNT(*) AS total_tickets,

            ROUND(
                100.0 * SUM(is_resolved) / COUNT(*),
                2
            ) AS resolution_rate_pct,

            SUM(has_csat) AS csat_observed_tickets,

            SUM(
                CASE
                    WHEN is_dissatisfied = 1 THEN 1
                    ELSE 0
                END
            ) AS dissatisfied_tickets,

            ROUND(
                100.0
                * SUM(
                    CASE
                        WHEN is_dissatisfied = 1 THEN 1
                        ELSE 0
                    END
                )
                / NULLIF(SUM(has_csat), 0),
                2
            ) AS observed_dissatisfaction_rate_pct,

            ROUND(
                100.0 * AVG(dissatisfaction_risk_score),
                2
            ) AS predicted_dissatisfaction_rate_pct,

            SUM(
                CASE
                    WHEN sentiment_label = 'NEGATIVE' THEN 1
                    ELSE 0
                END
            ) AS negative_tickets,

            SUM(
                CASE
                    WHEN sentiment_label = 'POSITIVE' THEN 1
                    ELSE 0
                END
            ) AS positive_tickets,

            ROUND(
                100.0
                * SUM(
                    CASE
                        WHEN sentiment_label = 'NEGATIVE' THEN 1
                        ELSE 0
                    END
                )
                / COUNT(*),
                2
            ) AS negative_sentiment_pct,

            ROUND(
                100.0
                * SUM(
                    CASE
                        WHEN sentiment_label = 'POSITIVE' THEN 1
                        ELSE 0
                    END
                )
                / COUNT(*),
                2
            ) AS positive_sentiment_pct

        FROM fact_ticket;
        """

        result = conn.execute(query).fetchdf()

        print("\n" + "=" * 60)
        print("Independent Dashboard KPI Recalculation")
        print("=" * 60)
        print(result.to_string(index=False))

    finally:
        conn.close()


if __name__ == "__main__":
    main()