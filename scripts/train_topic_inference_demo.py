from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CLEANED_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "customer_support_tickets_cleaned.csv"
)

TOPIC_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "customer_support_topics.csv"
)

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "topic_inference_demo.pkl"
)


def main():
    tickets = pd.read_csv(CLEANED_DATA_PATH)
    topics = pd.read_csv(TOPIC_DATA_PATH)

    df = tickets[
        ["Ticket ID", "Cleaned Ticket Description"]
    ].merge(
        topics[
            ["Ticket ID", "topic_id", "topic_label"]
        ],
        on="Ticket ID",
        validate="one_to_one",
    )

    df = df.dropna(
        subset=[
            "Cleaned Ticket Description",
            "topic_id",
        ]
    )

    X = df["Cleaned Ticket Description"].astype(str)
    y = df["topic_id"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    model = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    min_df=3,
                    max_features=20000,
                    sublinear_tf=True,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    print(f"Training rows: {len(X_train)}")
    print(f"Validation rows: {len(X_test)}")
    print(f"Topic classes: {y.nunique()}")
    print(f"Validation accuracy: {accuracy:.4f}")
    print()
    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0,
        )
    )

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        model,
        MODEL_PATH,
    )

    print(
        f"Demo topic inference model saved to: {MODEL_PATH}"
    )


if __name__ == "__main__":
    main()