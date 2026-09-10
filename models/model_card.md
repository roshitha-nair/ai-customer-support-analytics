# AI Model Cards

This document describes the three AI components used in the
AI-Powered Customer Support Analytics project:

1. Sentiment Classification
2. Topic Discovery
3. Dissatisfaction-Risk Modeling

The three components serve different analytical purposes and should
not be interpreted as equivalent types of predictions.

- Sentiment is a model-derived text classification signal.
- Topics are exploratory model-generated support themes.
- Dissatisfaction risk is a supervised prediction based on an
  observed CSAT-derived target.

All AI outputs are intended to support analytical interpretation and
ticket prioritization rather than autonomous customer-impact decisions.

## 1. Sentiment Classification

### Model Overview

The sentiment component classifies customer support ticket
descriptions using a pretrained Hugging Face sentiment-analysis
pipeline.

The model is applied to the cleaned ticket-description data and
produces a sentiment label and model score for every ticket.

The sentiment output is used as an analytical feature for:

- Sentiment reporting
- Issue analysis
- Channel-level sentiment analysis
- Dissatisfaction-risk modeling
- AI-driven support insights

The sentiment model is not fine-tuned on this project dataset.

### Model

- Model approach: Pretrained Hugging Face sentiment-analysis pipeline
- Inference population: 8,469 tickets
- Training performed for this project: No
- Fine-tuning performed for this project: No

The project intentionally uses a pretrained model rather than
training a custom sentiment classifier. The objective is to apply,
validate, and document the model appropriately within the customer
support analytics pipeline.

### Inputs

The sentiment model receives:

- Cleaned Ticket Description

The cleaning process removes or standardizes problematic text
patterns before downstream analysis.

### Outputs

The sentiment pipeline produces:

- `sentiment_label`
- `sentiment_score`

The resulting output is stored in:

```text
data/processed/ticket_sentiment.csv
```

The output is integrated into the analytical star schema as:

- `sentiment_label`
- `sentiment_score`

### Observed Results

The sentiment pipeline produced results for all 8,469 tickets:

| Sentiment | Tickets |  Share |
| --------- | ------: | -----: |
| NEGATIVE  |   7,733 | 91.31% |
| POSITIVE  |     736 |  8.69% |

Missing sentiment labels: 0

Missing sentiment scores: 0

The strongly negative distribution should be interpreted in the
context of the source data, which consists primarily of customer
support problem descriptions rather than general conversational text.

### Validation

A targeted manual validation sample of 20 tickets was reviewed and
compared against the model output.

Results:

- Agreements: 10 / 20
- Agreement rate: 50.0%

This was a targeted diagnostic check rather than a statistically
representative validation study.

The 50.0% agreement rate should therefore not be interpreted as the
overall accuracy of the sentiment model.

### Known Failure Modes

The validation and data-quality review identified several situations
where general-domain sentiment inference may be unreliable:

- Templated ticket language
- Very short or incomplete descriptions
- Noisy ticket text
- Surface-level positive wording inside otherwise problematic
  support requests
- Domain-specific customer-support language
- Scraped or unrelated text artifacts
- Placeholder text

Customer-support tickets frequently describe problems using neutral
or positive words even when the underlying customer experience is
negative. A general-domain sentiment model may therefore miss the
context of dissatisfaction.

### Limitations

- The sentiment model is pretrained rather than domain-fine-tuned.
- The model was not trained specifically on this customer-support
  dataset.
- The manual validation sample is small.
- The validation result is diagnostic and not an estimate of
  production accuracy.
- Sentiment predictions should not be treated as ground truth.
- `sentiment_score` is the model score associated with the predicted
  sentiment output and should not be interpreted as a calibrated
  probability of customer sentiment.

### Intended Use

The sentiment output is intended for:

- Analytical segmentation
- Support issue analysis
- Channel-level sentiment comparison
- Dashboard reporting
- Feature engineering for dissatisfaction-risk modeling

It is not intended to:

- Determine customer intent with certainty
- Replace human interpretation of ticket context
- Serve as a definitive measure of customer satisfaction
- Make automated customer-impact decisions

## 2. Topic Discovery

### Model Overview

