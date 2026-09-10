from pathlib import Path
import re

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from transformers import pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "dissatisfaction_risk_model.pkl"
)

TOPIC_INFERENCE_MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "topic_inference_demo.pkl"
)


# Human-readable labels assigned during topic interpretation.
TOPIC_LABELS = {
    -1: "Other or Unclassified Support Content",
    0: "Issue After Firmware Update",
    1: "App Issue Persists After Troubleshooting",
    2: "Account Access and Password Issues",
    3: "Data Loss and File Recovery",
    4: "Error Messages and Error Codes",
    5: "Unable to Perform Desired Action",
    6: "Wi-Fi Connectivity Issues",
    7: "Security and Data Safety Concerns",
    8: "Charging Problems",
    9: "Battery Life Issues",
    10: "Unstable Internet Connection",
    11: "Software Bugs and Data Loss",
    12: "Application Crashes and Software Bugs",
    13: "General Hardware Malfunction",
    14: "Software Freezing Issues",
    15: "Software Update Availability",
    16: "Screen and Display Problems",
    17: "Urgent Issue Affecting Productivity",
    18: "Device Not Turning On",
    19: "Urgent Issue Affecting Productivity",
    20: "Repair or Replacement Concerns",
    21: "Refund Issues",
    22: "Invoice and Payment Issues",
    23: "Email and Account Issues",
    24: "Other Support Content",
    25: "Refund and Exchange Requests",
    26: "Other Support Content",
    27: "Other Support Content",
    28: "Other Support Content",
}


class PredictionRequest(BaseModel):
    text: str = Field(..., min_length=1)
    priority: str = Field(..., min_length=1)
    channel: str = Field(..., min_length=1)


class PredictionResponse(BaseModel):
    sentiment_label: str
    sentiment_score: float
    topic_id: int
    topic_label: str
    dissatisfaction_risk_score: float


app = FastAPI(
    title="Customer Support AI Demo",
    description=(
        "Local inference demo for sentiment, topic inference, "
        "and dissatisfaction-risk scoring."
    ),
    version="1.0.0",
)


# Load the existing project models once when the API starts.
sentiment_pipeline = pipeline(
    "sentiment-analysis"
)

topic_inference_model = joblib.load(
    TOPIC_INFERENCE_MODEL_PATH
)

risk_model = joblib.load(
    MODEL_PATH
)


def clean_topic_text(text):
    """Apply the topic-modeling preprocessing used by the project."""

    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"\b\S+@\S+\.\S+\b", " ", text)

    text = re.sub(r"\{[^}]*\}", " ", text)
    text = re.sub(
        r"\bproduct_purch(?:ased)?\b|\bproduct_name\b",
        " ",
        text,
        flags=re.IGNORECASE,
    )

    generic_patterns = [
        r"\bi'?m having an issue with (?:the|my)?\b",
        r"\bi'?m facing a problem with (?:the|my)?\b",
        r"\bplease assist\b",
        r"\bplease help\b",
        r"\bthank you\b",
        r"\bthanks\b",
    ]

    for pattern in generic_patterns:
        text = re.sub(
            pattern,
            " ",
            text,
            flags=re.IGNORECASE,
        )

    artifact_patterns = [
        r"please enable javascript to view the comments powered by disqus",
        r"comments powered by disqus",
        r"\b(?:std|void|include|stdioh|fuser)\b",
        r"xda-developer",
    ]

    for pattern in artifact_patterns:
        text = re.sub(
            pattern,
            " ",
            text,
            flags=re.IGNORECASE,
        )

    text = re.sub(r"\s+", " ", text).strip()

    return text


@app.get("/")
def root():
    """Return basic API information."""

    return {
        "name": "Customer Support AI Demo",
        "status": "running",
        "endpoint": "/predict",
    }


@app.get("/health")
def health():
    """Return API health status."""

    return {"status": "healthy"}


@app.post(
    "/predict",
    response_model=PredictionResponse,
)
def predict(request: PredictionRequest):
    """Generate sentiment, topic, and dissatisfaction-risk predictions."""

    text = request.text.strip()

    if not text:
        raise HTTPException(
            status_code=400,
            detail="Ticket text cannot be empty.",
        )

    # Generate sentiment using the project's pretrained
    # Hugging Face sentiment-analysis approach.
    sentiment_result = sentiment_pipeline(
        text,
        truncation=True,
    )[0]

    sentiment_label = sentiment_result["label"]
    sentiment_score = float(
        sentiment_result["score"]
    )

    # Apply the same topic-specific text cleaning used
    # before fitting the original topic model.
    topic_text = clean_topic_text(text)

    if not topic_text:
        topic_text = text

    # Infer a topic using the compatibility classifier
    # trained from the validated project topic assignments.
    topic_id = int(
        topic_inference_model.predict(
            [topic_text]
        )[0]
    )

    topic_label = TOPIC_LABELS.get(
        topic_id,
        "Other or Unclassified Support Content",
    )

    # Reconstruct the exact feature structure expected
    # by the existing dissatisfaction-risk model.
    model_input = pd.DataFrame(
        {
            "Ticket Priority": [request.priority],
            "Ticket Channel": [request.channel],
            "sentiment_label": [sentiment_label],
            "topic_id": [topic_id],
            "sentiment_score": [sentiment_score],
        }
    )

    dissatisfaction_risk_score = float(
        risk_model.predict_proba(model_input)[:, 1][0]
    )

    return PredictionResponse(
        sentiment_label=sentiment_label,
        sentiment_score=sentiment_score,
        topic_id=topic_id,
        topic_label=topic_label,
        dissatisfaction_risk_score=dissatisfaction_risk_score,
    )