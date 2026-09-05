from pathlib import Path

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "customer_support.duckdb"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "powerbi"
)


def main():
    """Export star schema tables for Power BI."""

    tables = [
        "dim_category",
        "dim_channel",
        "dim_priority",
        "dim_date",
        "fact_ticket",
    ]

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    conn = duckdb.connect(str(DATABASE_PATH))

    try:
        for table_name in tables:
            output_path = (
                OUTPUT_DIR
                / f"{table_name}.csv"
            )

            conn.execute(
                f"""
                COPY {table_name}
                TO '{output_path.as_posix()}'
                (HEADER, DELIMITER ',')
                """
            )

            print(
                f"Exported: {output_path.name}"
            )

    finally:
        conn.close()


if __name__ == "__main__":
    main()