The topic component discovers recurring support themes from customer
ticket descriptions using BERTopic.

The approach is unsupervised. Topic labels were interpreted and
assigned manually after reviewing the discovered clusters.

This component was selected because the available ticket metadata did
not provide sufficiently reliable ground-truth issue labels for the
intended topic-discovery objective.

The topic output is therefore an exploratory analytical classification
rather than a supervised ground-truth issue category.

### Model

- Model approach: BERTopic
- Modeling objective: Unsupervised support-theme discovery
- Topic count after topic reduction: 30 topic IDs
- Inference/output population: 8,469 tickets
- Outlier topic: `-1`

The topic model was developed using the cleaned ticket-description
text.

Topic-specific preprocessing was applied to reduce the influence of
noise and repeated non-informative patterns, including:

- HTML
- URLs
- Email addresses
- Placeholder expressions
- Product placeholder artifacts
- Generic support boilerplate
- Scraped/code-like artifacts

The topic representation uses text features suitable for recurring
support-theme discovery.

### Outputs

The topic pipeline produces:

- `topic_id`
- `topic_label`

The resulting output is stored in:

```text
data/processed/customer_support_topics.csv
```

The output is integrated into the analytical star schema as:

- `topic_id`
- `topic_label`

### Topic Structure

The final output contains:

- 8,469 ticket assignments
- 30 topic IDs
- No missing topic labels

The topic IDs include:

```text
-1 through 28
```

with `-1` representing the outlier topic.

The outlier topic is labeled:

```text
Other or Unclassified Support Content
```

### Representative Discovered Themes

The modeling run identified support themes including:

- Issue After Firmware Update
- App Issue Persists After Troubleshooting
- Account Access and Password Issues
- Data Loss and File Recovery
- Error Messages and Error Codes
- Unable to Perform Desired Action
- Wi-Fi Connectivity Issues
- Security and Data Safety Concerns
- Charging Problems
- Battery Life Issues
- Unstable Internet Connection
- Software Bugs and Data Loss
- Application Crashes and Software Bugs
- General Hardware Malfunction
- Software Freezing Issues
- Software Update Availability
- Screen and Display Problems
- Device Not Turning On
- Repair or Replacement Concerns
- Refund Issues
- Refund and Exchange Requests
- Invoice and Payment Issues
- Email and Account Issues

Some discovered labels remain broad or semantically mixed. These
should be treated as analytical themes rather than definitive issue
taxonomies.

### Topic ID Interpretation

`topic_id` is a model-generated categorical identifier.

It does not represent:

- Severity
- Priority
- Importance
- Numerical magnitude
- Ranking

For example, topic `8` is not inherently more important or severe
than topic `3`.

The human-readable `topic_label` provides the intended analytical
interpretation of the discovered cluster.

### Validation

Topic quality was evaluated through inspection of discovered topic
content and human interpretation of the resulting clusters.

The topic assignments were reviewed for semantic coherence and
near-duplicate themes were reduced before the final ticket-level
output was exported.

The final topic table was validated to ensure:

- One topic assignment per ticket
- 8,469 ticket assignments
- No missing topic labels
- Consistent ticket-level joins for downstream SQL integration

### Limitations

- Topic modeling is exploratory.
- Topic labels are human interpretations rather than ground truth.
- Some clusters remain semantically mixed.
- The `-1` outlier topic does not represent one coherent support issue.
- Topic IDs are dependent on the modeling run.
- Retraining the topic model with different data, preprocessing,
  embeddings, or parameters may produce different topic IDs and
  cluster structures.
- The current topic output should therefore be treated as the fixed
  analytical result of this modeling run.

### Intended Use

Topic outputs are intended for:

- Complaint-theme analysis
- Issue discovery
- Support workload analysis
- Emerging-theme monitoring
- Product and service issue investigation
- Dashboard segmentation

They are not intended to be treated as definitive ground-truth
support categories without further human validation.

## 3. Dissatisfaction-Risk Modeling

### Model Overview

The dissatisfaction-risk model estimates the model-derived risk that a
customer support ticket may be associated with customer
dissatisfaction.

The supervised target is:

```text
is_dissatisfied
```

The target is derived from observed Customer Satisfaction Rating
values:

