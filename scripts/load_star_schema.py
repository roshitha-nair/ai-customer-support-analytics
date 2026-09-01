from pathlib import Path

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "customer_support.duckdb"
SCHEMA_PATH = PROJECT_ROOT / "sql" / "schema.sql"


def main():
    """Build and populate the customer support star schema."""
    conn = duckdb.connect(str(DATABASE_PATH))

    try:
        schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
        conn.execute(schema_sql)

        conn.execute(
            """
            INSERT INTO dim_category
            SELECT
                ROW_NUMBER() OVER (ORDER BY "Ticket Type") AS category_key,
                "Ticket Type" AS ticket_type
            FROM (
                SELECT DISTINCT "Ticket Type"
                FROM processed_customer_support_tickets
            )
            """
        )

        conn.execute(
            """
            INSERT INTO dim_channel
            SELECT
                ROW_NUMBER() OVER (ORDER BY "Ticket Channel") AS channel_key,
                "Ticket Channel" AS ticket_channel
            FROM (
                SELECT DISTINCT "Ticket Channel"
                FROM processed_customer_support_tickets
            )
            """
        )

        conn.execute(
            """
            INSERT INTO dim_priority
            SELECT
                ROW_NUMBER() OVER (ORDER BY "Ticket Priority") AS priority_key,
                "Ticket Priority" AS ticket_priority
            FROM (
                SELECT DISTINCT "Ticket Priority"
                FROM processed_customer_support_tickets
            )
            """
        )

        conn.execute(
            """
            INSERT INTO dim_date
            SELECT
                CAST(
                    STRFTIME("Date of Purchase", '%Y%m%d')
                    AS INTEGER
                ) AS date_key,
                "Date of Purchase" AS full_date,
                EXTRACT(YEAR FROM "Date of Purchase") AS year,
                EXTRACT(QUARTER FROM "Date of Purchase") AS quarter,
                EXTRACT(MONTH FROM "Date of Purchase") AS month,
                STRFTIME("Date of Purchase", '%B') AS month_name
            FROM (
                SELECT DISTINCT "Date of Purchase"
                FROM processed_customer_support_tickets
            )
            """
        )

        conn.execute(
            """
            INSERT INTO fact_ticket (
                ticket_id,
                category_key,
                channel_key,
                priority_key,
                purchase_date_key,
                customer_age,
                customer_gender,
                product_purchased,
                ticket_subject,
                cleaned_ticket_description,
                ticket_status,
                resolution,
                first_response_time,
                time_to_resolution,
                customer_satisfaction_rating,
                has_first_response,
                is_resolved,
                has_csat,
                is_dissatisfied
            )
            SELECT
                src."Ticket ID" AS ticket_id,
                cat.category_key,
                ch.channel_key,
                pri.priority_key,
                dt.date_key AS purchase_date_key,
                src."Customer Age" AS customer_age,
                src."Customer Gender" AS customer_gender,
                src."Product Purchased" AS product_purchased,
                src."Ticket Subject" AS ticket_subject,
                src."Cleaned Ticket Description" AS cleaned_ticket_description,
                src."Ticket Status" AS ticket_status,
                src."Resolution" AS resolution,
                src."First Response Time" AS first_response_time,
                src."Time to Resolution" AS time_to_resolution,
                src."Customer Satisfaction Rating"
                    AS customer_satisfaction_rating,
                src."Has First Response" AS has_first_response,
                src."Is Resolved" AS is_resolved,
                src."Has CSAT" AS has_csat,
                src.is_dissatisfied
            FROM processed_customer_support_tickets AS src
            JOIN dim_category AS cat
                ON src."Ticket Type" = cat.ticket_type
            JOIN dim_channel AS ch
                ON src."Ticket Channel" = ch.ticket_channel
            JOIN dim_priority AS pri
                ON src."Ticket Priority" = pri.ticket_priority
            JOIN dim_date AS dt
                ON src."Date of Purchase" = dt.full_date
            """
        )

        print("Star schema created and populated successfully.")

    finally:
        conn.close()


if __name__ == "__main__":
    main()