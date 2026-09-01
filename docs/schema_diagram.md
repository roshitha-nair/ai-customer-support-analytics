# Customer Support Analytics Star Schema

```mermaid
erDiagram
    DIM_CATEGORY ||--o{ FACT_TICKET : categorizes
    DIM_CHANNEL ||--o{ FACT_TICKET : receives
    DIM_PRIORITY ||--o{ FACT_TICKET : prioritizes
    DIM_DATE ||--o{ FACT_TICKET : relates_to

    DIM_CATEGORY {
        INTEGER category_key PK
        VARCHAR ticket_type
    }

    DIM_CHANNEL {
        INTEGER channel_key PK
        VARCHAR ticket_channel
    }

    DIM_PRIORITY {
        INTEGER priority_key PK
        VARCHAR ticket_priority
    }

    DIM_DATE {
        INTEGER date_key PK
        DATE full_date
        INTEGER year
        INTEGER quarter
        INTEGER month
        VARCHAR month_name
    }

    FACT_TICKET {
        BIGINT ticket_id PK
        INTEGER category_key FK
        INTEGER channel_key FK
        INTEGER priority_key FK
        INTEGER purchase_date_key FK
        BIGINT customer_age
        VARCHAR customer_gender
        VARCHAR product_purchased
        VARCHAR ticket_subject
        VARCHAR cleaned_ticket_description
        VARCHAR ticket_status
        VARCHAR resolution
        TIMESTAMP first_response_time
        TIMESTAMP time_to_resolution
        DOUBLE customer_satisfaction_rating
        BIGINT has_first_response
        BIGINT is_resolved
        BIGINT has_csat
        BIGINT is_dissatisfied
        VARCHAR sentiment_label
        DOUBLE sentiment_score
        INTEGER topic_id
        VARCHAR topic_label
        DOUBLE escalation_risk_score
    }
```

## Design Note

`DIM_DATE` represents **Date of Purchase**. It is not treated as a ticket creation date because the dataset does not contain a defensible ticket creation timestamp.