```text
1 = Customer Satisfaction Rating <= 2
0 = Customer Satisfaction Rating >= 3
NULL = Customer Satisfaction Rating unavailable
```

The model is trained only on tickets where CSAT is observed.

After training, the fitted model is applied to the complete analytical
population to generate a dissatisfaction-risk score for every ticket.

This distinction is important:

- `is_dissatisfied` is an observed CSAT-derived outcome.
- `dissatisfaction_risk_score` is a model-generated prediction.

The two fields must not be treated as interchangeable.

### Model

- Model type: Gradient Boosting Classifier
- Classification threshold: 0.30
- Random state: 42
- CSAT-observed population: 2,769 tickets
- Model fitting set: 2,215 tickets
- Evaluation set: 554 tickets
- Split: Stratified 80/20

### Model Artifact

The fitted preprocessing and classification pipeline is saved as:

```text
models/dissatisfaction_risk_model.pkl
```

The selected classification threshold and related metadata are stored
separately in:

```text
models/dissatisfaction_risk_threshold.json
```

### Input Features

The model uses:

#### Categorical features

- Ticket Priority
- Ticket Channel
- `sentiment_label`
- `topic_id`

#### Numeric feature

- `sentiment_score`

Categorical features are one-hot encoded.

`topic_id` is treated as categorical because BERTopic topic identifiers
are model-generated labels rather than ordinal values.

### Target

The model predicts:

```text
is_dissatisfied
```

Class definitions:

```text
0 = Not dissatisfied
1 = Dissatisfied
```

The target is available only when Customer Satisfaction Rating is
observed.

The CSAT-observed population contains:

```text
2,769 tickets
```

The target distribution within this population is:

```text
Not dissatisfied: 1,667
Dissatisfied:     1,102
```

This corresponds to approximately:

```text
60.20% not dissatisfied
39.80% dissatisfied
```

### Training Population

Only tickets with observed CSAT contribute to supervised model
training.

The labeled population is split as:

```text
CSAT-observed population: 2,769
            |
            +---- Training: 2,215
            |
            +---- Evaluation: 554
```

The split is stratified and uses random state 42.

Tickets without observed CSAT are not assigned a fabricated target.

Their `is_dissatisfied` value remains missing.

### Inference Population

After the model was trained, the saved pipeline was used to generate:

```text
8,469 dissatisfaction-risk scores
```

for the complete analytical ticket population.

The inference process does not require observed CSAT because the model
uses:

- Ticket Priority
- Ticket Channel
- `sentiment_label`
- `topic_id`
- `sentiment_score`

This creates a deliberate separation between:

```text
Observed label population
2,769 tickets
        ↓
Model training and evaluation
        ↓
Saved model
        ↓
Full-population inference
8,469 tickets
```

Predictions for tickets without observed CSAT remain predictions. They
do not become observed dissatisfaction labels.

### Performance

Evaluation was performed using a stratified 80/20 train/test split of
the CSAT-observed population.

At the selected classification threshold of 0.30:

| Metric    | Dissatisfied Class |
| --------- | ------------------: |
| Precision |              0.3988 |
| Recall    |              0.9136 |
| F1-score  |              0.5552 |
| Accuracy  |              0.4188 |

The selected threshold emphasizes recall.

This means the model is designed to surface a large proportion of
potentially dissatisfied tickets for review, at the cost of
substantial false-positive volume.

The resulting model should therefore be interpreted as a
prioritization signal rather than a definitive classification of
customer dissatisfaction.

### Model Selection

Three predictive approaches were evaluated:

- Logistic Regression
- Gradient Boosting
- Logistic Regression with balanced class weights

Observed Average Precision:

| Model                         | Average Precision |
| ------------------------------ | -----------------: |
| Gradient Boosting              |              0.4169 |
| Logistic Regression            |              0.3995 |
| Balanced Logistic Regression   |              0.3988 |

Gradient Boosting achieved the highest observed Average Precision and
was selected as the final model.

Threshold evaluation was then performed for the Gradient Boosting
model.

A threshold of 0.30 produced the strongest observed dissatisfied-class
F1-score among the evaluated thresholds:

