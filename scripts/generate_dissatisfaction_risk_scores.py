from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CLEANED_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "customer_support_tickets_cleaned.csv"
)

SENTIMENT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ticket_sentiment.csv"
)

TOPICS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "customer_support_topics.csv"
)

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "dissatisfaction_risk_model.pkl"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ticket_dissatisfaction_risk.csv"
)


def validate_ticket_ids(dataframe, ticket_id_column, dataset_name):
    """Validate ticket ID completeness and uniqueness."""
    if dataframe[ticket_id_column].isna().any():
        raise ValueError(
            f"{dataset_name} contains missing Ticket IDs."
        )

    if dataframe[ticket_id_column].duplicated().any():
        raise ValueError(
            f"{dataset_name} contains duplicate Ticket IDs."
        )


def main():
    """Generate dissatisfaction-risk scores for all tickets."""
    cleaned_df = pd.read_csv(CLEANED_DATA_PATH)
    sentiment_df = pd.read_csv(SENTIMENT_PATH)
    topics_df = pd.read_csv(TOPICS_PATH)

    validate_ticket_ids(
        cleaned_df,
        "Ticket ID",
        "Cleaned ticket dataset",
    )

    validate_ticket_ids(
        sentiment_df,
        "ticket_id",
        "Sentiment dataset",
    )

    validate_ticket_ids(
        topics_df,
        "Ticket ID",
        "Topic dataset",
    )

    sentiment_df = sentiment_df.rename(
        columns={"ticket_id": "Ticket ID"}
    )

    modeling_df = (
        cleaned_df[
            [
                "Ticket ID",
                "Ticket Priority",
                "Ticket Channel",
            ]
        ]
        .merge(
            sentiment_df,
            on="Ticket ID",
            how="left",
            validate="one_to_one",
        )
        .merge(
            topics_df[
                [
                    "Ticket ID",
                    "topic_id",
                ]
            ],
            on="Ticket ID",
            how="left",
            validate="one_to_one",
        )
    )

    expected_rows = len(cleaned_df)

    if len(modeling_df) != expected_rows:
        raise ValueError(
            "Inference dataset row count does not match "
            "the cleaned ticket dataset."
        )

    required_features = [
        "Ticket Priority",
        "Ticket Channel",
        "sentiment_label",
        "topic_id",
        "sentiment_score",
    ]

    if modeling_df[required_features].isna().any().any():
        missing_counts = (
            modeling_df[required_features]
            .isna()
            .sum()
        )

        raise ValueError(
            "Missing values found in model input features:\n"
            f"{missing_counts}"
        )

    model = joblib.load(MODEL_PATH)

    X_inference = modeling_df[required_features]

    dissatisfaction_risk_score = model.predict_proba(
        X_inference
    )[:, 1]

    output_df = pd.DataFrame(
        {
            "ticket_id": modeling_df["Ticket ID"],
            "dissatisfaction_risk_score": (
                dissatisfaction_risk_score
            ),
        }
    )

    if len(output_df) != expected_rows:
        raise ValueError(
            "Output row count does not match "
            "the cleaned ticket dataset."
        )

    if output_df["ticket_id"].duplicated().any():
        raise ValueError(
            "Output contains duplicate Ticket IDs."
        )

    if output_df["dissatisfaction_risk_score"].isna().any():
        raise ValueError(
            "Output contains missing dissatisfaction-risk scores."
        )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(
        "Dissatisfaction-risk scores generated successfully."
    )
    print(f"Rows: {len(output_df)}")
    print(
        "Unique Ticket IDs: "
        f"{output_df['ticket_id'].nunique()}"
    )
    print(
        "Missing risk scores: "
        f"{output_df['dissatisfaction_risk_score'].isna().sum()}"
    )
    print(
        "Minimum risk score: "
        f"{output_df['dissatisfaction_risk_score'].min():.6f}"
    )
    print(
        "Maximum risk score: "
        f"{output_df['dissatisfaction_risk_score'].max():.6f}"
    )


if __name__ == "__main__":
    main()