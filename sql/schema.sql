-- Drop existing star schema tables to allow a clean rebuild
DROP TABLE IF EXISTS fact_ticket;
DROP TABLE IF EXISTS dim_category;
DROP TABLE IF EXISTS dim_channel;
DROP TABLE IF EXISTS dim_priority;
DROP TABLE IF EXISTS dim_date;

-- Create ticket category dimension
CREATE TABLE dim_category (
    category_key INTEGER PRIMARY KEY,
    ticket_type VARCHAR NOT NULL UNIQUE
);

-- Create ticket channel dimension
CREATE TABLE dim_channel (
    channel_key INTEGER PRIMARY KEY,
    ticket_channel VARCHAR NOT NULL UNIQUE
);

-- Create ticket priority dimension
CREATE TABLE dim_priority (
    priority_key INTEGER PRIMARY KEY,
    ticket_priority VARCHAR NOT NULL UNIQUE
);

-- Create purchase date dimension
CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR NOT NULL
);

-- Create ticket fact table
CREATE TABLE fact_ticket (
    ticket_id BIGINT PRIMARY KEY,

    category_key INTEGER NOT NULL,
    channel_key INTEGER NOT NULL,
    priority_key INTEGER NOT NULL,
    purchase_date_key INTEGER NOT NULL,

    customer_age BIGINT,
    customer_gender VARCHAR,
    product_purchased VARCHAR,
    ticket_subject VARCHAR,
    cleaned_ticket_description VARCHAR,
    ticket_status VARCHAR,
    resolution VARCHAR,

    first_response_time TIMESTAMP,
    time_to_resolution TIMESTAMP,
    customer_satisfaction_rating DOUBLE,

    has_first_response BIGINT,
    is_resolved BIGINT,
    has_csat BIGINT,
    is_dissatisfied BIGINT,

    -- Reserved for AI-derived outputs populated in later pipeline stages
    sentiment_label VARCHAR,
    sentiment_score DOUBLE,
    topic_id INTEGER,
    topic_label VARCHAR,
    dissatisfaction_risk_score DOUBLE,

    FOREIGN KEY (category_key)
        REFERENCES dim_category(category_key),

    FOREIGN KEY (channel_key)
        REFERENCES dim_channel(channel_key),

    FOREIGN KEY (priority_key)
        REFERENCES dim_priority(priority_key),

    FOREIGN KEY (purchase_date_key)
        REFERENCES dim_date(date_key)
);