- Precision: 0.3988
- Recall: 0.9136
- F1-score: 0.5552

### Threshold Selection Caveat

The classification threshold was selected using the same test set used
for model evaluation.

Therefore, the threshold-specific performance should be considered
exploratory rather than an unbiased estimate of future production
performance.

An independent validation dataset or future-period holdout should be
used before production deployment.

### Feature Importance

Feature importance from the fitted Gradient Boosting model indicates
that:

```text
sentiment_score
```

is the dominant transformed feature, with an importance of
approximately:

```text
0.573
```

Other features, including ticket priority, ticket channel, and topic
assignments, have substantially smaller individual importance values.

Feature importance indicates relative contribution within the fitted
model.

It does not establish:

- Causality
- Business importance outside the fitted model
- That changing a feature will necessarily change customer
  dissatisfaction
- That one feature is independently responsible for an outcome

### Risk Score Interpretation

The generated field is:

```text
dissatisfaction_risk_score
```

Higher values indicate higher model-predicted dissatisfaction risk.

The score is intended for ranking and prioritization.

It should not be interpreted as:

- Observed customer dissatisfaction
- A confirmed complaint
- A causal measure
- A guaranteed probability of dissatisfaction
- A definitive customer classification

In particular, model calibration was not established as part of this
project. The score should therefore be treated as a model-derived risk
signal rather than a calibrated probability.

### Full-Population Risk Output

The generated risk output is stored in:

```text
data/processed/ticket_dissatisfaction_risk.csv
```

The output contains:

- Ticket ID
- `dissatisfaction_risk_score`

The generation process validates:

- Expected row count
- Unique Ticket IDs
- Missing risk scores
- Risk-score range

The final output contains a dissatisfaction-risk score for all 8,469
analytical tickets.

### Limitations

#### Training population

- The model is trained only on tickets with observed CSAT.
- Only 2,769 of 8,469 tickets have observed CSAT.
- The CSAT-observed population may not fully represent the complete
  ticket population.
- Missing CSAT may therefore introduce selection bias into the
  supervised modeling population.

#### Feature scope

- The available structured feature set provides limited separation
  between dissatisfied and non-dissatisfied tickets.
- The model uses a relatively small feature set.
- No reliable ticket-age or resolution-duration features were included
  because the source data does not support them defensibly.
- No explicit escalation target is used.

#### Sentiment dependency

- Sentiment features come from a pretrained general-domain sentiment
  model.
- The sentiment model has documented domain-mismatch limitations.
- Errors in sentiment inference can propagate into the
  dissatisfaction-risk model.

#### Topic dependency

- Topic assignments are exploratory.
- Topic IDs are model-generated categorical values.
- Topic instability across retraining may affect model inputs.

#### Threshold selection

- The threshold was selected using the same test set used for
  evaluation.
- Threshold-specific performance therefore requires independent
  validation.

#### Precision-recall trade-off

The selected threshold strongly favors recall:

```text
Recall:    0.9136
Precision: 0.3988
```

The model therefore generates a substantial number of false-positive
risk flags.

This is an intentional prioritization trade-off rather than evidence
that every flagged ticket is dissatisfied.

### Intended Use

The dissatisfaction-risk model is intended to support:

- Proactive ticket review
- Support-team prioritization
- Risk-based ticket triage
- Identification of groups with elevated predicted dissatisfaction
- Operational analysis of dissatisfaction-risk patterns
- Dashboard-based investigation of potentially at-risk tickets

The model is particularly suitable for a workflow where a support team
reviews a prioritized list and makes the final decision using the
underlying ticket context.

### Not Intended For

The model should not be used to:

- Automatically classify a customer as dissatisfied without human
  review
- Automatically reject or approve customer requests
- Automatically deny refunds
- Automatically change customer service treatment
- Make high-impact customer decisions
- Replace human support judgment
- Be deployed as a production decision system without independent
  validation

## 4. Relationship Between the Three AI Components

The three AI components form a connected analytical pipeline.

```text
Customer Support Ticket
          |
          v
   Cleaned Ticket Text
          |
    +-----+------+
    |            |
    v            v
Sentiment      Topics
    |            |
    +-----+------+
          |
          v
Dissatisfaction-Risk Model
          |
          v
dissatisfaction_risk_score
          |
          v
SQL / DuckDB Star Schema
          |
          v
Power BI AI Insights
```

