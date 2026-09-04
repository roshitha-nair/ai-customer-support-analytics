-- KPI aggregation queries for the customer support analytics star schema.
-- Date-based reporting uses Date of Purchase because no defensible ticket
-- creation timestamp is available.
-- SLA breach rate is not calculated because the available timestamps have
-- unreliable chronological ordering and no defensible SLA definition exists.

-- Resolution rate by day, category, and channel
SELECT
    dt.full_date AS reporting_date,
    cat.ticket_type,
    ch.ticket_channel,
    COUNT(*) AS total_tickets,
    SUM(ft.is_resolved) AS resolved_tickets,
    ROUND(
        100.0 * SUM(ft.is_resolved) / COUNT(*),
        2
    ) AS resolution_rate_pct
FROM fact_ticket AS ft
JOIN dim_date AS dt
    ON ft.purchase_date_key = dt.date_key
JOIN dim_category AS cat
    ON ft.category_key = cat.category_key
JOIN dim_channel AS ch
    ON ft.channel_key = ch.channel_key
GROUP BY
    dt.full_date,
    cat.ticket_type,
    ch.ticket_channel
ORDER BY
    reporting_date,
    ticket_type,
    ticket_channel;


-- Observed dissatisfaction rate by day, category, and channel.
-- Denominator includes only tickets with an observed CSAT value.
SELECT
    dt.full_date AS reporting_date,
    cat.ticket_type,
    ch.ticket_channel,
    COUNT(ft.is_dissatisfied) AS csat_observed_tickets,
    SUM(ft.is_dissatisfied) AS dissatisfied_tickets,
    ROUND(
        100.0
        * SUM(ft.is_dissatisfied)
        / NULLIF(COUNT(ft.is_dissatisfied), 0),
        2
    ) AS observed_dissatisfaction_rate_pct
FROM fact_ticket AS ft
JOIN dim_date AS dt
    ON ft.purchase_date_key = dt.date_key
JOIN dim_category AS cat
    ON ft.category_key = cat.category_key
JOIN dim_channel AS ch
    ON ft.channel_key = ch.channel_key
GROUP BY
    dt.full_date,
    cat.ticket_type,
    ch.ticket_channel
ORDER BY
    reporting_date,
    ticket_type,
    ticket_channel;


-- Predicted dissatisfaction rate by day, category, and channel.
-- This uses the model-derived risk score across the full ticket population.
SELECT
    dt.full_date AS reporting_date,
    cat.ticket_type,
    ch.ticket_channel,
    COUNT(*) AS total_tickets,
    ROUND(
        100.0
        * AVG(ft.dissatisfaction_risk_score),
        2
    ) AS predicted_dissatisfaction_rate_pct
FROM fact_ticket AS ft
JOIN dim_date AS dt
    ON ft.purchase_date_key = dt.date_key
JOIN dim_category AS cat
    ON ft.category_key = cat.category_key
JOIN dim_channel AS ch
    ON ft.channel_key = ch.channel_key
GROUP BY
    dt.full_date,
    cat.ticket_type,
    ch.ticket_channel
ORDER BY
    reporting_date,
    ticket_type,
    ticket_channel;


-- Sentiment distribution by day, category, and channel
SELECT
    dt.full_date AS reporting_date,
    cat.ticket_type,
    ch.ticket_channel,
    ft.sentiment_label,
    COUNT(*) AS ticket_count,
    ROUND(
        100.0 * COUNT(*)
        / SUM(COUNT(*)) OVER (
            PARTITION BY
                dt.full_date,
                cat.ticket_type,
                ch.ticket_channel
        ),
        2
    ) AS sentiment_distribution_pct
FROM fact_ticket AS ft
JOIN dim_date AS dt
    ON ft.purchase_date_key = dt.date_key
JOIN dim_category AS cat
    ON ft.category_key = cat.category_key
JOIN dim_channel AS ch
    ON ft.channel_key = ch.channel_key
GROUP BY
    dt.full_date,
    cat.ticket_type,
    ch.ticket_channel,
    ft.sentiment_label
ORDER BY
    reporting_date,
    ticket_type,
    ticket_channel,
    sentiment_label;


-- Emerging themes: topic volume trended week-over-week
SELECT
    DATE_TRUNC('week', dt.full_date) AS week_start,
    ft.topic_id,
    ft.topic_label,
    COUNT(*) AS ticket_count,
    LAG(COUNT(*)) OVER (
        PARTITION BY ft.topic_id
        ORDER BY DATE_TRUNC('week', dt.full_date)
    ) AS previous_week_ticket_count,
    COUNT(*) - LAG(COUNT(*)) OVER (
        PARTITION BY ft.topic_id
        ORDER BY DATE_TRUNC('week', dt.full_date)
    ) AS week_over_week_change
FROM fact_ticket AS ft
JOIN dim_date AS dt
    ON ft.purchase_date_key = dt.date_key
GROUP BY
    DATE_TRUNC('week', dt.full_date),
    ft.topic_id,
    ft.topic_label
ORDER BY
    week_start,
    ticket_count DESC;


-- Sentiment distribution by channel
SELECT
    ch.ticket_channel,
    ft.sentiment_label,
    COUNT(*) AS ticket_count,
    ROUND(
        100.0 * COUNT(*)
        / SUM(COUNT(*)) OVER (
            PARTITION BY ch.ticket_channel
        ),
        2
    ) AS channel_sentiment_pct
FROM fact_ticket AS ft
JOIN dim_channel AS ch
    ON ft.channel_key = ch.channel_key
GROUP BY
    ch.ticket_channel,
    ft.sentiment_label
ORDER BY
    ch.ticket_channel,
    ticket_count DESC;


-- Top 5 tickets by predicted dissatisfaction risk
SELECT
    ft.ticket_id,
    cat.ticket_type,
    ch.ticket_channel,
    pr.ticket_priority,
    ft.sentiment_label,
    ft.topic_label,
    ROUND(ft.dissatisfaction_risk_score, 6) AS dissatisfaction_risk_score
FROM fact_ticket AS ft
JOIN dim_category AS cat
    ON ft.category_key = cat.category_key
JOIN dim_channel AS ch
    ON ft.channel_key = ch.channel_key
JOIN dim_priority AS pr
    ON ft.priority_key = pr.priority_key
ORDER BY
    ft.dissatisfaction_risk_score DESC,
    ft.ticket_id
LIMIT 5;