The components have different roles:

| Component            | Role                   | Output                               | Interpretation                      |
| --------------------- | ----------------------- | ------------------------------------- | ------------------------------------ |
| Sentiment             | Text classification     | `sentiment_label`, `sentiment_score` | Model-derived sentiment signal      |
| Topic                 | Unsupervised discovery  | `topic_id`, `topic_label`            | Exploratory support theme           |
| Dissatisfaction Risk  | Supervised prediction   | `dissatisfaction_risk_score`         | Model-derived prioritization signal |

These outputs are integrated at ticket level and used together with
structured ticket metadata in the analytical layer.

## 5. Observed vs. Model-Derived Information

The project deliberately separates observed customer information from
AI-generated information.

### Observed

```text
Customer Satisfaction Rating
        ↓
is_dissatisfied
```

This represents an outcome observed through CSAT.

### Model-Derived

```text
Ticket Description
        ↓
Sentiment Model
        ↓
sentiment_label
sentiment_score

Ticket Description
        ↓
BERTopic
        ↓
topic_id
topic_label

Ticket Metadata
+
Sentiment
+
Topic
        ↓
Dissatisfaction-Risk Model
        ↓
dissatisfaction_risk_score
```

This distinction is maintained throughout the SQL layer and Power BI
dashboard.

The model-generated dissatisfaction-risk score must not be presented
as if it were observed CSAT-based dissatisfaction.

## 6. Scope Decision

The original project concept included an escalation-risk prediction
target.

During data profiling, the available fields were evaluated to
determine whether a defensible escalation label could be constructed.

The source data did not provide a reliable escalation indicator.

Rather than fabricate an escalation target, the supervised modeling
objective was changed to dissatisfaction risk using observed CSAT as
the target.

The revised target is:

```text
is_dissatisfied
```

with:

```text
1 = CSAT <= 2
0 = CSAT >= 3
NULL = CSAT unavailable
```

This is a data-driven modeling decision.

It preserves the original business objective of proactively identifying
support tickets that may require additional attention while ensuring
that the supervised target is grounded in an observable customer
outcome.

## 7. API Demo Note

The project also contains an optional local FastAPI demonstration.

The API returns:

- Sentiment
- Topic
- Dissatisfaction risk

The local API uses the project's sentiment approach, a persisted
topic-inference compatibility classifier, and the saved
dissatisfaction-risk model.

The API topic classifier is not the original BERTopic model. It is a
lightweight compatibility model trained from the validated BERTopic
topic assignments so that new ticket text can be assigned a topic in
the local demonstration.

The API-related artifact is:

```text
models/topic_inference_demo.pkl
```

The training script is:

```text
scripts/train_topic_inference_demo.py
```

The API implementation is:

```text
app/api.py
```

This component is provided for local demonstration and is not a
production deployment.

## 8. Overall AI Limitations

The three AI components should be interpreted together with the
limitations of the underlying dataset.

Key limitations include:

- Missing Customer Satisfaction Ratings for a large portion of
  tickets
- No defensible escalation label
- No reliable ticket creation timestamp
- Unreliable timestamp ordering for certain lifecycle calculations
- Templated ticket descriptions
- Placeholder text
- Scraped or unrelated text artifacts
- General-domain sentiment modeling
- Exploratory topic modeling
- Limited supervised training population
- Threshold selection on the evaluation set
- Lack of independent future-period validation

The project therefore demonstrates an end-to-end analytical AI
workflow rather than a production-ready predictive decision system.

## 9. Intended Overall Use

The AI layer is intended to enhance customer support analytics by
turning unstructured ticket text into structured analytical signals.

The intended workflow is:

```text
Support Tickets
      ↓
AI-derived signals
      ↓
SQL analytical layer
      ↓
Power BI reporting
      ↓
Prioritized human review
```

The practical objective is to help support teams answer:

- What are customers experiencing?
- What themes are appearing?
- What sentiment is being expressed?
- Which tickets may warrant additional attention?

Human review remains the final decision point for customer-impacting
actions.
